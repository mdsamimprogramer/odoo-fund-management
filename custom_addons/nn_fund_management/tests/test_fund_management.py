# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestFundManagement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_user = cls.env.ref('nn_fund_management.group_fund_user')
        cls.group_finance = cls.env.ref('nn_fund_management.group_fund_finance_user')
        cls.group_gm = cls.env.ref('nn_fund_management.group_fund_gm_approver')
        cls.group_md = cls.env.ref('nn_fund_management.group_fund_md_approver')

        cls.fund_user = cls.env['res.users'].create({
            'name': 'Fund User',
            'login': 'fund.user@test.local',
            'email': 'fund.user@test.local',
            'groups_id': [(6, 0, [cls.group_user.id])],
        })
        cls.finance_user = cls.env['res.users'].create({
            'name': 'Finance User',
            'login': 'finance.user@test.local',
            'email': 'finance.user@test.local',
            'groups_id': [(6, 0, [cls.group_finance.id])],
        })
        cls.gm_user = cls.env['res.users'].create({
            'name': 'GM User',
            'login': 'gm.user@test.local',
            'email': 'gm.user@test.local',
            'groups_id': [(6, 0, [cls.group_gm.id])],
        })
        cls.md_user = cls.env['res.users'].create({
            'name': 'MD User',
            'login': 'md.user@test.local',
            'email': 'md.user@test.local',
            'groups_id': [(6, 0, [cls.group_md.id])],
        })

        cls.env.ref('nn_fund_management.approval_config_allocation').write({
            'gm_approver_ids': [(6, 0, [cls.gm_user.id])],
            'md_approver_ids': [(6, 0, [cls.md_user.id])],
        })
        cls.env.ref('nn_fund_management.approval_config_requisition').write({
            'gm_approver_ids': [(6, 0, [cls.gm_user.id])],
            'md_approver_ids': [(6, 0, [cls.md_user.id])],
        })
        cls.env.ref('nn_fund_management.approval_config_transfer').write({
            'gm_approver_ids': [(6, 0, [cls.gm_user.id])],
            'md_approver_ids': [(6, 0, [cls.md_user.id])],
        })

    def _create_funded_account(self, amount=1000.0):
        account = self.env['nn.fund.account'].create({
            'name': 'Test Bank',
            'code': self.env['ir.sequence'].next_by_code('nn.fund.incoming') or 'TB',
            'account_type': 'bank',
        })
        incoming = self.env['nn.fund.incoming'].with_user(self.finance_user).create({
            'account_id': account.id,
            'amount': amount,
            'reference': 'REF-%s' % account.id,
            'sender': 'Test Sender',
        })
        incoming.action_post()
        return account

    def _approve_allocation(self, amount=500.0, project=None):
        account = self._create_funded_account(amount * 2)
        project = project or self.env['nn.fund.project'].create({'name': 'Project A', 'code': 'PA-%s' % account.id})
        allocation = self.env['nn.fund.allocation'].with_user(self.fund_user).create({
            'account_id': account.id,
            'destination_type': 'project',
            'project_id': project.id,
            'amount': amount,
        })
        allocation.action_submit()
        allocation.action_send_to_gm()
        allocation.with_user(self.gm_user).action_gm_approve()
        allocation.with_user(self.md_user).action_md_approve()
        return allocation

    def test_allocation_workflow_and_double_spending_prevention(self):
        account = self._create_funded_account(1000.0)
        project = self.env['nn.fund.project'].create({'name': 'Project B', 'code': 'PB'})
        first = self.env['nn.fund.allocation'].with_user(self.fund_user).create({
            'account_id': account.id,
            'destination_type': 'project',
            'project_id': project.id,
            'amount': 800.0,
        })
        first.action_submit()
        self.assertEqual(first.status, 'submitted')
        self.assertEqual(account.held_balance, 800.0)

        second = self.env['nn.fund.allocation'].with_user(self.fund_user).create({
            'account_id': account.id,
            'destination_type': 'project',
            'project_id': project.id,
            'amount': 300.0,
        })
        with self.assertRaises(ValidationError):
            second.action_submit()

        first.action_send_to_gm()
        first.with_user(self.gm_user).action_gm_approve()
        first.with_user(self.md_user).action_md_approve()
        self.assertEqual(first.status, 'approved')
        self.assertEqual(account.assigned_balance, 800.0)

    def test_requisition_workflow_and_bill_limits(self):
        allocation = self._approve_allocation(1000.0)
        requisition = self.env['nn.fund.requisition'].with_user(self.fund_user).create({
            'target_type': 'project',
            'project_id': allocation.project_id.id,
            'amount': 600.0,
            'purpose': 'Laptop purchase',
        })
        requisition.action_submit()
        requisition.action_send_to_gm()
        requisition.with_user(self.gm_user).action_gm_approve()
        requisition.with_user(self.md_user).action_md_approve()
        self.assertEqual(requisition.status, 'approved')

        bill = self.env['nn.fund.bill'].with_user(self.finance_user).create({
            'requisition_id': requisition.id,
            'amount': 400.0,
            'vendor': 'Vendor A',
            'reference': 'BILL-1',
        })
        bill.action_post()
        self.assertEqual(requisition.remaining_billable_amount, 200.0)

        excessive = self.env['nn.fund.bill'].with_user(self.finance_user).create({
            'requisition_id': requisition.id,
            'amount': 250.0,
            'vendor': 'Vendor B',
            'reference': 'BILL-2',
        })
        with self.assertRaises(ValidationError):
            excessive.action_post()

        bill.action_reverse()
        self.assertEqual(requisition.remaining_billable_amount, 600.0)

    def test_transfer_workflow_and_over_transfer_prevention(self):
        source_allocation = self._approve_allocation(1000.0)
        destination = self.env['nn.fund.project'].create({'name': 'Project C', 'code': 'PC'})
        transfer = self.env['nn.fund.transfer'].with_user(self.finance_user).create({
            'source_type': 'project',
            'source_project_id': source_allocation.project_id.id,
            'destination_type': 'project',
            'destination_project_id': destination.id,
            'amount': 400.0,
            'reason': 'Budget movement',
        })
        transfer.action_submit()
        self.assertEqual(transfer.status, 'submitted')

        excessive = self.env['nn.fund.transfer'].with_user(self.finance_user).create({
            'source_type': 'project',
            'source_project_id': source_allocation.project_id.id,
            'destination_type': 'project',
            'destination_project_id': destination.id,
            'amount': 700.0,
            'reason': 'Too much',
        })
        with self.assertRaises(ValidationError):
            excessive.action_submit()

        transfer.action_send_to_gm()
        transfer.with_user(self.gm_user).action_gm_approve()
        transfer.with_user(self.md_user).action_md_approve()
        self.assertEqual(transfer.status, 'approved')
        self.assertEqual(destination.incoming_transfer_amount, 400.0)

    def test_no_self_approval_and_finance_permissions(self):
        account = self._create_funded_account(500.0)
        project = self.env['nn.fund.project'].create({'name': 'Project D', 'code': 'PD'})
        allocation = self.env['nn.fund.allocation'].with_user(self.gm_user).create({
            'account_id': account.id,
            'destination_type': 'project',
            'project_id': project.id,
            'amount': 200.0,
        })
        allocation.action_submit()
        allocation.action_send_to_gm()
        with self.assertRaises(ValidationError):
            allocation.with_user(self.gm_user).action_gm_approve()

        incoming = self.env['nn.fund.incoming'].with_user(self.fund_user).create({
            'account_id': account.id,
            'amount': 100.0,
            'reference': 'NO-FINANCE',
            'sender': 'Unauthorized',
        })
        with self.assertRaises(AccessError):
            incoming.action_post()
