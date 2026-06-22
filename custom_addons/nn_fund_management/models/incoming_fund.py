# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


class IncomingFund(models.Model):
    _name = 'nn.fund.incoming'
    _description = 'Incoming Fund'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    account_id = fields.Many2one('nn.fund.account', required=True, tracking=True)
    amount = fields.Monetary(required=True, currency_field='currency_id', tracking=True)
    date = fields.Date(required=True, default=fields.Date.context_today, tracking=True)
    reference = fields.Char(required=True, tracking=True)
    sender = fields.Char(required=True, tracking=True)
    attachment = fields.Binary(attachment=True)
    attachment_filename = fields.Char()
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True)
    status = fields.Selection(
        [('draft', 'Draft'), ('posted', 'Posted'), ('cancelled', 'Cancelled')],
        default='draft',
        required=True,
        tracking=True,
    )

    _sql_constraints = [
        ('reference_account_unique', 'unique(reference, account_id)', 'Transaction reference must be unique per account.'),
        ('amount_positive', 'check(amount > 0)', 'Incoming amount must be greater than zero.'),
    ]

    def _ensure_finance(self):
        if not (
            self.env.user.has_group('nn_fund_management.group_fund_finance_user')
            or self.env.user.has_group('nn_fund_management.group_fund_administrator')
        ):
            raise AccessError(_('Only Finance Users can post incoming funds.'))

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('nn_fund_management.group_fund_administrator'):
            for vals in vals_list:
                if vals.get('status') and vals['status'] != 'draft':
                    raise AccessError(_('Incoming funds must be created in Draft status.'))
        return super().create(vals_list)

    def write(self, vals):
        if 'status' in vals and not self.env.context.get('nn_fund_status_transition'):
            raise AccessError(_('Use posting buttons to change incoming fund status.'))
        return super().write(vals)

    def action_post(self):
        self._ensure_finance()
        for record in self:
            if record.status != 'draft':
                raise ValidationError(_('Only draft incoming funds can be posted.'))
            if record.name == 'New':
                record.name = self.env['ir.sequence'].next_by_code('nn.fund.incoming') or 'New'
            record.with_context(nn_fund_status_transition=True).status = 'posted'
            record.message_post(body=_('Incoming fund posted.'))

    def action_cancel(self):
        self._ensure_finance()
        for record in self:
            if record.status != 'draft':
                raise ValidationError(_('Only draft incoming funds can be cancelled.'))
            record.with_context(nn_fund_status_transition=True).status = 'cancelled'
            record.message_post(body=_('Incoming fund cancelled.'))
