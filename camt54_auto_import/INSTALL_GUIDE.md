# 🔧 CAMT54 Auto Import - Technical Installation Guide

## 📋 Prerequisites Checklist

### System Requirements
- ✅ **Odoo 17.0+** (this module is specifically designed for v17)
- ✅ **Python 3.8+** (standard with Odoo 17)
- ✅ **Linux/Windows** file system access
- ✅ **Database access** for creating new models

### Dependencies Check
```bash
# Check Python version
python3 --version

# Check if watchdog is available (optional)
pip3 show watchdog

# Install if missing
pip3 install watchdog
```

### File System Permissions
The Odoo user must have:
- **Read access** to watch folders
- **Write access** to processed/error folders
- **Directory creation** permissions for auto-creating folders

---

## 🚀 Installation Steps

### Method 1: Direct Installation (Recommended)

1. **Copy Module to Addons Directory**
   ```bash
   # Copy to custom addons path
   cp -r camt54_auto_import /path/to/odoo/custom/addons/
   
   # Example paths:
   # /opt/odoo/custom/addons/
   # /home/odoo/addons/
   # /var/lib/odoo/addons/
   ```

2. **Set Proper Permissions**
   ```bash
   # Make sure Odoo can read the module
   chown -R odoo:odoo /path/to/odoo/custom/addons/camt54_auto_import
   chmod -R 755 /path/to/odoo/custom/addons/camt54_auto_import
   ```

3. **Update Odoo Addons Path** (if needed)
   ```bash
   # In odoo.conf, ensure custom path is included:
   addons_path = /opt/odoo/addons,/opt/odoo/custom/addons
   ```

4. **Restart Odoo Service**
   ```bash
   # SystemD
   sudo systemctl restart odoo
   
   # Or manual restart
   sudo service odoo restart
   ```

### Method 2: Development Mode Installation

1. **For Development Environments**
   ```bash
   # Navigate to Odoo directory
   cd /path/to/odoo
   
   # Start with addons path
   ./odoo-bin -d your_database --addons-path=./addons,./custom/addons --dev=all
   ```

2. **Using Docker**
   ```yaml
   # docker-compose.yml
   version: '3'
   services:
     odoo:
       image: odoo:17.0
       volumes:
         - ./camt54_auto_import:/mnt/extra-addons/camt54_auto_import
       command: odoo --dev=all
   ```

---

## 📦 Module Installation in Odoo

### Step 1: Update Apps List

1. **Login as Administrator**
2. **Navigate to Apps**
3. **Click "Update Apps List"**
4. **Wait for completion**

### Step 2: Install Module

1. **Search for "CAMT54 Auto Import"**
2. **Click "Install"**
3. **Wait for dependencies to install**

### Expected Installation Process:
```
Installing: camt54_auto_import
├── Creating database tables
├── Loading security rules
├── Installing views
├── Creating scheduled actions
└── ✅ Installation complete
```

---

## 🔧 Configuration Requirements

### Database Tables Created
The module creates these new tables:
- `camt54_config` - Configuration settings
- `camt54_import_log` - Processing logs
- `camt54_auto_importer` - Import engine (transient)

### Scheduled Actions
- **Name:** "CAMT54 Auto Import"
- **Interval:** 5 minutes (configurable)
- **Model:** `camt54.auto.importer`
- **Method:** `run_auto_import()`

### Security Groups
- **Accounting Users:** Read/write access to configurations and logs
- **Accounting Managers:** Full access including deletion

---

## 🗂️ Folder Structure Setup

### Recommended Directory Structure
```bash
# Create base directory
sudo mkdir -p /opt/camt54_import/{incoming,processed,errors}

# Set ownership to Odoo user
sudo chown -R odoo:odoo /opt/camt54_import

# Set permissions
sudo chmod -R 755 /opt/camt54_import
sudo chmod -R 777 /opt/camt54_import/incoming
sudo chmod -R 777 /opt/camt54_import/processed
sudo chmod -R 777 /opt/camt54_import/errors
```

### Testing Directory Access
```bash
# Test as Odoo user
sudo -u odoo touch /opt/camt54_import/incoming/test.txt
sudo -u odoo mv /opt/camt54_import/incoming/test.txt /opt/camt54_import/processed/
sudo -u odoo rm /opt/camt54_import/processed/test.txt
```

---

## ⚙️ Advanced Configuration

### Customizing Scheduled Action

1. **Navigate to Settings > Technical > Automation > Scheduled Actions**
2. **Find "CAMT54 Auto Import"**
3. **Modify settings:**
   ```
   Interval Number: 1-60 (minutes)
   Interval Type: minutes/hours/days
   Active: True/False
   ```

### Environment Variables (Optional)
```bash
# In your Odoo environment
export CAMT54_DEFAULT_WATCH_DIR="/opt/camt54_import/incoming"
export CAMT54_DEFAULT_PROCESSED_DIR="/opt/camt54_import/processed"
export CAMT54_DEFAULT_ERROR_DIR="/opt/camt54_import/errors"
```

### Logging Configuration
```python
# In Odoo config file, add for detailed logging:
[logger_camt54]
level = DEBUG
handlers = console
qualname = odoo.addons.camt54_auto_import
```

---

## 🧪 Testing Installation

### 1. Verify Module Installation
```python
# In Odoo shell (odoo-bin shell -d database_name)
modules = self.env['ir.module.module'].search([('name', '=', 'camt54_auto_import')])
print(f"Module state: {modules.state}")
# Should output: Module state: installed
```

### 2. Test Configuration Creation
1. **Go to CAMT54 Auto Import > Configurations**
2. **Create test configuration:**
   ```
   Name: Test Config
   Watch Folder: /tmp/test_camt54
   Journal: Any bank journal
   ```
3. **Click "Test Connection"**

### 3. Test Manual Import
1. **Create sample CAMT54 file** (minimal valid XML)
2. **Use Manual Import wizard**
3. **Verify import logs show success/failure**

---

## 🐛 Troubleshooting Installation

### Common Installation Issues

#### ❌ "Module not found"
**Cause:** Module not in addons path
**Solution:**
```bash
# Check addons path
grep addons_path /etc/odoo/odoo.conf

# Verify module location
ls -la /path/to/addons/camt54_auto_import/
```

#### ❌ "Permission denied"
**Cause:** Incorrect file permissions
**Solution:**
```bash
# Fix permissions
sudo chown -R odoo:odoo /path/to/addons/camt54_auto_import
sudo chmod -R 755 /path/to/addons/camt54_auto_import
```

#### ❌ "Database constraint error"
**Cause:** Conflicting data or incomplete installation
**Solution:**
```bash
# Uninstall and reinstall
# In Odoo: Apps > CAMT54 Auto Import > Uninstall
# Then reinstall fresh
```

#### ❌ "Dependency not found"
**Cause:** Missing account modules
**Solution:**
```bash
# Ensure base modules are installed:
# - account
# - account_accountant
```

### Verification Commands
```bash
# Check Odoo logs for errors
tail -f /var/log/odoo/odoo.log | grep camt54

# Check database tables exist
sudo -u postgres psql -d your_database -c "\dt *camt54*"

# Check scheduled action
# In Odoo: Settings > Technical > Automation > Scheduled Actions
```

---

## 🔄 Upgrade Instructions

### From Previous Versions
```bash
# 1. Backup database
pg_dump your_database > backup_before_upgrade.sql

# 2. Replace module files
cp -r new_camt54_auto_import /path/to/addons/

# 3. Update module in Odoo
# Apps > CAMT54 Auto Import > Upgrade

# 4. Test functionality
```

### Version Compatibility
- **v17.0.1.0.0:** Initial release
- **v17.0.1.0.1:** Bug fixes for Odoo 17 compatibility

---

## 📚 Development Setup

### For Module Customization
```bash
# Clone/download module source
git clone <repository> camt54_auto_import

# Set up development environment
pip install -r requirements.txt

# Create development database
createdb camt54_dev

# Start Odoo in development mode
./odoo-bin -d camt54_dev --addons-path=./addons,./custom/addons --dev=all
```

### Testing Framework
```bash
# Run unit tests (if available)
./odoo-bin -d test_db --addons-path=./addons,./custom/addons --test-enable --stop-after-init -i camt54_auto_import
```

---

## ✅ Post-Installation Checklist

- [ ] Module shows as "Installed" in Apps
- [ ] Menu "CAMT54 Auto Import" appears in main menu
- [ ] Can create configurations without errors
- [ ] Test connection works for sample folders
- [ ] Scheduled action is active and running
- [ ] Import logs are being created
- [ ] Manual import wizard works
- [ ] File permissions are correct for watch folders

---

## 📞 Support Information

### Log Locations
- **Odoo Logs:** `/var/log/odoo/odoo.log`
- **Module Logs:** Search for "camt54" in Odoo logs
- **Import Logs:** Available in Odoo UI under Import Logs

### Debug Information
```python
# Enable debug mode in Odoo for detailed error traces
# Add to URL: ?debug=1

# Check module version
# Apps > CAMT54 Auto Import > Technical Info
```

**Installation Complete! 🎉**

The module is now ready for configuration and use. Proceed to the USER_GUIDE.md for setup instructions.