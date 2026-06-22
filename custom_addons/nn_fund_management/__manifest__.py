# -*- coding: utf-8 -*-
{
    'name': 'NN Fund Management',
    'version': '18.0.1.0.0',
    'category': 'Finance',
    'author': 'NN Development Team',
    'website': 'https://www.nnservicesengineering.com',
    'license': 'LGPL-3',
    'summary': 'Production fund management, approval, requisition, bill and transfer workflows',
    'description': '''
        Complete fund management module for Odoo 18 Community Edition.

        Features:
        - Bank and cash fund accounts
        - Incoming funds with duplicate transaction prevention
        - Allocation, requisition and transfer workflows
        - Reusable GM/MD approval engine
        - Project and expense head computed balances
        - Partial bill management with reversal support
        - Audit history, chatter, activities, dashboard and PDF reports
    ''',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        'security/fund_groups.xml',
        'security/ir.model.access.csv',
        'security/fund_record_rules.xml',
        'data/fund_sequences.xml',
        'data/fund_expense_heads.xml',
        'data/fund_approval_config.xml',
        'data/fund_dashboard.xml',
        'views/fund_account_views.xml',
        'views/fund_incoming_views.xml',
        'views/fund_project_views.xml',
        'views/fund_expense_head_views.xml',
        'views/fund_allocation_views.xml',
        'views/fund_requisition_views.xml',
        'views/fund_bill_views.xml',
        'views/fund_transfer_views.xml',
        'views/fund_approval_views.xml',
        'views/fund_dashboard_views.xml',
        'views/fund_menu.xml',
        'report/fund_report_templates.xml',
        'report/fund_reports.xml',
    ],
    'demo': [
        'demo/fund_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
