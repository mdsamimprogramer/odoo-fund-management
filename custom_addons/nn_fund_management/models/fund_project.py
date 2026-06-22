# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FundProject(models.Model):
    _name = 'nn.fund.project'
    _description = 'Fund Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True)
    active = fields.Boolean(default=True)
    allocation_ids = fields.One2many('nn.fund.allocation', 'project_id')
    source_transfer_ids = fields.One2many('nn.fund.transfer', 'source_project_id')
    destination_transfer_ids = fields.One2many('nn.fund.transfer', 'destination_project_id')
    requisition_ids = fields.One2many('nn.fund.requisition', 'project_id')
    allocated_amount = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    available_amount = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    hold_amount = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    spent_amount = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    incoming_transfer_amount = fields.Monetary(compute='_compute_balances', currency_field='currency_id')
    outgoing_transfer_amount = fields.Monetary(compute='_compute_balances', currency_field='currency_id')

    _sql_constraints = [
        ('code_company_unique', 'unique(code, company_id)', 'Project code must be unique per company.'),
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
        for project in self:
            allocated = sum(project.allocation_ids.filtered(lambda a: a.status == 'approved').mapped('amount'))
            incoming = sum(project.destination_transfer_ids.filtered(lambda t: t.status == 'approved').mapped('amount'))
            outgoing = sum(project.source_transfer_ids.filtered(lambda t: t.status in ('submitted', 'gm_approval', 'md_approval', 'approved')).mapped('amount'))
            hold = sum(project.requisition_ids.filtered(lambda r: r.status in ('submitted', 'gm_approval', 'md_approval')).mapped('amount'))
            posted_requisitions = project.requisition_ids.filtered(lambda r: r.status in ('approved', 'closed'))
            spent = sum(posted_requisitions.mapped('posted_bill_amount'))
            reserved = sum((r.amount - r.posted_bill_amount) for r in posted_requisitions if r.status == 'approved')
            project.allocated_amount = allocated
            project.incoming_transfer_amount = incoming
            project.outgoing_transfer_amount = outgoing
            project.hold_amount = hold
            project.spent_amount = spent
            project.available_amount = allocated + incoming - outgoing - hold - reserved - spent
