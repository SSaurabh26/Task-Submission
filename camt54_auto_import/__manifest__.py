# -*- coding: utf-8 -*-
{
    'name': "CAMT54 Auto Import & Reconciliation",
    'summary': "Automatically import and reconcile CAMT54 banking statements from a defined folder",
    'description': """
        This module provides automatic import and reconciliation functionality for CAMT54 banking statements.
        
        Key Features:
        * Monitors a defined folder for CAMT54 files
        * Automatically imports banking statements
        * Performs automatic reconciliation
        * Configuration for folder monitoring
        * Processing logs and error handling
    """,
    'author': "Custom Development",
    'website': "https://www.example.com",
    'category': 'Accounting',
    'version': '17.0.1.0.1',
    'license': 'LGPL-3',
    
    # Dependencies
    'depends': [
        'base',
        'account',
        'account_accountant',
        'account_statement_import_camt',  # OCA dependency for CAMT parsing
    ],
    
    # Always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/camt54_config_views.xml',
        'views/camt54_import_log_views.xml',
        'views/camt54_manual_import_views.xml',
        'views/menu_views.xml',
    ],
    
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    
    # External dependencies
    'external_dependencies': {
        'python': ['watchdog'],
    },
}