# NN Fund Management Module for Odoo 18

## Overview

This is a production-quality Odoo 18 custom module for comprehensive fund request management. The module provides complete workflow support from request creation through approval/rejection.

## Features

### 1. Fund Request Model

- **Request Number**: Auto-generated sequence (Format: FR/YYYY/MM/00001)
- **Employee Name**: Selection from company employees
- **Request Date**: Date when the request was submitted
- **Amount**: Fund amount with validation (must be > 0)
- **Purpose**: Detailed description of fund usage
- **Status**: Workflow states (Draft, Submitted, Approved, Rejected)
- **Notes**: Additional comments and information

### 2. Workflow

The module implements a complete state machine workflow:

```
Draft → Submitted → Approved/Rejected
```

**State Transitions:**

- **Submit**: Draft → Submitted (Any user with Fund User role)
- **Approve**: Submitted → Approved (Fund Manager only)
- **Reject**: Submitted → Rejected (Fund Manager only)
- **Reset**: Rejected → Draft (Fund Manager only, for re-submission)

### 3. Business Logic

- **Amount Validation**: Ensures amount is always greater than 0
- **Status Management**: Prevents invalid state transitions
- **Audit Trail**: Tracks creation and modification by user
- **Activity Logging**: Records all state changes in chatter
- **Deletion Protection**: Prevents deletion of approved/rejected requests

### 4. User Interface

- **Tree View**: List view with color-coded status indicators
- **Form View**: Comprehensive form with workflow buttons
- **Search View**: Advanced search with filters and grouping options
- **Status Bar**: Visual workflow indicator

### 5. Security

- **Fund User Group**: Can create and submit requests
- **Fund Manager Group**: Can approve/reject and manage all requests
- **Record-level Access**: Defined in ir_model_access.csv

### 6. Reports

- **PDF Report**: Professional PDF generation for fund requests
- **Dynamic Naming**: Report names include request number
- **Comprehensive Details**: Includes all request information and audit trail

## Folder Structure

```
nn_fund_management/
├── __init__.py                          # Package initializer
├── __manifest__.py                      # Module manifest
├── models/
│   ├── __init__.py                      # Models package initializer
│   └── fund_request.py                  # Fund Request model with business logic
├── views/
│   ├── fund_request_views.xml           # Tree, Form, Search views
│   └── fund_request_menu.xml            # Menu items and action window
├── security/
│   ├── fund_groups.xml                  # User groups definition
│   └── ir_model_access.csv              # Access rights configuration
├── data/
│   ├── fund_request_sequence.xml        # Sequence configuration
│   └── fund_request_demo.xml            # Demo data
├── reports/
│   ├── fund_request_report.xml          # Report action definition
│   └── fund_request_report_template.xml # PDF report template
└── static/
    └── description/
        └── icon.png                     # Module icon (if available)
```

## File Descriptions

### Core Files

#### `__manifest__.py`

Module configuration file containing:

- Module metadata (name, version, author)
- Dependencies
- Data files load order
- Demo data specification

#### `__init__.py`

Python package initializer that imports the models package.

### Models

#### `models/__init__.py`

Package initializer that imports the fund_request model.

#### `models/fund_request.py`

Main model file containing:

- **Model Definition**: fund.request with inheritance from mail.thread
- **Fields**: All request fields with proper documentation
- **Constraints**: Amount validation
- **Methods**: Workflow actions (submit, approve, reject, reset)
- **Lifecycle Hooks**: create(), write(), unlink()
- **Utility Methods**: name_get(), action_print_report()

### Views

#### `views/fund_request_views.xml`

Contains three view definitions:

- **Tree View**: List view with status decorations
- **Form View**: Detailed form with buttons and notebook tabs
- **Search View**: Search and filter options

#### `views/fund_request_menu.xml`

Menu structure:

- Fund Management (Main menu)
  - Fund Requests (Submenu with action)

### Security

#### `security/fund_groups.xml`

User group definitions:

- **Fund User**: Basic user with read/write/create permissions
- **Fund Manager**: Manager with all permissions including delete

#### `security/ir_model_access.csv`

Access rights matrix defining read, write, create, and delete permissions for each group.

### Data

#### `data/fund_request_sequence.xml`

Sequence configuration for auto-generating request numbers:

- Format: FR/YYYY/MM/00001 (customizable)
- Padding: 5 digits

#### `data/fund_request_demo.xml`

Demo data including:

- Sample employees (John Doe, Jane Smith)
- Demo fund requests in various states
- Used for testing and demonstration

### Reports

#### `reports/fund_request_report.xml`

Report action definition linking to the template.

#### `reports/fund_request_report_template.xml`

QWeb PDF template with:

- Request details section
- Employee information
- Financial details
- Purpose and notes
- Audit trail
- Professional formatting

## Installation

1. **Copy module to Odoo addons directory:**

   ```bash
   cp -r nn_fund_management /path/to/odoo/addons/
   ```

2. **Update module list in Odoo:**
   - Go to Apps → Update Apps List

3. **Install the module:**
   - Search for "NN Fund Management"
   - Click Install

## Usage

### Creating a Fund Request

1. Navigate to Fund Management → Fund Requests
2. Click Create
3. Fill in employee, amount, and purpose
4. Click Submit

### Approving/Rejecting Requests

1. Go to Fund Management → Fund Requests
2. Open a submitted request
3. Click Approve or Reject (Manager only)

### Generating Reports

1. Open a fund request
2. Click "Print Report"
3. Save or print the PDF

### Filtering and Searching

1. Use the search bar to find requests
2. Apply filters (Status, Date, Employee)
3. Group by Status, Employee, or Date

## Best Practices Implemented

✅ **Code Quality**

- Comprehensive docstrings for all methods
- Inline comments for complex logic
- Proper error handling and validation
- PEP 8 compliant Python code

✅ **Odoo Conventions**

- Proper model inheritance (mail.thread)
- Standard field naming conventions
- Correct view architecture
- Proper group and security definitions

✅ **Database Design**

- Optimized field definitions
- Proper constraints and validation
- Audit trail implementation
- Foreign key relationships

✅ **User Experience**

- Intuitive workflow buttons
- Color-coded status indicators
- Helpful tooltips and placeholders
- Responsive design

✅ **Security**

- Role-based access control
- Record-level permissions
- Audit trail tracking
- Data protection constraints

## API Reference

### Fund Request Model Methods

#### `action_submit()`

Submit a draft fund request for review.

#### `action_approve()`

Approve a submitted fund request (Manager only).

#### `action_reject()`

Reject a submitted fund request (Manager only).

#### `action_reset_to_draft()`

Reset a rejected request to draft status for re-submission.

#### `action_print_report()`

Generate and return PDF report for the request.

## Customization

### Adding New Fields

1. Add field definition in `models/fund_request.py`
2. Update form view in `views/fund_request_views.xml`
3. Update tree view if needed

### Modifying Workflow

1. Edit status selection in the model
2. Update state machine logic in workflow methods
3. Modify status bar in form view

### Changing Report Format

Edit `reports/fund_request_report_template.xml` to customize PDF layout.

## Support

For issues or questions about this module, please contact the development team or refer to the Odoo 18 documentation.

---

**Module Version:** 18.0.1.0.0  
**Author:** NN Development Team  
**License:** LGPL-3
