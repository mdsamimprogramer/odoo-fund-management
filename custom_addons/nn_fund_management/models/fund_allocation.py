# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


class FundAllocation(models.Model):
    _name = 'nn.fund.allocation'
    _description = 'Fund Allocation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'nn.fund.approval.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    account_id = fields.Many2one('nn.fund.account', required=True, tracking=True)
    destination_type = fields.Selection([('project', 'Project'), ('expense_head', 'Expense Head')], required=True, default='project')
    project_id = fields.Many2one('nn.fund.project', tracking=True)
    expense_head_id = fields.Many2one('nn.fund.expense.head', tracking=True)
    amount = fields.Monetary(required=True, currency_field='currency_id', tracking=True)
    date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    requested_by_id = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True)
    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('gm_approval', 'GM Approval'),
            ('md_approval', 'MD Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    comments = fields.Text()

    _sql_constraints = [
        ('amount_positive', 'check(amount > 0)', 'Allocation amount must be greater than zero.'),
    ]

    @api.constrains('destination_type', 'project_id', 'expense_head_id')
    def _check_destination(self):
        for record in self:
            if record.destination_type == 'project' and not record.project_id:
                raise ValidationError(_('Project is required for project allocation.'))
            if record.destination_type == 'expense_head' and not record.expense_head_id:
                raise ValidationError(_('Expense head is required for expense head allocation.'))
            if record.project_id and record.expense_head_id:
                raise ValidationError(_('Choose either project or expense head, not both.'))

    def _ensure_user(self):
        if not (
            self.env.user.has_group('nn_fund_management.group_fund_user')
            or self.env.user.has_group('nn_fund_management.group_fund_finance_user')
            or self.env.user.has_group('nn_fund_management.group_fund_administrator')
        ):
            raise AccessError(_('You cannot manage fund allocations.'))

    def _check_available(self, include_own_hold=False):
        for record in self:
            available = record.account_id.available_balance
            if include_own_hold and record.status in ('submitted', 'gm_approval', 'md_approval'):
                available += record.amount
            if record.amount > available:
                raise ValidationError(_('Insufficient available balance in the source account.'))

    def action_submit(self):
        self._ensure_user()
        for record in self:
            if record.status != 'draft':
                raise ValidationError(_('Only draft allocations can be submitted.'))
            record._check_available()
            if record.name == 'New':
                record.name = self.env['ir.sequence'].next_by_code('nn.fund.allocation') or 'New'
            record._write_status('submitted', _('Submitted'), record.comments)

    def action_send_to_gm(self):
        self._ensure_user()
        for record in self:
            if record.status != 'submitted':
                raise ValidationError(_('Only submitted allocations can be sent for GM approval.'))
            config = record._approval_config()
            record._write_status('gm_approval', _('Sent to GM'), record.comments)
            record._schedule_approval_activities(config.gm_approver_ids, _('New allocation approval request'), record.name)

    def action_gm_approve(self):
        for record in self:
            if record.status != 'gm_approval':
                raise ValidationError(_('Only allocations waiting for GM approval can be approved.'))
            record._check_gm_approver()
            config = record._approval_config()
            record._write_status('md_approval', _('GM Approved'))
            record._schedule_approval_activities(config.md_approver_ids, _('New allocation MD approval request'), record.name)

    def action_md_approve(self):
        for record in self:
            if record.status != 'md_approval':
                raise ValidationError(_('Only allocations waiting for MD approval can be approved.'))
            record._check_md_approver()
            record._check_available(include_own_hold=True)
            record._write_status('approved', _('MD Approved'))
            record._notify_request_owner(_('Allocation approved'), record.name)

    def action_reject(self):
        for record in self:
            if record.status not in ('gm_approval', 'md_approval'):
                raise ValidationError(_('Only allocations in approval can be rejected.'))
            record._write_status('rejected', _('Rejected'), record.comments)
            record._notify_request_owner(_('Allocation rejected'), record.name)

    def action_cancel(self):
        self._ensure_user()
        for record in self:
            if record.status not in ('draft', 'submitted', 'gm_approval', 'md_approval'):
                raise ValidationError(_('Only draft or pending allocations can be cancelled.'))
            record._write_status('cancelled', _('Cancelled'), record.comments)

    def action_print_report(self):
        return self.env.ref('nn_fund_management.action_report_fund_allocation').report_action(self)
