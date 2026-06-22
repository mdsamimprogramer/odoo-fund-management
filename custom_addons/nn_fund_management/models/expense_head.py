# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FundExpenseHead(models.Model):
    _name = 'nn.fund.expense.head'
    _description = 'Fund Expense Head'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True)
    active = fields.Boolean(default=True)
    allocation_ids = fields.One2many('nn.fund.allocation', 'expense_head_id')
    source_transfer_ids = fields.One2many('nn.fund.transfer', 'source_expense_head_id')
    destination_transfer_ids = fields.One2many('nn.fund.transfer', 'destination_expense_head_id')
    requisition_ids = fields.One2many('nn.fund.requisition', 'expense_head_id')
    allocated_amount = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    available_amount = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    hold_amount = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    spent_amount = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    incoming_transfer_amount = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    outgoing_transfer_amount = fields.Monetary(compute='_compute_balances', currency_field='currency_id')

    _sql_constraints = [
        ('code_company_unique', 'unique(code, company_id)', 'Expense head code must be unique per company.'),
    ]

    @api.depends(
        'allocation_ids.status',
        'allocation_ids.amount',
        'source_transfer_ids.status',
        'source_transfer_ids.amount',
        'destination_transfer_ids.status',
        'destination_transfer_ids.amount',
        'requisition_ids.status',
        'requisition_ids.amount',
        'requisition_ids.bill_ids.status',
        'requisition_ids.bill_ids.amount',
    )
    def _compute_balances(self):
        for head in self:
            allocated = sum(head.allocation_ids.filtered(lambda a: a.status == 'approved').mapped('amount'))
            incoming = sum(head.destination_transfer_ids.filtered(lambda t: t.status == 'approved').mapped('amount'))
            outgoing = sum(head.source_transfer_ids.filtered(lambda t: t.status in ('submitted', 'gm_approval', 'md_approval', 'approved')).mapped('amount'))
            hold = sum(head.requisition_ids.filtered(lambda r: r.status in ('submitted', 'gm_approval', 'md_approval')).mapped('amount'))
            posted_requisitions = head.requisition_ids.filtered(lambda r: r.status in ('approved', 'closed'))
            spent = sum(posted_requisitions.mapped('posted_bill_amount'))
            reserved = sum((r.amount - r.posted_bill_amount) for r in posted_requisitions if r.status == 'approved')
            head.allocated_amount = allocated
            head.incoming_transfer_amount = incoming
            head.outgoing_transfer_amount = outgoing
            head.hold_amount = hold
            head.spent_amount = spent
            head.available_amount = allocated + incoming - outgoing - hold - reserved - spent
