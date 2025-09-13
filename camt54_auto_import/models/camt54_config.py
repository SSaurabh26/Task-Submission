# -*- coding: utf-8 -*-
"""
CAMT54 Configuration Model

This module defines the configuration settings for CAMT54 automatic import.
Each configuration represents a complete setup for monitoring a specific folder
and processing CAMT54 files according to defined rules.

Author: Custom Development Team
License: LGPL-3
"""

import os
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Camt54Config(models.Model):
    """
    CAMT54 Auto Import Configuration Model
    
    This model stores all the configuration settings needed for automatic
    CAMT54 file processing, including:
    - Folder monitoring settings
    - File processing rules
    - Reconciliation preferences
    - Journal assignments
    
    Each record represents one complete import configuration that can be
    independently activated or deactivated.
    """
    _name = 'camt54.config'
    _description = 'CAMT54 Auto Import Configuration'
    _rec_name = 'name'  # Field to use as display name

    name = fields.Char(
        string='Configuration Name',
        required=True,
        help='Name to identify this configuration'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this configuration is active for monitoring'
    )
    
    watch_folder = fields.Char(
        string='Watch Folder Path',
        required=True,
        help='Full path to the folder containing CAMT54 files to import'
    )
    
    processed_folder = fields.Char(
        string='Processed Files Folder',
        help='Folder to move successfully processed files (optional)'
    )
    
    error_folder = fields.Char(
        string='Error Files Folder',
        help='Folder to move files that failed processing (optional)'
    )
    
    journal_id = fields.Many2one(
        'account.journal',
        string='Bank Journal',
        required=True,
        domain=[('type', '=', 'bank')],
        help='Journal where statements will be imported'
    )
    
    auto_reconcile = fields.Boolean(
        string='Auto Reconcile',
        default=True,
        help='Automatically reconcile transactions after import'
    )
    
    reconcile_method = fields.Selection([
        ('exact_match', 'Exact Amount Match'),
        ('reference_match', 'Reference Match'),
        ('partner_amount', 'Partner + Amount Match'),
        ('smart_match', 'Smart Matching'),
    ], string='Reconciliation Method', default='smart_match',
       help='Method to use for automatic reconciliation')
    
    file_pattern = fields.Char(
        string='File Pattern',
        default='*.xml',
        help='File pattern to match (e.g., *.xml, camt54_*.xml)'
    )
    
    process_subfolders = fields.Boolean(
        string='Process Subfolders',
        default=False,
        help='Also monitor subfolders for files'
    )
    
    delete_after_processing = fields.Boolean(
        string='Delete Files After Processing',
        default=False,
        help='Delete files after successful processing (not recommended)'
    )
    
    last_run = fields.Datetime(
        string='Last Run',
        readonly=True,
        help='Last time this configuration was processed'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    import_log_ids = fields.One2many(
        'camt54.import.log',
        'config_id',
        string='Import Logs'
    )
    
    @api.constrains('watch_folder')
    def _check_watch_folder(self):
        """
        Validate watch folder exists and is accessible
        
        This constraint runs whenever the watch_folder field is modified.
        It ensures that the specified folder actually exists on the file system.
        If the folder doesn't exist, it raises a validation error.
        
        Raises:
            ValidationError: If the watch folder doesn't exist
        """
        for record in self:
            if record.watch_folder and not os.path.exists(record.watch_folder):
                raise ValidationError(_('Watch folder does not exist: %s') % record.watch_folder)
    
    @api.constrains('processed_folder')
    def _check_processed_folder(self):
        """
        Validate processed folder exists or can be created
        
        This constraint runs whenever the processed_folder field is modified.
        If the folder doesn't exist, it attempts to create it automatically.
        If creation fails (due to permissions or invalid path), it raises an error.
        
        Raises:
            ValidationError: If the processed folder cannot be created
        """
        for record in self:
            if record.processed_folder and not os.path.exists(record.processed_folder):
                try:
                    os.makedirs(record.processed_folder, exist_ok=True)
                except OSError:
                    raise ValidationError(_('Cannot create processed folder: %s') % record.processed_folder)
    
    @api.constrains('error_folder')
    def _check_error_folder(self):
        """
        Validate error folder exists or can be created
        
        Similar to processed folder validation, this ensures the error folder
        exists or can be created for storing files that fail processing.
        
        Raises:
            ValidationError: If the error folder cannot be created
        """
        for record in self:
            if record.error_folder and not os.path.exists(record.error_folder):
                try:
                    os.makedirs(record.error_folder, exist_ok=True)
                except OSError:
                    raise ValidationError(_('Cannot create error folder: %s') % record.error_folder)
    
    def action_test_connection(self):
        """
        Test folder access and permissions
        
        This method is called when the user clicks the "Test Connection" button
        in the configuration form. It performs comprehensive tests to verify:
        1. Read access to the watch folder
        2. Write access to processed folder (if configured)
        3. Write access to error folder (if configured)
        
        The test creates temporary files to verify write permissions and then
        removes them. This ensures the system will be able to move files
        during actual processing.
        
        Returns:
            dict: Odoo action dictionary containing notification to display
                  Either success message with file count or error details
        """
        self.ensure_one()  # Ensure method is called on single record
        try:
            # Test read access to watch folder by listing its contents
            files = os.listdir(self.watch_folder)
            
            # Test write access to processed folder if it's configured
            if self.processed_folder:
                test_file = os.path.join(self.processed_folder, '.test_access')
                with open(test_file, 'w') as f:
                    f.write('test')  # Create temporary test file
                os.remove(test_file)  # Clean up test file
            
            # Test write access to error folder if it's configured
            if self.error_folder:
                test_file = os.path.join(self.error_folder, '.test_access')
                with open(test_file, 'w') as f:
                    f.write('test')  # Create temporary test file
                os.remove(test_file)  # Clean up test file
                
            # Return success notification to user
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Folder access test successful. Found %d files in watch folder.') % len(files),
                    'type': 'success',
                }
            }
        except Exception as e:
            # Return error notification with details
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Folder access test failed: %s') % str(e),
                    'type': 'danger',
                }
            }
    
    def action_manual_import(self):
        """
        Manually trigger import for this configuration
        
        This method is called when the user clicks the "Manual Import" button
        in the configuration form. It immediately processes the watch folder
        for this specific configuration, bypassing the scheduled automation.
        
        This is useful for:
        - Testing the configuration
        - Processing urgent files immediately
        - Troubleshooting import issues
        
        Returns:
            int: Number of files processed by the importer
        """
        self.ensure_one()  # Ensure method is called on single record
        # Get the auto importer service and process this configuration
        importer = self.env['camt54.auto.importer']
        return importer.process_configuration(self)