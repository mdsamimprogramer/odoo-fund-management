# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


class FundTransfer(models.Model):
    _name = 'nn.fund.transfer'
    _description = 'Fund Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'nn.fund.approval.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    source_type = fields.Selection([('project', 'Project'), ('expense_head', 'Expense Head')], required=True, default='project')
    destination_type = fields.Selection([('project', 'Project'), ('expense_head', 'Expense Head')], required=True, default='project')
    source_project_id = fields.Many2one('nn.fund.project', tracking=True)
    source_expense_head_id = fields.Many2one('nn.fund.expense.head', tracking=True)
    destination_project_id = fields.Many2one('nn.fund.project', tracking=True)
    destination_expense_head_id = fields.Many2one('nn.fund.expense.head', tracking=True)
    amount = fields.Monetary(required=True, currency_field='currency_id', tracking=True)
    date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    reason = fields.Text(required=True, tracking=True)
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
        ('amount_positive', 'check(amount > 0)', 'Transfer amount must be greater than zero.'),
    ]

    @api.constrains(
        'source_type',
        'destination_type',
        'source_project_id',
        'source_expense_head_id',
        'destination_project_id',
        'destination_expense_head_id',
    )
    def _check_endpoints(self):
        for record in self:
            if record.source_type == 'project' and not record.source_project_id:
                raise ValidationError(_('Source project is required.'))
            if record.source_type == 'expense_head' and not record.source_expense_head_id:
                raise ValidationError(_('Source expense head is required.'))
            if record.destination_type == 'project' and not record.destination_project_id:
                raise ValidationError(_('Destination project is required.'))
            if record.destination_type == 'expense_head' and not record.destination_expense_head_id:
                raise ValidationError(_('Destination expense head is required.'))
            if record._source_key() == record._destination_key():
                raise ValidationError(_('Source and destination cannot be the same.'))

    def _source_key(self):
        self.ensure_one()
        if self.source_type == 'project':
            return ('project', self.source_project_id.id)
        return ('expense_head', self.source_expense_head_id.id)

    def _destination_key(self):
        self.ensure_one()
        if self.destination_type == 'project':
            return ('project', self.destination_project_id.id)
        return ('expense_head', self.destination_expense_head_id.id)

    def _source_available(self):
        self.ensure_one()
        return self.source_project_id.available_amount if self.source_type == 'project' else self.source_expense_head_id.available_amount

    def _check_available(self, include_own_hold=False):
        for record in self:
            available = record._source_available()
            if include_own_hold and record.status in ('submitted', 'gm_approval', 'md_approval'):
                available += record.amount
            if record.amount > available:
                raise ValidationError(_('Transfer amount exceeds source available balance.'))

    def _ensure_user(self):
        if not (
            self.env.user.has_group('nn_fund_management.group_fund_finance_user')
            or self.env.user.has_group('nn_fund_management.group_fund_administrator')
        ):
            raise AccessError(_('Only Finance Users can manage fund transfers.'))

    def action_submit(self):
        self._ensure_user()
        for record in self:
            if record.status != 'draft':
                raise ValidationError(_('Only draft transfers can be submitted.'))
            record._check_available()
            if record.name == 'New':
                record.name = self.env['ir.sequence'].next_by_code('nn.fund.transfer') or 'New'
            record._write_status('submitted', _('Submitted'), record.comments)

    def action_send_to_gm(self):
        self._ensure_user()
        for record in self:
            if record.status != 'submitted':
                raise ValidationError(_('Only submitted transfers can be sent for GM approval.'))
            config = record._approval_config()
            record._write_status('gm_approval', _('Sent to GM'), record.comments)
            record._schedule_approval_activities(config.gm_approver_ids, _('New transfer approval request'), record.name)

    def action_gm_approve(self):
        for record in self:
            if record.status != 'gm_approval':
                raise ValidationError(_('Only transfers waiting for GM approval can be approved.'))
            record._check_gm_approver()
            config = record._approval_config()
            record._write_status('md_approval', _('GM Approved'))
            record._schedule_approval_activities(config.md_approver_ids, _('New transfer MD approval request'), record.name)

    def action_md_approve(self):
        for record in self:
            if record.status != 'md_approval':
                raise ValidationError(_('Only transfers waiting for MD approval can be approved.'))
            record._check_md_approver()
            record._check_available(include_own_hold=True)
            record._write_status('approved', _('MD Approved'))
            record._notify_request_owner(_('Transfer approved'), record.name)

    def action_reject(self):
        for record in self:
            if record.status not in ('gm_approval', 'md_approval'):
                raise ValidationError(_('Only transfers in approval can be rejected.'))
            record._write_status('rejected', _('Rejected'), record.comments)
            record._notify_request_owner(_('Transfer rejected'), record.name)

    def action_cancel(self):
        self._ensure_user()
        for record in self:
            if record.status not in ('draft', 'submitted', 'gm_approval', 'md_approval'):
                raise ValidationError(_('Only draft or pending transfers can be cancelled.'))
            record._write_status('cancelled', _('Cancelled'), record.comments)

    def action_print_report(self):
        return self.env.ref('nn_fund_management.action_report_fund_transfer').report_action(self)
