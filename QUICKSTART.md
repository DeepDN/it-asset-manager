# 🚀 Quick Start Guide - IT Asset Manager

## 1. Setup (2 minutes)

```bash
cd /home/deepak/it-asset-manager
./setup.sh
```

## 2. Start Application

```bash
source venv/bin/activate
python app.py
```

## 3. Access Application

- **URL**: http://localhost:5000
- **Username**: admin
- **Password**: admin123

## 4. Add Sample Data (Optional)

```bash
python add_sample_data.py
```

## 5. Key Features to Try

### 📱 Asset Management
1. Go to **Assets** → **Add Asset**
2. Add a laptop with specifications
3. Assign it to a user
4. Export asset list to CSV

### 🔐 Application Access
1. Go to **App Access** → **Add Access**
2. Grant GitHub access to a user
3. Set access level and dates
4. Filter by application or user

### 🐙 GitHub Access
1. Go to **GitHub Access** → **Add GitHub Access**
2. Track repository permissions
3. Monitor organization access
4. Export GitHub audit trail

### 📊 Dashboard
- View system overview
- Quick action buttons
- Export all data types

## 6. Next Steps

1. **Change default password** (Security → User Management)
2. **Add your real assets** (Replace sample data)
3. **Set up regular exports** (For backup/compliance)
4. **Customize asset types** (Edit templates as needed)

## 🔧 Common Commands

```bash
# Start application
source venv/bin/activate && python app.py

# Add sample data
python add_sample_data.py

# Reset database (if needed)
rm it_assets.db && python app.py

# Update dependencies
pip install -r requirements.txt --upgrade
```

## 📞 Need Help?

- Check `README.md` for detailed documentation
- Review troubleshooting section
- Verify all files are in place

**Happy Asset Managing! 🎯**
