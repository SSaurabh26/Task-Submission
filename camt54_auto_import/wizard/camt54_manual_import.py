# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Camt54ManualImport(models.TransientModel):
    _name = 'camt54.manual.import'
    _description = 'CAMT54 Manual Import Wizard'

    config_id = fields.Many2one(
        'camt54.config',
        string='Configuration',
        required=True,
        domain=[('active', '=', True)],
        help='Configuration to use for importing'
    )
    
    file_data = fields.Binary(
        string='CAMT54 File',
        required=True,
        help='Select the CAMT54 XML file to import'
    )
    
    filename = fields.Char(
        string='Filename',
        required=True,
        help='Name of the file being imported'
    )
    
    auto_reconcile = fields.Boolean(
        string='Auto Reconcile',
        help='Override configuration auto-reconcile setting'
    )
    
    @api.onchange('config_id')
    def _onchange_config_id(self):
        if self.config_id:
            self.auto_reconcile = self.config_id.auto_reconcile
    
    def action_import(self):
        """Import the selected CAMT54 file"""
        self.ensure_one()
        
        if not self.file_data:
            raise UserError(_('Please select a file to import'))
        
        if not self.filename.lower().endswith('.xml'):
            raise UserError(_('Please select a valid XML file'))
        
        # Decode file data
        file_content = base64.b64decode(self.file_data)
        
        # Create temporary config if auto_reconcile differs
        config = self.config_id
        if self.auto_reconcile != config.auto_reconcile:
            # Create a temporary configuration copy with different reconcile setting
            temp_config_vals = {
                'name': config.name + ' (Manual Import)',
                'active': False,
                'watch_folder': config.watch_folder,
                'journal_id': config.journal_id.id,
                'auto_reconcile': self.auto_reconcile,
                'reconcile_method': config.reconcile_method,
                'company_id': config.company_id.id,
            }
            config = self.env['camt54.config'].create(temp_config_vals)
        
        try:
            # Use the auto importer to process the file
            importer = self.env['camt54.auto.importer']
            
            # Create log entry
            log_entry = self.env['camt54.import.log'].create_log_entry(
                config.id, self.filename, file_size=len(file_content)
            )
            
            # Import using standard import functionality
            statement_ids = importer._import_statement_file(config, file_content, self.filename)
            
            transactions_imported = 0
            transactions_reconciled = 0
            
            if statement_ids:
                # Count transactions
                statements = self.env['account.bank.statement'].browse(statement_ids)
                for statement in statements:
                    transactions_imported += len(statement.line_ids)
                
                # Perform auto-reconciliation if enabled
                if self.auto_reconcile:
                    transactions_reconciled = importer._auto_reconcile_statements(config, statements)
            
            # Log success
            log_entry.log_success(
                message=_("Successfully imported %d statements with %d transactions via manual import") % 
                        (len(statement_ids) if statement_ids else 0, transactions_imported),
                statements_created=len(statement_ids) if statement_ids else 0,
                transactions_imported=transactions_imported,
                transactions_reconciled=transactions_reconciled,
                statement_ids=statement_ids
            )
            
            # Clean up temporary config if created
            if config != self.config_id:
                config.unlink()
            
            # Return action to view created statements
            if statement_ids:
                action = self.env.ref('account.action_bank_statement_tree').read()[0]
                action['domain'] = [('id', 'in', statement_ids)]
                action['context'] = {'default_journal_id': self.config_id.journal_id.id}
                return action
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Import Completed'),
                        'message': _('File imported successfully but no statements were created'),
                        'type': 'info',
                    }
                }
                
        except Exception as e:
            # Log error
            if 'log_entry' in locals():
                log_entry.log_error(
                    message=_("Failed to import file: %s") % str(e),
                    error_details=str(e)
                )
            
            # Clean up temporary config if created
            if config != self.config_id:
                config.unlink()
            
            raise UserError(_('Import failed: %s') % str(e))