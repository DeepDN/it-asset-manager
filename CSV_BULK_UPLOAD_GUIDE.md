# 📊 CSV Bulk Upload Feature Guide

## 🌟 Overview

The CSV Bulk Upload feature allows you to import multiple assets at once using a CSV file. This feature is perfect for:

- **Initial system setup** with existing asset data
- **Bulk asset updates** from external systems
- **Data migration** from other asset management tools
- **Regular bulk imports** from procurement systems

## 🚀 How to Use

### Step 1: Access Bulk Upload
1. Navigate to **Assets** page
2. Click the **"Bulk Upload"** button in the top action bar
3. Or use the sidebar navigation: **Bulk Upload**

### Step 2: Download Sample Template
1. Click **"Download Sample CSV"** button
2. This downloads `asset_sample_template.csv` with:
   - All required headers
   - 3 sample asset records
   - Proper formatting examples

### Step 3: Prepare Your Data
1. Open the downloaded CSV file in Excel, Google Sheets, or any CSV editor
2. Replace sample data with your actual asset information
3. **Keep all headers unchanged**
4. Follow the data format guidelines below

### Step 4: Upload Your File
1. Drag & drop your CSV file onto the upload area
2. Or click to browse and select your file
3. Click **"Upload & Import Assets"**
4. Review the import results

## 📋 CSV Format Requirements

### Required Fields
- **asset_tag**: Unique identifier (e.g., LAP0001, RTR0024)
- **asset_type**: Type of asset (laptop, router, monitor, etc.)
- **serial_number**: Unique serial number

### All Available Fields

| Field | Description | Example | Format |
|-------|-------------|---------|---------|
| `asset_tag` | Unique asset identifier | LAP0001 | Text |
| `asset_type` | Type of asset | laptop | Text |
| `asset_category` | Auto-filled based on type | Computing | Text |
| `ownership_type` | purchased/rented/leased | purchased | Text |
| `vendor_name` | Vendor for rented/leased assets | TechRent Solutions | Text |
| `rental_start_date` | Rental start date | 2024-01-01 | YYYY-MM-DD |
| `rental_end_date` | Rental end date | 2024-12-31 | YYYY-MM-DD |
| `rental_cost_monthly` | Monthly rental cost | 150.00 | Number |
| `purchase_date` | Purchase date | 2024-01-15 | YYYY-MM-DD |
| `purchase_cost` | Purchase cost | 1200.00 | Number |
| `warranty_expiry` | Warranty expiry date | 2027-01-15 | YYYY-MM-DD |
| `brand` | Asset brand | Dell | Text |
| `model` | Asset model | Latitude 5520 | Text |
| `serial_number` | Unique serial number | DL123456789 | Text |
| `processor` | CPU specification | Intel Core i7-1165G7 | Text |
| `ram_gb` | RAM in GB | 16 | Number |
| `storage_gb` | Storage in GB | 512 | Number |
| `storage_type` | Storage type | SSD | Text |
| `port_count` | Number of ports | 24 | Number |
| `network_type` | Network type | Ethernet | Text |
| `screen_size` | Screen size | 15.6" | Text |
| `resolution` | Screen resolution | 1920x1080 | Text |
| `audio_type` | Audio equipment type | Microphone | Text |
| `connector_type` | Connector type | HDMI | Text |
| `assigned_to` | Username assigned to | john.doe | Text |
| `assign_date` | Assignment date | 2024-01-20 | YYYY-MM-DD |
| `location` | Physical location | Office Floor 2, Desk 15 | Text |
| `status` | Asset status | assigned/unassigned | Text |
| `condition` | Asset condition | excellent/good/fair/poor/damaged | Text |
| `remarks` | Additional notes | Primary work laptop | Text |

## 🎯 Asset Types & Categories

The system automatically assigns categories based on asset types:

### Computing Devices
- `laptop` → Computing
- `desktop` → Computing
- `cpu` → Computing

### Mobile Devices
- `mobile` → Mobile
- `tablet` → Mobile
- `ipad` → Mobile
- `iphone` → Mobile

### Network Equipment
- `router` → Network
- `switch` → Network
- `firewall` → Network
- `load_balancer` → Network

### Display Equipment
- `monitor` → Display
- `television` → Display
- `projector` → Display

### Audio/Video Equipment
- `speaker` → Audio/Video
- `microphone` → Audio/Video

### Storage & Peripherals
- `usb_drive` → Storage
- `external_hdd` → Storage
- `external_ssd` → Storage
- `keyboard` → Peripherals
- `mouse` → Peripherals

### Connectors & Cables
- `hdmi_cable` → Connectors
- `usb_c_cable` → Connectors
- `lightning_cable` → Connectors
- `ethernet_cable` → Connectors

## 📅 Date Formats

The system accepts multiple date formats:
- `YYYY-MM-DD` (recommended): 2024-01-15
- `MM/DD/YYYY`: 01/15/2024
- `DD/MM/YYYY`: 15/01/2024
- `YYYY/MM/DD`: 2024/01/15

## 🔄 Import Behavior

### New Assets
- Assets with new `asset_tag` values are **created**
- All provided fields are populated

### Existing Assets
- Assets with existing `asset_tag` values are **updated**
- Only non-empty fields in CSV will update existing data
- Empty fields in CSV won't overwrite existing data

### Validation Rules
- **Asset tags must be unique** across all assets
- **Serial numbers must be unique** across all assets
- **Required fields** must not be empty
- **Date fields** must use valid date formats
- **Numeric fields** must contain valid numbers

## ⚠️ Important Notes

### Data Validation
- The system validates all data before import
- Invalid rows are reported with specific error messages
- Valid rows are imported even if some rows have errors

### Duplicate Handling
- **Asset Tag**: Existing assets are updated
- **Serial Number**: Must be unique; duplicates are rejected

### Default Values
- `ownership_type`: Defaults to "purchased" if empty
- `status`: Defaults to "assigned" if `assigned_to` is provided, otherwise "unassigned"
- `condition`: Defaults to "good" if empty
- `asset_category`: Auto-assigned based on `asset_type`

## 📊 Sample Data Examples

### Laptop Example
```csv
asset_tag,asset_type,brand,model,serial_number,ownership_type,purchase_date,purchase_cost,warranty_expiry,processor,ram_gb,storage_gb,storage_type,assigned_to,location,status,condition
LAP0001,laptop,Dell,Latitude 5520,DL123456789,purchased,2024-01-15,1200.00,2027-01-15,Intel Core i7-1165G7,16,512,SSD,john.doe,Office Floor 2 Desk 15,assigned,excellent
```

### Network Router Example
```csv
asset_tag,asset_type,brand,model,serial_number,ownership_type,vendor_name,rental_start_date,rental_end_date,rental_cost_monthly,port_count,network_type,location,status,condition
RTR0001,router,Cisco,ISR 4331,CS987654321,rented,TechRent Solutions,2024-01-01,2024-12-31,150.00,4,Ethernet,Server Room A Rack 1,unassigned,good
```

### Monitor Example
```csv
asset_tag,asset_type,brand,model,serial_number,ownership_type,purchase_date,purchase_cost,screen_size,resolution,connector_type,assigned_to,location,status,condition
MON0001,monitor,Samsung,Odyssey G5,SM456789123,purchased,2024-02-01,350.00,27",2560x1440,HDMI,jane.smith,Office Floor 1 Desk 8,assigned,excellent
```

## 🛠️ Troubleshooting

### Common Errors

#### "Invalid CSV headers"
- **Cause**: CSV headers don't match expected format
- **Solution**: Download fresh sample template and use its headers

#### "Asset tag is required"
- **Cause**: Empty asset_tag field
- **Solution**: Ensure every row has a unique asset_tag

#### "Serial number already exists"
- **Cause**: Duplicate serial number for different assets
- **Solution**: Ensure all serial numbers are unique

#### "Invalid date format"
- **Cause**: Date not in accepted format
- **Solution**: Use YYYY-MM-DD format (e.g., 2024-01-15)

### Best Practices

1. **Start Small**: Test with a few assets first
2. **Backup Data**: Export existing assets before bulk import
3. **Validate Data**: Check your CSV in a spreadsheet application
4. **Use Templates**: Always start with the downloaded sample
5. **Check Results**: Review import summary and error messages

## 🔧 Technical Details

### File Requirements
- **Format**: CSV (Comma Separated Values)
- **Encoding**: UTF-8
- **Size Limit**: No specific limit (reasonable file sizes recommended)
- **Extension**: Must be .csv

### Performance
- **Processing**: Server-side validation and import
- **Speed**: Handles hundreds of assets efficiently
- **Memory**: Optimized for large file processing

### Security
- **Validation**: All data is validated before database insertion
- **Sanitization**: Input data is cleaned and sanitized
- **Error Handling**: Graceful error handling with detailed messages

## 📈 Import Results

After upload, you'll see:
- **Success Message**: Number of assets created and updated
- **Error Messages**: Specific issues with individual rows
- **Summary**: Total processed vs. successful imports

Example result:
```
✅ Import completed: 45 assets created, 12 assets updated
⚠️ Row 15: Serial number already exists for asset LAP0023
⚠️ Row 28: Invalid date format: 2024/13/45. Use YYYY-MM-DD format.
```

## 🎯 Use Cases

### Initial System Setup
```csv
asset_tag,asset_type,brand,model,serial_number,assigned_to,location,status
LAP0001,laptop,Dell,Latitude 5520,DL001,john.doe,Floor 2 Desk 15,assigned
LAP0002,laptop,HP,EliteBook 840,HP002,jane.smith,Floor 1 Desk 8,assigned
RTR0001,router,Cisco,ISR 4331,CS001,,Server Room,unassigned
```

### Rental Equipment Tracking
```csv
asset_tag,asset_type,ownership_type,vendor_name,rental_start_date,rental_end_date,rental_cost_monthly
LAP0100,laptop,rented,TechRent,2024-01-01,2024-12-31,85.00
LAP0101,laptop,rented,TechRent,2024-01-01,2024-12-31,85.00
```

### Warranty Tracking
```csv
asset_tag,asset_type,purchase_date,warranty_expiry,purchase_cost
LAP0001,laptop,2024-01-15,2027-01-15,1200.00
MON0001,monitor,2024-02-01,2027-02-01,350.00
```

---

## 🎉 Ready to Import?

1. **Download** the sample CSV template
2. **Fill in** your asset data
3. **Upload** and let the system do the work!

The CSV Bulk Upload feature makes asset management efficient and scalable. Start with small batches to get familiar with the process, then scale up to handle your entire asset inventory.

**Happy Asset Managing! 🚀**
