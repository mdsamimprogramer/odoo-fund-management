# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


class FundBill(models.Model):
    _name = 'nn.fund.bill'
    _description = 'Fund Bill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    requisition_id = fields.Many2one('nn.fund.requisition', required=True, tracking=True)
    amount = fields.Monetary(required=True, currency_field='currency_id', tracking=True)
    date = fields.Date(default=fields.Date.context_today, required=True, tracking=True)
    vendor = fields.Char(required=True, tracking=True)
    reference = fields.Char(required=True, tracking=True)
    attachment = fields.Binary(attachment=True)
    attachment_filename = fields.Char()
    company_id = fields.Many2one(related='requisition_id.company_id', store=True)
    currency_id = fields.Many2one(related='requisition_id.currency_id', store=True)
    status = fields.Selection(
        [('draft', 'Draft'), ('posted', 'Posted'), ('reversed', 'Reversed'), ('cancelled', 'Cancelled')],
        default='draft',
        required=True,
        tracking=True,
    )

    _sql_constraints = [
        ('amount_positive', 'check(amount > 0)', 'Bill amount must be greater than zero.'),
    ]

    @api.constrains('requisition_id', 'amount', 'status')
    def _check_bill_limit(self):
        for record in self:
            if record.requisition_id.status not in ('approved', 'closed'):
                raise ValidationError(_('Bills can only be created for approved requisitions.'))
            posted_total = sum(record.requisition_id.bill_ids.filtered(lambda b: b.status == 'posted').mapped('amount'))
            if posted_total > record.requisition_id.amount:
                raise ValidationError(_('Posted bills cannot exceed the approved requisition amount.'))

    def _ensure_finance(self):
        if not (
            self.env.user.has_group('nn_fund_management.group_fund_finance_user')
            or self.env.user.has_group('nn_fund_management.group_fund_administrator')
        ):
            raise AccessError(_('Only Finance Users can post or reverse bills.'))

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('nn_fund_management.group_fund_administrator'):
            for vals in vals_list:
                if vals.get('status') and vals['status'] != 'draft':
                    raise AccessError(_('Bills must be created in Draft status.'))
        return super().create(vals_list)

    def write(self, vals):
        if 'status' in vals and not self.env.context.get('nn_fund_status_transition'):
            raise AccessError(_('Use bill workflow buttons to change status.'))
        return super().write(vals)

    def action_post(self):
        self._ensure_finance()
        for record in self:
            if record.status != 'draft':
                raise ValidationError(_('Only draft bills can be posted.'))
            if record.requisition_id.status != 'approved':
                raise ValidationError(_('Only approved open requisitions can be billed.'))
            if record.amount > record.requisition_id.remaining_billable_amount:
                raise ValidationError(_('Bill amount exceeds remaining billable amount.'))
            if record.name == 'New':
                record.name = self.env['ir.sequence'].next_by_code('nn.fund.bill') or 'New'
            record.with_context(nn_fund_status_transition=True).status = 'posted'
            record.message_post(body=_('Bill posted.'))
            if record.requisition_id.remaining_billable_amount <= 0:
                record.requisition_id.activity_schedule(
                    activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                    user_id=record.requisition_id.requested_by_id.id,
                    summary=_('Requisition exhausted'),
                    note=record.requisition_id.name,
                )
            elif record.requisition_id.remaining_billable_amount <= (record.requisition_id.amount * 0.1):
                record.requisition_id.activity_schedule(
                    activity_type_id=self.env.ref('mail.mail_activity_data_todo').id,
                    user_id=record.requisition_id.requested_by_id.id,
                    summary=_('Requisition almost exhausted'),
                    note=record.requisition_id.name,
                )

    def action_reverse(self):
        self._ensure_finance()
        for record in self:
            if record.status != 'posted':
                raise ValidationError(_('Only posted bills can be reversed.'))
            record.with_context(nn_fund_status_transition=True).status = 'reversed'
            record.message_post(body=_('Bill reversed.'))

    def action_cancel(self):
        self._ensure_finance()
        for record in self:
            if record.status != 'draft':
                raise ValidationError(_('Only draft bills can be cancelled.'))
            record.with_context(nn_fund_status_transition=True).status = 'cancelled'
