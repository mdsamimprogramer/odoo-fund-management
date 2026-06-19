# -*- coding: utf-8 -*-
"""
Fund Request Model
Handles fund request management with workflow and validation
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class FundRequest(models.Model):
    """
    Model for managing fund requests with complete workflow support.
    
    Workflow: Draft → Submitted → Approved/Rejected
    """
    
    _name = 'fund.request'
    _description = 'Fund Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc, id desc'
    
    # ==================== Fields ====================
    
    request_number = fields.Char(
        string='Request Number',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code('fund.request')
    )
    
    employee_id = fields.Many2one(
        comodel_name='res.partner',
        string='Employee Name',
        required=True,
        tracking=True,
        help='Select the employee requesting the fund'
    )
    
    employee_name = fields.Char(
        string='Employee Name (Display)',
        compute='_compute_employee_name',
        store=True,
        help='Automatic display of employee name'
    )
    
    request_date = fields.Date(
        string='Request Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        help='Date when the request was submitted'
    )
    
    amount = fields.Float(
        string='Amount',
        required=True,
        tracking=True,
        help='Amount of fund requested (must be greater than 0)'
    )
    
    purpose = fields.Text(
        string='Purpose',
        required=True,
        tracking=True,
        help='Detailed description of fund usage'
    )
    
    status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Status',
        required=True,
        default='draft',
        tracking=True,
        help='Current status of the fund request'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes or comments about the request'
    )
    
    created_by = fields.Many2one(
        comodel_name='res.users',
        string='Created By',
        readonly=True,
        default=lambda self: self.env.user
    )
    
    last_modified_by = fields.Many2one(
        comodel_name='res.users',
        string='Last Modified By',
        readonly=True
    )
    
    # ==================== Computed Fields ====================
    
    @api.depends('employee_id')
    def _compute_employee_name(self):
        """Compute employee name from employee_id"""
        for record in self:
            record.employee_name = record.employee_id.name if record.employee_id else ''
    
    # ==================== Constraints ====================
    
    @api.constrains('amount')
    def _check_amount_positive(self):
        """
        Validate that amount is greater than 0
        
        Raises:
            ValidationError: If amount is not positive
        """
        for record in self:
            if record.amount <= 0:
                raise ValidationError(
                    'Fund Request Amount must be greater than 0. '
                    f'You entered: {record.amount}'
                )
    
    # ==================== Business Logic ====================
    
    def action_submit(self):
        """
        Submit the fund request.
        Transition: Draft → Submitted
        """
        for record in self:
            if record.status != 'draft':
                raise ValidationError(
                    f'Only draft requests can be submitted. '
                    f'Current status: {record.status}'
                )
            record.write({
                'status': 'submitted',
                'last_modified_by': self.env.user.id,
            })
        
        return self._log_activity('Submitted', 'Fund request submitted for review')
    
    def action_approve(self):
        """
        Approve the fund request.
        Transition: Submitted → Approved
        """
        for record in self:
            if record.status != 'submitted':
                raise ValidationError(
                    f'Only submitted requests can be approved. '
                    f'Current status: {record.status}'
                )
            record.write({
                'status': 'approved',
                'last_modified_by': self.env.user.id,
            })
        
        return self._log_activity('Approved', 'Fund request approved')
    
    def action_reject(self):
        """
        Reject the fund request.
        Transition: Submitted → Rejected
        """
        for record in self:
            if record.status != 'submitted':
                raise ValidationError(
                    f'Only submitted requests can be rejected. '
                    f'Current status: {record.status}'
                )
            record.write({
                'status': 'rejected',
                'last_modified_by': self.env.user.id,
            })
        
        return self._log_activity('Rejected', 'Fund request rejected')
    
    def action_reset_to_draft(self):
        """
        Reset the fund request back to draft status.
        Useful for re-submission after rejection.
        """
        for record in self:
            record.write({
                'status': 'draft',
                'last_modified_by': self.env.user.id,
            })
        
        return self._log_activity('Reset', 'Fund request reset to draft')
    
    def _log_activity(self, activity_type, message):
        """
        Log activity in chatter
        
        Args:
            activity_type: Type of activity (str)
            message: Activity message (str)
        """
        for record in self:
            record.message_post(
                body=f'<strong>{activity_type}:</strong> {message}',
                message_type='notification'
            )
    
    # ==================== Model Lifecycle ====================
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to set created_by field
        
        Args:
            vals_list: List of values for creation
            
        Returns:
            Created records
        """
        for vals in vals_list:
            vals['created_by'] = self.env.user.id
        
        return super().create(vals_list)
    
    def write(self, vals):
        """
        Override write to update last_modified_by field
        
        Args:
            vals: Dictionary of values to update
            
        Returns:
            Boolean success indicator
        """
        vals['last_modified_by'] = self.env.user.id
        return super().write(vals)
    
    def unlink(self):
        """
        Override unlink to prevent deletion of approved/rejected requests
        
        Raises:
            ValidationError: If trying to delete approved or rejected request
        """
        for record in self:
            if record.status in ('approved', 'rejected'):
                raise ValidationError(
                    f'Cannot delete {record.status} fund requests. '
                    f'Request Number: {record.request_number}'
                )
        
        return super().unlink()
    
    # ==================== Search & Display Methods ====================
    
    def name_get(self):
        """
        Override name_get to display request number with employee name
        
        Returns:
            List of tuples (id, display_name)
        """
        result = []
        for record in self:
            name = f'{record.request_number} - {record.employee_name or "Unknown"}'
            result.append((record.id, name))
        return result
    
    # ==================== Action Buttons ====================
    
    def action_print_report(self):
        """
        Generate and print PDF report for fund request
        
        Returns:
            Action for report generation
        """
        return self.env.ref('nn_fund_management.action_report_fund_request').report_action(self)
