# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FundAccount(models.Model):
    _name = 'nn.fund.account'
    _description = 'Fund Bank or Cash Account'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    account_type = fields.Selection(
        [('bank', 'Bank'), ('cash', 'Cash')],
        required=True,
        default='bank',
        tracking=True,
    )
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True)
    active = fields.Boolean(default=True)
    incoming_fund_ids = fields.One2many('nn.fund.incoming', 'account_id')
    allocation_ids = fields.One2many('nn.fund.allocation', 'account_id')
    total_received = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    held_balance = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    assigned_balance = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    available_balance = fields.Monetary(compute='_compute_balances', currency_field='currency_id')

    _sql_constraints = [
        ('code_company_unique', 'unique(code, company_id)', 'Account code must be unique per company.'),
    ]

    @api.depends('incoming_fund_ids.status', 'incoming_fund_ids.amount', 'allocation_ids.status', 'allocation_ids.amount')
    def _compute_balances(self):
        for account in self:
            received = sum(account.incoming_fund_ids.filtered(lambda f: f.status == 'posted').mapped('amount'))
            held = sum(account.allocation_ids.filtered(lambda a: a.status in ('submitted', 'gm_approval', 'md_approval')).mapped('amount'))
            assigned = sum(account.allocation_ids.filtered(lambda a: a.status == 'approved').mapped('amount'))
            account.total_received = received
            account.held_balance = held
            account.assigned_balance = assigned
            account.available_balance = received - held - assigned
