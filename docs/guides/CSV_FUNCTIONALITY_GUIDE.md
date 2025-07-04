# 📊 CSV Bulk Upload & Export - Complete Guide

## 🚀 **CSV Functionality Overview**

The IT Asset Manager now includes comprehensive CSV functionality for bulk operations:

### ✅ **Available Features:**
- **Bulk Upload**: Import hundreds of records at once
- **CSV Export**: Export all data for backup/reporting
- **Template Downloads**: Get properly formatted CSV templates
- **Error Handling**: Detailed validation and error reporting
- **Data Validation**: Automatic field validation and duplicate detection

---

## 📥 **Bulk Upload Features**

### **1. Assets Bulk Upload**
- **URL**: `/assets/bulk-upload`
- **Template**: Download from Assets page → "Bulk Upload" → "Download Template"
- **Features**:
  - ✅ Unique asset tag validation
  - ✅ Status validation (assigned, unassigned, maintenance, retired)
  - ✅ Condition validation (excellent, good, fair, poor)
  - ✅ Ownership validation (purchased, leased, rented)
  - ✅ Date format validation (YYYY-MM-DD)
  - ✅ Cost validation (numeric values)

### **2. Application Access Bulk Upload**
- **URL**: `/app-access/bulk-upload`
- **Template**: Download from App Access page
- **Features**:
  - ✅ Access level validation (read, write, admin, full)
  - ✅ Status validation (active, inactive, suspended)
  - ✅ Date format validation

### **3. GitHub Access Bulk Upload**
- **URL**: `/github-access/bulk-upload`
- **Template**: Download from GitHub Access page
- **Features**:
  - ✅ Access level validation (read, write, admin)
  - ✅ Status validation (active, inactive, suspended)
  - ✅ Repository and username validation

---

## 📤 **CSV Export Features**

### **Export URLs:**
- **Assets**: `/export/assets`
- **Application Access**: `/export/app-access`
- **GitHub Access**: `/export/github-access`

### **Export Features:**
- ✅ All records exported with complete data
- ✅ Professional CSV formatting
- ✅ Timestamped filenames
- ✅ Ready for Excel/Google Sheets
- ✅ Can be used as backup or for bulk editing

---

## 🎯 **How to Use CSV Functionality**

### **Method 1: Bulk Upload Assets**

1. **Navigate to Assets page**
2. **Click "Bulk Upload" button**
3. **Download CSV template**
4. **Fill in your data** (follow the format exactly)
5. **Upload the completed CSV file**
6. **Review success/error messages**

### **Method 2: Export and Modify**

1. **Export existing data** using "Export CSV" button
2. **Open in Excel/Google Sheets**
3. **Add new rows or modify existing data**
4. **Save as CSV**
5. **Use bulk upload to import changes**

---

## 📋 **CSV Format Requirements**

### **Assets CSV Format:**
```csv
asset_tag,asset_type,brand,model,serial_number,status,condition,location,purchase_date,warranty_expiry,cost,ownership,vendor,notes
LAP001,Laptop,Dell,Latitude 7420,DL123456789,assigned,excellent,Office Floor 1,2024-01-15,2027-01-15,1200.00,purchased,Dell Technologies,Sample laptop
```

### **Application Access CSV Format:**
```csv
user_name,application_name,access_level,granted_date,status,notes
John Doe,Microsoft Office 365,full,2024-01-01,active,Standard office suite access
```

### **GitHub Access CSV Format:**
```csv
user_name,github_username,repository_name,access_level,granted_date,status,notes
Jane Smith,janesmith,company-website,write,2024-02-01,active,Frontend development access
```

---

## ⚠️ **Important Validation Rules**

### **Assets:**
- **asset_tag**: Must be unique across all assets
- **status**: Must be one of: assigned, unassigned, maintenance, retired
- **condition**: Must be one of: excellent, good, fair, poor
- **ownership**: Must be one of: purchased, leased, rented
- **dates**: Must be in YYYY-MM-DD format
- **cost**: Must be numeric (decimals allowed)

### **Application Access:**
- **access_level**: Must be one of: read, write, admin, full
- **status**: Must be one of: active, inactive, suspended
- **granted_date**: Must be in YYYY-MM-DD format

### **GitHub Access:**
- **access_level**: Must be one of: read, write, admin
- **status**: Must be one of: active, inactive, suspended
- **granted_date**: Must be in YYYY-MM-DD format

---

## 🔧 **Error Handling**

### **Common Errors and Solutions:**

#### **"Asset tag already exists"**
- **Cause**: Duplicate asset tag in CSV or database
- **Solution**: Use unique asset tags for each asset

#### **"Insufficient columns"**
- **Cause**: Missing required columns in CSV
- **Solution**: Use the downloaded template with all columns

#### **"Invalid status/condition/ownership"**
- **Cause**: Using values not in the allowed list
- **Solution**: Use only the specified valid values

#### **"Invalid date format"**
- **Cause**: Dates not in YYYY-MM-DD format
- **Solution**: Format dates as 2024-01-15 (not 01/15/2024)

#### **"Invalid cost value"**
- **Cause**: Non-numeric cost values
- **Solution**: Use numeric values like 1200.00 (not $1,200)

---

## 💡 **Best Practices**

### **Before Upload:**
1. **Download the template** - Always start with the official template
2. **Keep headers intact** - Don't modify column names
3. **Validate data** - Check for duplicates and correct formats
4. **Test with small batch** - Upload 5-10 records first
5. **Backup existing data** - Export current data before bulk changes

### **During Upload:**
1. **Check file size** - Keep under 10MB for best performance
2. **Use UTF-8 encoding** - Ensures special characters work
3. **Remove empty rows** - Delete any blank rows at the end
4. **One upload at a time** - Don't upload multiple files simultaneously

### **After Upload:**
1. **Review success messages** - Check how many records were imported
2. **Check error messages** - Fix any validation errors
3. **Verify data** - Browse the records to ensure they're correct
4. **Export for backup** - Create a backup of the updated data

---

## 🎯 **Use Cases**

### **Initial System Setup:**
- Import all existing assets from spreadsheets
- Bulk create user access records
- Set up GitHub repository permissions

### **Regular Maintenance:**
- Monthly asset updates from procurement
- Quarterly access reviews and updates
- Annual asset audits and corrections

### **Data Migration:**
- Moving from other asset management systems
- Consolidating multiple spreadsheets
- Standardizing data formats

### **Reporting and Analysis:**
- Export data for executive reports
- Create custom analytics in Excel
- Generate compliance reports

---

## 🚀 **Advanced Tips**

### **Excel/Google Sheets Tips:**
1. **Use data validation** - Set up dropdowns for status, condition, etc.
2. **Format date columns** - Set column format to YYYY-MM-DD
3. **Use formulas** - Generate asset tags with formulas like `="LAP"&TEXT(ROW()-1,"000")`
4. **Freeze headers** - Keep column headers visible while scrolling

### **Large Dataset Handling:**
1. **Split large files** - Upload in batches of 500-1000 records
2. **Use unique identifiers** - Ensure asset tags follow a consistent pattern
3. **Validate before upload** - Use Excel's data validation features
4. **Monitor progress** - Check success/error counts after each batch

---

## 📞 **Getting Help**

### **If CSV Upload Fails:**
1. **Check the error messages** - They show exactly what's wrong
2. **Verify file format** - Ensure it's a proper CSV file
3. **Check column headers** - Must match template exactly
4. **Validate data types** - Dates, numbers, and text in correct format
5. **Test with template** - Try uploading the downloaded template first

### **For Large Imports:**
1. **Start small** - Test with 10-20 records first
2. **Use consistent formatting** - Keep date and number formats consistent
3. **Check for duplicates** - Especially asset tags
4. **Monitor server resources** - Large uploads may take time

---

## ✅ **Success Checklist**

After implementing CSV functionality, you should be able to:

- [ ] Download CSV templates for all modules
- [ ] Export existing data to CSV format
- [ ] Upload bulk assets with validation
- [ ] Upload bulk application access records
- [ ] Upload bulk GitHub access records
- [ ] See detailed error messages for invalid data
- [ ] Get success counts for imported records
- [ ] Use exported data as templates for new uploads

---

**🎉 Your IT Asset Manager now has complete CSV functionality for efficient bulk operations!**

---

*For technical support, check the troubleshooting guides or create an issue on GitHub.*
