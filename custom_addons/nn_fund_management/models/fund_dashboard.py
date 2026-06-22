# -*- coding: utf-8 -*-

from odoo import api, fields, models


class FundDashboard(models.Model):
    _name = 'nn.fund.dashboard'
    _description = 'Fund Management Dashboard'

    name = fields.Char(default='Fund Dashboard', required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True)
    total_received = fields.Monetary(compute='_compute_dashboard', currency_field='currency_id')
    unassigned_balance = fields.Monetary(compute='_compute_dashboard', currency_field='currency_id')
    held_balance = fields.Monetary(compute='_compute_dashboard', currency_field='currency_id')
    assigned_balance = fields.Monetary(compute='_compute_dashboard', currency_field='currency_id')
    spent_balance = fields.Monetary(compute='_compute_dashboard', currency_field='currency_id')
    pending_approval_count = fields.Integer(compute='_compute_dashboard')
    project_ids = fields.Many2many('nn.fund.project', compute='_compute_dashboard')
    expense_head_ids = fields.Many2many('nn.fund.expense.head', compute='_compute_dashboard')

    @api.depends_context('company')
    def _compute_dashboard(self):
        for record in self:
            accounts = self.env['nn.fund.account'].search([('company_id', '=', record.company_id.id)])
            projects = self.env['nn.fund.project'].search([('company_id', '=', record.company_id.id)])
            heads = self.env['nn.fund.expense.head'].search([('company_id', '=', record.company_id.id)])
            pending_domain = [('status', 'in', ('submitted', 'gm_approval', 'md_approval')), ('company_id', '=', record.company_id.id)]
            record.total_received = sum(accounts.mapped('total_received'))
            record.unassigned_balance = sum(accounts.mapped('available_balance'))
            record.held_balance = sum(accounts.mapped('held_balance')) + sum(projects.mapped('hold_amount')) + sum(heads.mapped('hold_amount'))
            record.assigned_balance = sum(accounts.mapped('assigned_balance'))
            record.spent_balance = sum(projects.mapped('spent_amount')) + sum(heads.mapped('spent_amount'))
            record.pending_approval_count = (
                self.env['nn.fund.allocation'].search_count(pending_domain)
                + self.env['nn.fund.requisition'].search_count(pending_domain)
                + self.env['nn.fund.transfer'].search_count(pending_domain)
            )
            record.project_ids = projects
            record.expense_head_ids = heads
