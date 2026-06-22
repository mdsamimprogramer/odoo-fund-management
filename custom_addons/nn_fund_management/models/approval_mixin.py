# -*- coding: utf-8 -*-

from odoo import _, api, models
from odoo.exceptions import AccessError, UserError, ValidationError


class FundApprovalMixin(models.AbstractModel):
    _name = 'nn.fund.approval.mixin'
    _description = 'Reusable Fund Approval Engine'

    def _approval_amount(self):
        self.ensure_one()
        return getattr(self, 'amount', 0.0)

    def _approval_reference(self):
        self.ensure_one()
        return getattr(self, 'name', False) or self.display_name

    def _request_owner(self):
        self.ensure_one()
        return getattr(self, 'requested_by_id', False) or self.create_uid

    def _approval_config(self):
        self.ensure_one()
        config = self.env['nn.fund.approval.config'].search([
            ('target_model', '=', self._name),
            ('active', '=', True),
        ], limit=1)
        if not config:
            raise UserError(_('No approval configuration found for %s.') % self._description)
        return config

    def _check_group(self, xmlid):
        if not self.env.user.has_group(xmlid):
            raise AccessError(_('You do not have permission to perform this action.'))

    def _check_gm_approver(self):
        self._check_group('nn_fund_management.group_fund_gm_approver')
        config = self._approval_config()
        if config.gm_approver_ids and self.env.user not in config.gm_approver_ids:
            raise AccessError(_('You are not configured as a GM approver for this workflow.'))
        self._check_no_self_approval()

    def _check_md_approver(self):
        self._check_group('nn_fund_management.group_fund_md_approver')
        config = self._approval_config()
        if config.md_approver_ids and self.env.user not in config.md_approver_ids:
            raise AccessError(_('You are not configured as an MD approver for this workflow.'))
        self._check_no_self_approval()

    def _check_no_self_approval(self):
        self.ensure_one()
        owner = self._request_owner()
        if owner and owner == self.env.user:
            raise ValidationError(_('Self approval is not allowed.'))

    def _write_status(self, new_status, action, comments=False):
        for record in self:
            previous_status = record.status
            record.with_context(nn_fund_status_transition=True).write({'status': new_status})
            record._create_history(previous_status, new_status, action, comments)
            record.message_post(
                body=_('<b>%s</b><br/>Status changed from %s to %s.') % (
                    action,
                    previous_status,
                    new_status,
                )
            )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('nn_fund_management.group_fund_administrator'):
            for vals in vals_list:
                if vals.get('status') and vals['status'] != 'draft':
                    raise AccessError(_('Workflow records must be created in Draft status.'))
        return super().create(vals_list)

    def write(self, vals):
        if 'status' in vals and not self.env.context.get('nn_fund_status_transition'):
            raise AccessError(_('Use workflow buttons to change status.'))
        return super().write(vals)

    def _create_history(self, previous_status, new_status, action, comments=False):
        self.ensure_one()
        self.env['nn.fund.approval.history'].sudo().create({
            'model': self._name,
            'res_id': self.id,
            'reference': self._approval_reference(),
            'user_id': self.env.user.id,
            'previous_status': previous_status,
            'new_status': new_status,
            'action': action,
            'amount': self._approval_amount(),
            'currency_id': self.currency_id.id,
            'comments': comments,
        })

    def _activity_type_todo(self):
        return self.env.ref('mail.mail_activity_data_todo')

    def _schedule_approval_activities(self, users, summary, note):
        activity_type = self._activity_type_todo()
        for record in self:
            for user in users:
                record.activity_schedule(
                    activity_type_id=activity_type.id,
                    user_id=user.id,
                    summary=summary,
                    note=note,
                )

    def _notify_request_owner(self, summary, note):
        activity_type = self._activity_type_todo()
        for record in self:
            owner = record._request_owner()
            if owner:
                record.activity_schedule(
                    activity_type_id=activity_type.id,
                    user_id=owner.id,
                    summary=summary,
                    note=note,
                )
