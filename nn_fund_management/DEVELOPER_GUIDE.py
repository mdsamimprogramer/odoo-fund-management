"""
NN Fund Management Module - Complete Documentation
Odoo 18 Custom Module

This file serves as technical documentation for developers.
"""

# ============================================================================
# MODULE OVERVIEW
# ============================================================================
"""
Module Name: NN Fund Management (nn_fund_management)
Version: 18.0.1.0.0
Category: Finance
Purpose: Comprehensive fund request management with workflow automation

Key Components:
1. Fund Request Model - Core data model
2. Workflow Engine - State machine implementation
3. Views - UI components (Tree, Form, Search)
4. Security - Role-based access control
5. Reports - PDF generation
6. Sequences - Auto-numbering
"""

# ============================================================================
# QUICK START FOR DEVELOPERS
# ============================================================================
"""
To modify or extend this module:

1. Model Changes:
   - Edit models/fund_request.py
   - Add/remove fields, methods, or constraints
   - Run module update in Odoo

2. View Changes:
   - Edit XML files in views/ directory
   - Modify form, tree, or search views
   - Refresh browser to see changes

3. Security Changes:
   - Edit security/fund_groups.xml for groups
   - Edit security/ir_model_access.csv for permissions
   - Run module update in Odoo

4. Report Changes:
   - Edit reports/fund_request_report_template.xml
   - Modify PDF layout and content
   - Test report generation

5. Data/Demo Changes:
   - Edit data/ XML files
   - Add/remove demo records
   - Run module update in Odoo
"""

# ============================================================================
# DATABASE SCHEMA
# ============================================================================
"""
Table: fund_request

Columns:
- id: INTEGER PRIMARY KEY (Auto-increment)
- request_number: VARCHAR (Auto-generated: FR/YYYY/MM/00001)
- employee_id: MANY2ONE (res.partner)
- employee_name: VARCHAR (Computed from employee_id)
- request_date: DATE
- amount: NUMERIC(10,2) - Must be > 0
- purpose: TEXT
- status: VARCHAR (draft|submitted|approved|rejected)
- notes: TEXT
- created_by: MANY2ONE (res.users)
- last_modified_by: MANY2ONE (res.users)
- create_date: DATETIME (Auto)
- write_date: DATETIME (Auto)
- message_ids: ONE2MANY (mail.message) - Chatter
- activity_ids: ONE2MANY (mail.activity) - Activities

Indexes:
- request_number (Unique)
- status (For filtering)
- employee_id (For filtering)
- request_date (For sorting)
"""

# ============================================================================
# WORKFLOW STATE MACHINE
# ============================================================================
"""
States:
- draft: Initial state, editable
- submitted: Submitted for review, awaiting manager action
- approved: Approved by manager, final state
- rejected: Rejected by manager, can be reset to draft

Transitions:
1. draft → submitted (action_submit)
   - Triggered by: Any Fund User
   - Validation: Status must be 'draft'

2. submitted → approved (action_approve)
   - Triggered by: Fund Manager only
   - Validation: Status must be 'submitted'

3. submitted → rejected (action_reject)
   - Triggered by: Fund Manager only
   - Validation: Status must be 'submitted'

4. rejected → draft (action_reset_to_draft)
   - Triggered by: Fund Manager only
   - Validation: Status must be 'rejected'

Constraints:
- Cannot delete approved/rejected records
- Amount must always be > 0
- Employee is required
- Purpose and amount are required
"""

# ============================================================================
# SECURITY MODEL
# ============================================================================
"""
Groups:
1. Fund User (group_fund_user)
   - Permissions: Read, Write, Create
   - Cannot Delete
   - Can Submit requests
   - Cannot Approve/Reject

2. Fund Manager (group_fund_manager)
   - Permissions: Read, Write, Create, Delete
   - Implies: Fund User permissions
   - Can Submit, Approve, Reject, Reset requests
   - Can Delete records

Record-level Rules:
- None (uses group-based access control)

Field-level Restrictions:
- request_number: Readonly for users
- created_by: Readonly for users
- last_modified_by: Readonly for users
- employee_name: Computed, readonly
"""

# ============================================================================
# API METHODS
# ============================================================================
"""
Public Methods:

1. action_submit()
   - Description: Submit draft request for review
   - Parameters: self
   - Returns: Activity log action
   - Raises: ValidationError if status != 'draft'

2. action_approve()
   - Description: Approve submitted request
   - Parameters: self
   - Returns: Activity log action
   - Raises: ValidationError if status != 'submitted'
   - Permission: Fund Manager only

3. action_reject()
   - Description: Reject submitted request
   - Parameters: self
   - Returns: Activity log action
   - Raises: ValidationError if status != 'submitted'
   - Permission: Fund Manager only

4. action_reset_to_draft()
   - Description: Reset rejected request to draft
   - Parameters: self
   - Returns: Activity log action
   - Permission: Fund Manager only

5. action_print_report()
   - Description: Generate and return PDF report
   - Parameters: self
   - Returns: Report action

6. _compute_employee_name()
   - Description: Compute employee name from employee_id
   - Type: Computed field
   - Auto-trigger: When employee_id changes

7. name_get()
   - Description: Return display name with request number
   - Returns: List of tuples (id, display_name)

8. create()
   - Description: Override to set created_by
   - Parameters: vals_list
   - Returns: Created records

9. write()
   - Description: Override to set last_modified_by
   - Parameters: vals
   - Returns: Boolean

10. unlink()
    - Description: Override to protect approved/rejected records
    - Raises: ValidationError if record is approved/rejected
"""

# ============================================================================
# VIEWS REFERENCE
# ============================================================================
"""
1. Tree View (view_fund_request_tree)
   - Displays: Request list with key fields
   - Columns: Request #, Employee, Date, Amount, Status
   - Features: Color decorations, column sums
   - Filters: None (use search view)

2. Form View (view_fund_request_form)
   - Sections: 
     * Header (Status bar, action buttons)
     * Request Information (Employee, Date)
     * Financial Details (Amount)
     * Notebook Pages:
       - Details (Purpose)
       - Additional Information (Notes, Audit)
   - Chatter: Messages, Activities, Followers

3. Search View (view_fund_request_search)
   - Search Fields: Request #, Employee, Amount, Purpose
   - Filters: Draft, Submitted, Approved, Rejected
   - Group By: Status, Employee, Date
"""

# ============================================================================
# SEQUENCE CONFIGURATION
# ============================================================================
"""
Sequence ID: seq_fund_request
Code: fund.request
Format: FR/%(year)s/%(month)s/%(seq)s
Padding: 5 digits
Example: FR/2024/06/00001, FR/2024/06/00002, etc.

Customization:
- Edit data/fund_request_sequence.xml
- Change prefix format as needed
- Examples:
  * FRM/%(year)s/%(seq)s (FRM/2024/00001)
  * FUND-%(seq)s (FUND-00001)
  * %(year)s/%(month)s/%(day)s/%(seq)s (2024/06/20/00001)
"""

# ============================================================================
# REPORT REFERENCE
# ============================================================================
"""
Report ID: action_report_fund_request
Template: report_fund_request_template
Format: QWeb PDF
Output Filename: Fund Request - {request_number}

Report Sections:
1. Header - Title and divider
2. Request Details - Request number, date, status
3. Employee Information - Name, email, phone
4. Financial Details - Amount
5. Purpose - Detailed fund usage description
6. Additional Notes - Optional notes
7. Audit Trail - Created/Modified by information
8. Footer - Disclaimer

Customization:
- Edit reports/fund_request_report_template.xml
- Modify layout, colors, or sections
- Add logos or images
- Change fonts or styling
"""

# ============================================================================
# DEMO DATA REFERENCE
# ============================================================================
"""
Demo Employees:
- partner_john_doe: Test employee
- partner_jane_smith: Test employee

Demo Fund Requests:
1. fund_request_draft: John Doe, 5000.00, Draft status
2. fund_request_submitted: Jane Smith, 10000.00, Submitted status
3. fund_request_approved: John Doe, 3500.00, Approved status

Load Demo Data:
1. Install module with demo data
2. Go to Fund Requests
3. Demo records will appear
"""

# ============================================================================
# EXTENSION POINTS
# ============================================================================
"""
Developers can extend this module by:

1. Adding new fields to fund_request model
2. Creating child models (related documents)
3. Adding new workflows/states
4. Creating additional reports
5. Adding email templates for notifications
6. Integrating with other modules
7. Adding custom compute fields
8. Creating server actions
9. Adding scheduled actions
10. Creating custom security rules

Example Extensions:
- Add budget allocation tracking
- Integrate with project management
- Add approval hierarchy levels
- Create budget vs. actual reports
- Add notification emails
- Track fund disbursement
- Add fund category classification
"""

# ============================================================================
# TESTING CHECKLIST
# ============================================================================
"""
Functionality Tests:
☐ Create fund request in draft status
☐ Submit request to submitted status
☐ Approve request to approved status
☐ Reject request to rejected status
☐ Reset rejected request to draft
☐ Validate amount > 0 constraint
☐ Test employee selection
☐ Verify sequence auto-generation
☐ Generate PDF report
☐ Test search and filters

Permission Tests:
☐ Fund User can create requests
☐ Fund User can submit requests
☐ Fund User cannot approve requests
☐ Fund Manager can approve requests
☐ Fund Manager can reject requests
☐ Cannot delete approved/rejected records
☐ Non-members cannot access module

UI Tests:
☐ Tree view displays correctly
☐ Form view displays all sections
☐ Workflow buttons appear/disappear correctly
☐ Search filters work
☐ Status colors display correctly
☐ Chatter functionality works

Database Tests:
☐ Records persist after module update
☐ Constraints are enforced
☐ Sequences continue incrementing
☐ Audit trail is recorded
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================
"""
Common Issues:

1. Module not appearing after installation
   - Check manifest.py for syntax errors
   - Verify all XML files are well-formed
   - Check module dependencies

2. Reports not generating
   - Check if report template is valid
   - Verify report action is linked correctly
   - Check for missing fields in template

3. Workflow buttons not appearing
   - Verify user group assignments
   - Check view state conditions
   - Verify status field values

4. Access denied errors
   - Verify user group permissions
   - Check ir_model_access.csv
   - Verify security rules

5. Sequence not generating
   - Verify sequence XML is loaded
   - Check sequence code matches model
   - Verify data file is in manifest
"""

# ============================================================================
# DEPLOYMENT CHECKLIST
# ============================================================================
"""
Before deploying to production:

☐ Remove all demo data
☐ Change sequence format if needed
☐ Configure user groups and permissions
☐ Test all workflows in production environment
☐ Verify email/notification settings
☐ Backup database
☐ Document any customizations
☐ Train end users
☐ Monitor for errors after deployment
☐ Create backup plan for rollback
"""

# ============================================================================
# TECHNICAL SPECIFICATIONS
# ============================================================================
"""
Technology Stack:
- Framework: Odoo 18
- Language: Python 3.9+
- Database: PostgreSQL 12+
- Frontend: XML/QWeb, JavaScript
- Reporting: QWeb PDF

Dependencies:
- base: Core Odoo module
- sale: Sales module (for extensions)
- mail: Email and chatter functionality

Performance Considerations:
- Indexes on frequently searched fields
- Computed fields for display optimization
- Efficient queries for large datasets
- Proper pagination for list views

Security Considerations:
- Input validation on all fields
- SQL injection prevention (ORM usage)
- XSS prevention (template escaping)
- CSRF protection (Odoo built-in)
- Role-based access control
"""

# ============================================================================
# CONTACT & SUPPORT
# ============================================================================
"""
Module: NN Fund Management
Version: 18.0.1.0.0
Author: NN Development Team
License: LGPL-3
Category: Finance

For support or questions:
- Review README.md for overview
- Check inline code comments
- Refer to Odoo 18 documentation
- Contact development team

Last Updated: 2024-06-20
"""
