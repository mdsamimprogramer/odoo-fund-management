# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


class FundRequisition(models.Model):
    _name = 'nn.fund.requisition'
    _description = 'Fund Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'nn.fund.approval.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    target_type = fields.Selection([('project', 'Project'), ('expense_head', 'Expense Head')], required=True, default='project')
    project_id = fields.Many2one('nn.fund.project', tracking=True)
    expense_head_id = fields.Many2one('nn.fund.expense.head', tracking=True)
    amount = fields.Monetary(required=True, currency_field='currency_id', tracking=True)
    date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    purpose = fields.Text(required=True, tracking=True)
    requested_by_id = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True)
    bill_ids = fields.One2many('nn.fund.bill', 'requisition_id')
    posted_bill_amount = fields.Monetary(compute='_compute_bill_amounts', currency_field='currency_id')
    remaining_billable_amount = fields.Monetary(compute='_compute_bill_amounts', currency_field='currency_id')
    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('gm_approval', 'GM Approval'),
            ('md_approval', 'MD Approval'),
            ('approved', 'Approved'),
            ('closed', 'Closed'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    comments = fields.Text()

    _sql_constraints = [
        ('amount_positive', 'check(amount > 0)', 'Requisition amount must be greater than zero.'),
    ]

    @api.depends('bill_ids.status', 'bill_ids.amount', 'amount')
    def _compute_bill_amounts(self):
        for record in self:
            posted = sum(record.bill_ids.filtered(lambda b: b.status == 'posted').mapped('amount'))
            record.posted_bill_amount = posted
            record.remaining_billable_amount = record.amount - posted

    @api.constrains('target_type', 'project_id', 'expense_head_id')
    def _check_target(self):
        for record in self:
            if record.target_type == 'project' and not record.project_id:
                raise ValidationError(_('Project is required for project requisition.'))
            if record.target_type == 'expense_head' and not record.expense_head_id:
                raise ValidationError(_('Expense head is required for expense head requisition.'))
            if record.project_id and record.expense_head_id:
                raise ValidationError(_('Choose either project or expense head, not both.'))

    def _available_source_balance(self):
        self.ensure_one()
        return self.project_id.available_amount if self.target_type == 'project' else self.expense_head_id.available_amount

    def _check_available(self, include_own_hold=False):
        for record in self:
            available = record._available_source_balance()
            if include_own_hold and record.status in ('submitted', 'gm_approval', 'md_approval'):
                available += record.amount
            if record.amount > available:
                raise ValidationError(_('Insufficient available balance for this requisition.'))

    def _ensure_user(self):
        if not (
            self.env.user.has_group('nn_fund_management.group_fund_user')
            or self.env.user.has_group('nn_fund_management.group_fund_finance_user')
            or self.env.user.has_group('nn_fund_management.group_fund_administrator')
        ):
            raise AccessError(_('You cannot manage fund requisitions.'))

    def action_submit(self):
        self._ensure_user()
        for record in self:
            if record.status != 'draft':
                raise ValidationError(_('Only draft requisitions can be submitted.'))
            record._check_available()
            if record.name == 'New':
                record.name = self.env['ir.sequence'].next_by_code('nn.fund.requisition') or 'New'
            record._write_status('submitted', _('Submitted'), record.comments)

    def action_send_to_gm(self):
        self._ensure_user()
        for record in self:
            if record.status != 'submitted':
                raise ValidationError(_('Only submitted requisitions can be sent for GM approval.'))
            config = record._approval_config()
            record._write_status('gm_approval', _('Sent to GM'), record.comments)
            record._schedule_approval_activities(config.gm_approver_ids, _('New requisition approval request'), record.name)

    def action_gm_approve(self):
        for record in self:
            if record.status != 'gm_approval':
                raise ValidationError(_('Only requisitions waiting for GM approval can be approved.'))
            record._check_gm_approver()
            config = record._approval_config()
            record._write_status('md_approval', _('GM Approved'))
            record._schedule_approval_activities(config.md_approver_ids, _('New requisition MD approval request'), record.name)

    def action_md_approve(self):
        for record in self:
            if record.status != 'md_approval':
                raise ValidationError(_('Only requisitions waiting for MD approval can be approved.'))
            record._check_md_approver()
            record._check_available(include_own_hold=True)
            record._write_status('approved', _('MD Approved'))
            record._notify_request_owner(_('Requisition approved'), record.name)

    def action_close(self):
        self._ensure_user()
        for record in self:
            if record.status != 'approved':
                raise ValidationError(_('Only approved requisitions can be closed.'))
            record._write_status('closed', _('Closed'))

    def action_reject(self):
        for record in self:
            if record.status not in ('gm_approval', 'md_approval'):
                raise ValidationError(_('Only requisitions in approval can be rejected.'))
            record._write_status('rejected', _('Rejected'), record.comments)
            record._notify_request_owner(_('Requisition rejected'), record.name)

    def action_cancel(self):
        self._ensure_user()
        for record in self:
            if record.status not in ('draft', 'submitted', 'gm_approval', 'md_approval'):
                raise ValidationError(_('Only draft or pending requisitions can be cancelled.'))
            record._write_status('cancelled', _('Cancelled'), record.comments)

    def action_print_report(self):
        return self.env.ref('nn_fund_management.action_report_fund_requisition').report_action(self)
