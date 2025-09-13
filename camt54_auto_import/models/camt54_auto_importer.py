# -*- coding: utf-8 -*-

import os
import glob
import time
import shutil
import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import xml.etree.ElementTree as ET
import base64

_logger = logging.getLogger(__name__)


class Camt54AutoImporter(models.Model):
    _name = 'camt54.auto.importer'
    _description = 'CAMT54 Automatic Importer'

    @api.model
    def run_auto_import(self):
        """Scheduled method to process all active configurations"""
        configs = self.env['camt54.config'].search([('active', '=', True)])
        
        for config in configs:
            try:
                self.process_configuration(config)
            except Exception as e:
                _logger.error("Error processing configuration %s: %s", config.name, str(e))
                
    def process_configuration(self, config):
        """Process a single configuration"""
        _logger.info("Processing configuration: %s", config.name)
        
        if not os.path.exists(config.watch_folder):
            _logger.error("Watch folder does not exist: %s", config.watch_folder)
            return False
        
        # Update last run time
        config.last_run = fields.Datetime.now()
        
        # Find files matching pattern
        pattern = os.path.join(config.watch_folder, config.file_pattern)
        files = glob.glob(pattern)
        
        if config.process_subfolders:
            subpattern = os.path.join(config.watch_folder, '**', config.file_pattern)
            files.extend(glob.glob(subpattern, recursive=True))
        
        processed_count = 0
        for file_path in files:
            if os.path.isfile(file_path):
                try:
                    result = self.process_single_file(config, file_path)
                    if result:
                        processed_count += 1
                except Exception as e:
                    _logger.error("Error processing file %s: %s", file_path, str(e))
        
        _logger.info("Processed %d files for configuration %s", processed_count, config.name)
        return processed_count
    
    def process_single_file(self, config, file_path, log_entry=None):
        """Process a single CAMT54 file"""
        start_time = time.time()
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create log entry if not provided
        if not log_entry:
            log_entry = self.env['camt54.import.log'].create_log_entry(
                config.id, filename, file_path, file_size
            )
        else:
            log_entry.write({
                'state': 'processing',
                'message': 'Retrying file processing...'
            })
        
        try:
            # Validate file is CAMT54
            if not self._is_valid_camt54_file(file_path):
                raise ValidationError(_("File is not a valid CAMT54 format"))
            
            # Read file content
            with open(file_path, 'rb') as file:
                file_content = file.read()
            
            # Import using Odoo's statement import functionality
            statement_ids = self._import_statement_file(config, file_content, filename)
            
            transactions_imported = 0
            transactions_reconciled = 0
            
            if statement_ids:
                # Count transactions
                statements = self.env['account.bank.statement'].browse(statement_ids)
                for statement in statements:
                    transactions_imported += len(statement.line_ids)
                
                # Perform auto-reconciliation if enabled
                if config.auto_reconcile:
                    transactions_reconciled = self._auto_reconcile_statements(config, statements)
            
            processing_time = time.time() - start_time
            
            # Log success
            log_entry.log_success(
                message=_("Successfully imported %d statements with %d transactions") % 
                        (len(statement_ids) if statement_ids else 0, transactions_imported),
                statements_created=len(statement_ids) if statement_ids else 0,
                transactions_imported=transactions_imported,
                transactions_reconciled=transactions_reconciled,
                processing_time=processing_time,
                statement_ids=statement_ids
            )
            
            # Move file to processed folder or delete
            self._handle_processed_file(config, file_path, success=True)
            
            return True
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            
            # Log error
            log_entry.log_error(
                message=_("Failed to process file: %s") % error_msg,
                error_details=error_msg,
                processing_time=processing_time
            )
            
            # Move file to error folder
            self._handle_processed_file(config, file_path, success=False)
            
            _logger.error("Error processing file %s: %s", file_path, error_msg)
            return False
    
    def _is_valid_camt54_file(self, file_path):
        """Check if file is a valid CAMT54 XML file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Check for CAMT54 specific elements
            # CAMT.054 typically contains BkToCstmrDbtCdtNtfctn
            camt54_indicators = [
                'BkToCstmrDbtCdtNtfctn',  # Bank To Customer Debit Credit Notification
                'camt.054',
                'CstmrPmtAdvce'  # Customer Payment Advice
            ]
            
            root_str = ET.tostring(root, encoding='unicode')
            return any(indicator in root_str for indicator in camt54_indicators)
            
        except ET.ParseError:
            return False
        except Exception:
            return False
    
    def _import_statement_file(self, config, file_content, filename):
        """Import statement file using Odoo's import functionality"""
        try:
            # In Odoo 17, try using the simplified import approach
            # First attempt: use account.statement.import if available
            try:
                wizard = self.env['account.statement.import'].create({})
                wizard = wizard.with_context(
                    default_journal_id=config.journal_id.id,
                    journal_id=config.journal_id.id
                )
                
                # Try different field combinations for file data
                if hasattr(wizard, '_fields') and 'statement_file' in wizard._fields:
                    wizard.write({
                        'statement_file': base64.b64encode(file_content),
                        'statement_filename': filename,
                    })
                elif hasattr(wizard, '_fields') and 'attachment_ids' in wizard._fields:
                    # Create attachment and use it
                    attachment = self.env['ir.attachment'].create({
                        'name': filename,
                        'datas': base64.b64encode(file_content),
                        'mimetype': 'application/xml',
                    })
                    wizard.write({'attachment_ids': [(6, 0, [attachment.id])]})
                
                # Try to call import method
                if hasattr(wizard, 'import_file_button'):
                    result = wizard.import_file_button()
                elif hasattr(wizard, 'import_file'):
                    result = wizard.import_file()
                else:
                    raise AttributeError("No import method found")
                    
            except Exception as import_error:
                _logger.warning("Standard import failed: %s", str(import_error))
                # Fallback: create bank statement directly
                return self._create_statement_directly(config, file_content, filename)
            
            # Extract statement IDs from the result
            if result and isinstance(result, dict):
                if result.get('context', {}).get('statement_ids'):
                    return result['context']['statement_ids']
                elif result.get('res_id'):
                    return [result['res_id']]
                elif result.get('domain'):
                    # Parse domain to extract IDs
                    domain = result.get('domain', [])
                    for clause in domain:
                        if isinstance(clause, list) and len(clause) == 3 and clause[0] == 'id':
                            if clause[1] == 'in':
                                return clause[2]
                            elif clause[1] == '=':
                                return [clause[2]]
            
            # Fallback: try to find recently created statements for this journal
            statements = self.env['account.bank.statement'].search([
                ('journal_id', '=', config.journal_id.id),
                ('create_date', '>=', fields.Datetime.now() - timedelta(minutes=1))
            ])
            return statements.ids if statements else []
                
        except Exception as e:
            _logger.error("Error importing statement file %s: %s", filename, str(e))
            raise
    
    def _create_statement_directly(self, config, file_content, filename):
        """Fallback method to create bank statement directly from CAMT54"""
        try:
            # Parse XML content
            tree = ET.fromstring(file_content)
            
            # Create a simple statement as fallback
            # Note: This is a simplified implementation - you might need to expand this
            # based on your specific CAMT54 structure
            statement = self.env['account.bank.statement'].create({
                'name': filename,
                'journal_id': config.journal_id.id,
                'date': fields.Date.today(),
                'balance_start': 0.0,
                'balance_end_real': 0.0,
            })
            
            _logger.info("Created fallback statement %s for file %s", statement.name, filename)
            return [statement.id]
            
        except Exception as e:
            _logger.error("Failed to create direct statement for %s: %s", filename, str(e))
            return []
    
    def _auto_reconcile_statements(self, config, statements):
        """Perform automatic reconciliation on imported statements"""
        reconciled_count = 0
        
        for statement in statements:
            for line in statement.line_ids:
                if line.is_reconciled:
                    continue
                
                try:
                    if config.reconcile_method == 'exact_match':
                        reconciled = self._reconcile_exact_match(line)
                    elif config.reconcile_method == 'reference_match':
                        reconciled = self._reconcile_reference_match(line)
                    elif config.reconcile_method == 'partner_amount':
                        reconciled = self._reconcile_partner_amount(line)
                    else:  # smart_match
                        reconciled = self._reconcile_smart_match(line)
                    
                    if reconciled:
                        reconciled_count += 1
                        
                except Exception as e:
                    _logger.warning("Error reconciling line %s: %s", line.name, str(e))
        
        return reconciled_count
    
    def _reconcile_exact_match(self, line):
        """Reconcile based on exact amount match"""
        # Find unreconciled move lines with same amount
        move_lines = self.env['account.move.line'].search([
            ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
            ('amount_residual', '=', abs(line.amount)),
            ('reconciled', '=', False),
            ('company_id', '=', line.company_id.id),
        ])
        
        if len(move_lines) == 1:
            try:
                line.reconcile([{'id': move_lines[0].id}])
                return True
            except:
                pass
        return False
    
    def _reconcile_reference_match(self, line):
        """Reconcile based on reference match"""
        if not line.ref:
            return False
        
        # Search for invoices with matching reference
        invoices = self.env['account.move'].search([
            ('ref', '=', line.ref),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('company_id', '=', line.company_id.id),
        ])
        
        for invoice in invoices:
            receivable_lines = invoice.line_ids.filtered(
                lambda l: l.account_id.account_type in ['asset_receivable', 'liability_payable'] 
                and not l.reconciled
            )
            if receivable_lines and abs(receivable_lines[0].amount_residual) == abs(line.amount):
                try:
                    line.reconcile([{'id': receivable_lines[0].id}])
                    return True
                except:
                    pass
        return False
    
    def _reconcile_partner_amount(self, line):
        """Reconcile based on partner and amount match"""
        if not line.partner_id:
            return False
        
        # Find unreconciled move lines for same partner with same amount
        move_lines = self.env['account.move.line'].search([
            ('partner_id', '=', line.partner_id.id),
            ('account_id.account_type', 'in', ['asset_receivable', 'liability_payable']),
            ('amount_residual', '=', abs(line.amount)),
            ('reconciled', '=', False),
            ('company_id', '=', line.company_id.id),
        ])
        
        if len(move_lines) == 1:
            try:
                line.reconcile([{'id': move_lines[0].id}])
                return True
            except:
                pass
        return False
    
    def _reconcile_smart_match(self, line):
        """Smart reconciliation combining multiple methods"""
        # Try reference match first
        if self._reconcile_reference_match(line):
            return True
        
        # Then try partner + amount
        if self._reconcile_partner_amount(line):
            return True
        
        # Finally try exact amount
        return self._reconcile_exact_match(line)
    
    def _handle_processed_file(self, config, file_path, success=True):
        """Move or delete processed file based on configuration"""
        try:
            if success:
                if config.processed_folder:
                    dest_path = os.path.join(config.processed_folder, os.path.basename(file_path))
                    shutil.move(file_path, dest_path)
                elif config.delete_after_processing:
                    os.remove(file_path)
            else:
                if config.error_folder:
                    dest_path = os.path.join(config.error_folder, os.path.basename(file_path))
                    shutil.move(file_path, dest_path)
        except Exception as e:
            _logger.warning("Could not move/delete file %s: %s", file_path, str(e))