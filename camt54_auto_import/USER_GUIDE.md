# 🏦 CAMT54 Auto Import - Simple User Guide

## 🎯 What This Module Does

**In Simple Terms:** This module watches a folder on your computer. When you put CAMT54 bank files in that folder, it automatically imports them into Odoo and tries to match transactions with your invoices.

**Think of it like:** A smart assistant that processes your bank statements while you sleep!

---

## 🚀 Getting Started (5 Minutes Setup)

### 1. Create Folders on Your Computer

Create these folders (example paths - adjust for your system):

```
📁 /home/yourname/banking/
   ├── 📁 incoming/     ← Put CAMT54 files here
   ├── 📁 processed/    ← Successful files go here
   └── 📁 errors/       ← Failed files go here
```

**Windows Users:** Use paths like `C:\banking\incoming\`

### 2. Set Up in Odoo

1. **Open Odoo** and go to `CAMT54 Auto Import > Configurations`
2. **Click "Create"**
3. **Fill out the form:**

   ```
   Configuration Name: My Bank Import
   Active: ✅ (checked)
   Bank Journal: [Select your bank account]
   
   Watch Folder Path: /home/yourname/banking/incoming/
   Processed Files Folder: /home/yourname/banking/processed/
   Error Files Folder: /home/yourname/banking/errors/
   
   Auto Reconcile: ✅ (recommended)
   Reconciliation Method: Smart Matching
   ```

4. **Click "Test Connection"** - you should see "Success" message
5. **Save the configuration**

### 3. Test It Works

1. **Put a CAMT54 file** in your `incoming` folder
2. **Wait 5 minutes** (the system checks every 5 minutes)
3. **Check results:**
   - File should move to `processed` folder
   - Go to `CAMT54 Auto Import > Import Logs` to see what happened
   - Check `Accounting > Bank Statements` for imported data

**That's it! 🎉 Your system is now automated.**

---

## 📖 Daily Usage

### Normal Operation
- **Just drop CAMT54 files** in your `incoming` folder
- **System processes automatically** every 5 minutes
- **Files get organized** into `processed` or `errors` folders
- **Check logs occasionally** to ensure everything is working

### Manual Import (For Urgent Files)
1. Go to `CAMT54 Auto Import > Manual Import`
2. Select your configuration
3. Upload the file
4. Click "Import"
5. View results immediately

### Checking What Happened
- **Import Logs:** See all processing activity
- **Bank Statements:** View imported statements
- **Error Folder:** Check for any failed files

---

## 🔧 Settings Explained (In Plain English)

### Configuration Fields

| Field | What It Does | Example |
|-------|-------------|---------|
| **Name** | Just a label for you | "Daily Bank Import" |
| **Active** | Turn on/off this configuration | ✅ = Working |
| **Watch Folder** | Where you put CAMT54 files | `/home/user/banking/incoming/` |
| **Journal** | Which bank account in Odoo | "Main Bank Account" |
| **File Pattern** | Which files to process | `*.xml` = all XML files |
| **Auto Reconcile** | Match transactions automatically | ✅ = Recommended |

### Reconciliation Methods

| Method | What It Means | When It Works |
|--------|---------------|---------------|
| **Exact Amount** | Finds invoices with same amount | €100 transaction matches €100 invoice |
| **Reference Match** | Uses invoice numbers | "INV001" in bank matches invoice INV001 |
| **Partner + Amount** | Customer name + amount | "ACME Corp €500" matches ACME's €500 invoice |
| **Smart Matching** | Tries all methods above | Best choice for most users |

---

## ⚠️ Common Problems & Solutions

### 🚫 "Folder does not exist"
**Problem:** Odoo can't find your folder
**Solution:** 
- Check the folder path is exactly right
- Make sure folder exists
- Use full path (starting with `/` on Linux or `C:\` on Windows)

### 🚫 "No files being processed"
**Problem:** Files stay in incoming folder
**Solution:**
- Check "Active" is ticked ✅
- Verify file is actually CAMT54 format
- Wait 5 minutes or try manual import
- Check Import Logs for error messages

### 🚫 "Import failed"
**Problem:** File moves to error folder
**Solution:**
- Check Import Logs for exact error message
- Verify CAMT54 file isn't corrupted
- Check bank journal is set up correctly
- Try manual import to see detailed error

### ⚠️ "Import works but no reconciliation"
**Problem:** Transactions import but don't match invoices
**Solution:**
- **Normal situation** - means no matching invoices found
- Check invoice numbers match bank references
- Verify customer names are consistent
- Try different reconciliation methods

---

## 📊 What Success Looks Like

After setup, you should see:

✅ **Files automatically disappear** from incoming folder within 5 minutes
✅ **Files appear** in processed folder
✅ **Import logs show** "Success" status
✅ **Bank statements appear** in Odoo
✅ **Some transactions** show as reconciled (matched with invoices)

**Reconciliation Rate:** Don't expect 100% - even 50-70% automatic matching is excellent and saves huge amounts of time!

---

## 🆘 Need Help?

### Step 1: Check Import Logs
- Go to `CAMT54 Auto Import > Import Logs`
- Look for error messages
- Most problems are clearly explained here

### Step 2: Try Manual Import
- Use `Manual Import` to test single files
- Easier to see what's going wrong

### Step 3: Test Connection
- Use "Test Connection" button on configuration
- Verifies folder access is working

### Step 4: Check the Basics
- Folder paths correct? 📁
- Files are CAMT54 format? 📄
- Bank journal configured? 🏦
- Configuration is Active? ✅

---

## 🎉 Benefits You'll See

### Time Savings
- **Before:** Manual import every file, manual reconciliation
- **After:** Drop files in folder, system handles the rest

### Accuracy
- **Before:** Manual typing errors, missed transactions
- **After:** Automatic processing, consistent results

### Organization
- **Before:** Files scattered, hard to track what's processed
- **After:** Clean folder structure, detailed logs

### Cash Flow
- **Before:** Delayed bank statement processing
- **After:** Up-to-date bank balances within minutes

---

## 🏁 Quick Reference

### Folder Structure
```
📁 banking/
   ├── 📁 incoming/     ← Drop CAMT54 files here
   ├── 📁 processed/    ← Success files
   └── 📁 errors/       ← Failed files
```

### Menu Locations
- **Configurations:** `CAMT54 Auto Import > Configurations`
- **Manual Import:** `CAMT54 Auto Import > Manual Import`
- **Import Logs:** `CAMT54 Auto Import > Import Logs`
- **Bank Statements:** `Accounting > Bank Statements`

### Key Actions
- **Setup:** Create configuration, test connection
- **Daily Use:** Drop files in incoming folder
- **Monitor:** Check import logs occasionally
- **Troubleshoot:** Review error messages in logs

**Remember: The system runs automatically every 5 minutes. Just drop files and let it work! 🚀**
