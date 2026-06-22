# -*- coding: utf-8 -*-

from odoo import fields, models


class ApprovalCommentWizard(models.TransientModel):
    _name = 'nn.fund.approval.comment.wizard'
    _description = 'Approval Comment Wizard'

    comments = fields.Text(required=True)
