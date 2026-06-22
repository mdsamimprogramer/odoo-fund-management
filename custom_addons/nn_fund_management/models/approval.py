# -*- coding: utf-8 -*-

from odoo import fields, models


class FundApprovalConfig(models.Model):
    _name = 'nn.fund.approval.config'
    _description = 'Fund Approval Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(required=True, tracking=True)
    target_model = fields.Selection(
        selection=[
            ('nn.fund.allocation', 'Fund Allocation'),
            ('nn.fund.requisition', 'Fund Requisition'),
            ('nn.fund.transfer', 'Fund Transfer'),
        ],
        required=True,
        tracking=True,
    )
    gm_approver_ids = fields.Many2many(
        'res.users',
        'nn_fund_approval_config_gm_rel',
        'config_id',
        'user_id',
        string='GM Approvers',
        tracking=True,
    )
    md_approver_ids = fields.Many2many(
        'res.users',
        'nn_fund_approval_config_md_rel',
        'config_id',
        'user_id',
        string='MD Approvers',
        tracking=True,
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            'target_model_unique',
            'unique(target_model)',
            'Only one approval configuration is allowed per workflow model.',
        ),
    ]


class FundApprovalHistory(models.Model):
    _name = 'nn.fund.approval.history'
    _description = 'Fund Approval and Audit History'
    _order = 'date desc, id desc'
    _rec_name = 'display_name'

    display_name = fields.Char(compute='_compute_display_name')
    model = fields.Char(required=True, index=True)
    res_id = fields.Integer(required=True, index=True)
    reference = fields.Char(required=True, index=True)
    user_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user)
    previous_status = fields.Char()
    new_status = fields.Char(required=True)
    action = fields.Char(required=True)
    amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.company.currency_id)
    comments = fields.Text()
    date = fields.Datetime(default=fields.Datetime.now, required=True)

    def _compute_display_name(self):
        for record in self:
            record.display_name = '%s - %s' % (record.reference, record.action)
