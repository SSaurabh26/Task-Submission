# -*- coding: utf-8 -*-
"""
CAMT54 Import Log Model

This module tracks all CAMT54 file processing activities, providing a complete
audit trail of what files were processed, when, and with what results.

The import log is essential for:
- Monitoring system performance
- Troubleshooting failed imports
- Compliance and auditing
- Understanding processing patterns

Author: Custom Development Team
License: LGPL-3
"""

import os
from odoo import models, fields, api


class Camt54ImportLog(models.Model):
    """
    CAMT54 Import Log Model
    
    This model maintains a detailed log of every CAMT54 file processing attempt,
    including both successful and failed imports. Each log entry contains:
    
    - File identification (name, path, size)
    - Processing status and timing
    - Results (statements created, transactions imported/reconciled)
    - Error details for troubleshooting
    - Links to created bank statements
    
    The log is ordered by creation date (newest first) and uses filename
    as the display name for easy identification.
    """
    _name = 'camt54.import.log'
    _description = 'CAMT54 Import Log'
    _order = 'create_date desc'  # Show newest entries first
    _rec_name = 'filename'  # Use filename as display name

    config_id = fields.Many2one(
        'camt54.config',
        string='Configuration',
        required=True,
        ondelete='cascade'
    )
    
    filename = fields.Char(
        string='Filename',
        required=True,
        help='Name of the processed file'
    )
    
    file_path = fields.Char(
        string='File Path',
        help='Full path of the processed file'
    )
    
    state = fields.Selection([
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('warning', 'Warning'),
    ], string='Status', default='processing', required=True)
    
    message = fields.Text(
        string='Message',
        help='Processing result message'
    )
    
    error_details = fields.Text(
        string='Error Details',
        help='Detailed error information if processing failed'
    )
    
    file_size = fields.Integer(
        string='File Size (bytes)',
        help='Size of the processed file in bytes'
    )
    
    processing_time = fields.Float(
        string='Processing Time (seconds)',
        help='Time taken to process the file'
    )
    
    statements_created = fields.Integer(
        string='Statements Created',
        default=0,
        help='Number of bank statements created from this file'
    )
    
    transactions_imported = fields.Integer(
        string='Transactions Imported',
        default=0,
        help='Number of transactions imported from this file'
    )
    
    transactions_reconciled = fields.Integer(
        string='Transactions Reconciled',
        default=0,
        help='Number of transactions automatically reconciled'
    )
    
    statement_ids = fields.Many2many(
        'account.bank.statement',
        string='Created Statements',
        help='Bank statements created from this import'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='config_id.company_id',
        store=True
    )
    
    @api.model
    def create_log_entry(self, config_id, filename, file_path=None, file_size=None):
        """
        Create a new log entry for file processing
        
        This method creates a new log record when file processing begins.
        The log starts in 'processing' state and will be updated with results
        when processing completes.
        
        Args:
            config_id (int): ID of the configuration being used
            filename (str): Name of the file being processed
            file_path (str, optional): Full path to the file
            file_size (int, optional): Size of the file in bytes
            
        Returns:
            camt54.import.log: The created log record
        """
        return self.create({
            'config_id': config_id,
            'filename': filename,
            'file_path': file_path,
            'file_size': file_size,
            'state': 'processing',  # Initial state
        })
    
    def log_success(self, message, statements_created=0, transactions_imported=0, 
                   transactions_reconciled=0, processing_time=0, statement_ids=None):
        """
        Update log entry with successful processing results
        
        Called when file processing completes successfully. Updates the log
        with all relevant statistics and links to created bank statements.
        
        Args:
            message (str): Success message describing what happened
            statements_created (int): Number of bank statements created
            transactions_imported (int): Number of transaction lines imported
            transactions_reconciled (int): Number of transactions reconciled
            processing_time (float): Time taken to process in seconds
            statement_ids (list, optional): IDs of created bank statements
        """
        self.ensure_one()  # Ensure method is called on single record
        vals = {
            'state': 'success',
            'message': message,
            'statements_created': statements_created,
            'transactions_imported': transactions_imported,
            'transactions_reconciled': transactions_reconciled,
            'processing_time': processing_time,
        }
        # Link to created bank statements if provided
        if statement_ids:
            vals['statement_ids'] = [(6, 0, statement_ids)]  # Replace all links
        self.write(vals)
    
    def log_error(self, message, error_details=None, processing_time=0):
        """
        Update log entry with error information
        
        Called when file processing fails. Records the error message and
        detailed error information for troubleshooting.
        
        Args:
            message (str): Brief error message
            error_details (str, optional): Detailed error information/stack trace
            processing_time (float): Time taken before error occurred
        """
        self.ensure_one()  # Ensure method is called on single record
        self.write({
            'state': 'error',
            'message': message,
            'error_details': error_details,
            'processing_time': processing_time,
        })
    
    def log_warning(self, message, statements_created=0, transactions_imported=0,
                   transactions_reconciled=0, processing_time=0, statement_ids=None):
        """
        Update log entry with warning information
        
        Called when file processing succeeds but with warnings (e.g., partial
        reconciliation, validation issues). Records both success statistics
        and warning details.
        
        Args:
            message (str): Warning message describing issues
            statements_created (int): Number of bank statements created
            transactions_imported (int): Number of transaction lines imported
            transactions_reconciled (int): Number of transactions reconciled
            processing_time (float): Time taken to process in seconds
            statement_ids (list, optional): IDs of created bank statements
        """
        self.ensure_one()  # Ensure method is called on single record
        vals = {
            'state': 'warning',
            'message': message,
            'statements_created': statements_created,
            'transactions_imported': transactions_imported,
            'transactions_reconciled': transactions_reconciled,
            'processing_time': processing_time,
        }
        # Link to created bank statements if provided
        if statement_ids:
            vals['statement_ids'] = [(6, 0, statement_ids)]  # Replace all links
        self.write(vals)
    
    def action_view_statements(self):
        """
        Open the bank statements created from this import
        
        This action is available when bank statements were successfully created.
        It opens the bank statement list view filtered to show only the
        statements created by this specific import.
        
        Returns:
            dict: Odoo action dictionary to open bank statements view
                  Returns None if no statements were created
        """
        self.ensure_one()  # Ensure method is called on single record
        
        # Only show action if statements were actually created
        if not self.statement_ids:
            return
        
        # Get the standard bank statement action and modify it
        action = self.env.ref('account.action_bank_statement_tree').read()[0]
        
        # Filter to show only statements from this import
        action['domain'] = [('id', 'in', self.statement_ids.ids)]
        
        # Set default journal for context
        action['context'] = {'default_journal_id': self.config_id.journal_id.id}
        
        return action
    
    def action_retry_processing(self):
        """
        Retry processing a failed file
        
        This action is available for log entries in 'error' state. It attempts
        to reprocess the file using the same configuration. The file must still
        exist at its original location.
        
        Returns:
            bool: True if retry was initiated, False if file not available
        """
        self.ensure_one()  # Ensure method is called on single record
        
        # Only allow retry for failed imports
        if self.state != 'error':
            return
        
        # Check if original file still exists
        if not self.file_path or not os.path.exists(self.file_path):
            self.log_error("File no longer exists at original location")
            return
        
        # Attempt to reprocess the file using the same configuration
        importer = self.env['camt54.auto.importer']
        return importer.process_single_file(self.config_id, self.file_path, log_entry=self)