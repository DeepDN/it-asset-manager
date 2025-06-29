# 🔧 Dashboard Display Issue - Troubleshooting Guide

## 🚨 **Issue Description**
After successful login, only the left sidebar is visible, but the main dashboard content is not displaying.

## 🎯 **Quick Fixes (Try These First)**

### **Method 1: Run Diagnostic Script**
```bash
# On your EC2 instance, in the it-asset-manager directory
python diagnose_dashboard.py
```

### **Method 2: Run Automatic Fix**
```bash
# This will fix common display issues
python fix_dashboard_display.py

# Then restart your application
python app.py
```

### **Method 3: Manual Browser Fixes**
1. **Clear Browser Cache**: Ctrl+F5 or Cmd+Shift+R
2. **Try Incognito/Private Mode**
3. **Try Different Browser** (Chrome, Firefox, Safari)
4. **Check Browser Console**: Press F12, look for errors in Console tab

---

## 🔍 **Common Causes & Solutions**

### **1. CSS Loading Issues**
**Symptoms**: Sidebar visible but no main content styling
**Solution**:
```bash
# Check if external CSS is loading
curl -I https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css

# If fails, run the fix script
python fix_dashboard_display.py
```

### **2. JavaScript Errors**
**Symptoms**: Layout broken, responsive issues
**Solution**:
- Open browser console (F12)
- Look for JavaScript errors
- Run fix script to add fallback JavaScript

### **3. Database Issues**
**Symptoms**: Dashboard loads but shows zero counts
**Solution**:
```bash
# Check database and create sample data
python diagnose_dashboard.py
```

### **4. Template Rendering Issues**
**Symptoms**: Only sidebar, no main content area
**Check**: Ensure all template files exist
```bash
ls -la templates/
# Should show: base.html, dashboard.html, login.html
```

---

## 🌐 **Network & Security Issues**

### **EC2 Security Group**
Ensure your EC2 security group allows:
- **Port 5000** (for Flask app)
- **Port 80** (for HTTP)
- **Port 443** (for HTTPS)

### **Firewall Issues**
```bash
# Check if port is accessible
sudo ufw status
sudo ufw allow 5000
```

---

## 🔧 **Step-by-Step Debugging**

### **Step 1: Check Application Status**
```bash
# Ensure app is running
ps aux | grep python
netstat -tlnp | grep :5000
```

### **Step 2: Check Browser Access**
```bash
# Test from EC2 instance itself
curl http://localhost:5000/

# Should return HTML content or redirect
```

### **Step 3: Check External Access**
```bash
# From your local machine
curl http://YOUR_EC2_PUBLIC_IP:5000/
```

### **Step 4: Check Application Logs**
```bash
# Look for errors in application output
tail -f logs/app.log  # if logging is enabled
```

---

## 🎨 **CSS/Layout Specific Fixes**

### **Fix 1: Force Main Content Display**
Add this to browser console:
```javascript
document.querySelector('.main-content').style.display = 'block';
document.querySelector('.main-content').style.visibility = 'visible';
```

### **Fix 2: Check Bootstrap Loading**
In browser console:
```javascript
console.log(typeof bootstrap);  // Should not be 'undefined'
```

### **Fix 3: Mobile Responsive Issues**
```javascript
// Check viewport
console.log(window.innerWidth);
// Should adjust layout for mobile if < 768px
```

---

## 📱 **Mobile/Responsive Issues**

If using mobile or small screen:
1. **Tap hamburger menu** (if visible) to toggle sidebar
2. **Rotate device** to landscape mode
3. **Zoom out** to see full layout
4. **Try desktop browser** to confirm it's responsive issue

---

## 🚀 **Advanced Troubleshooting**

### **Check Flask Debug Mode**
```python
# In app.py, ensure debug mode for development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### **Check Template Context**
Add debug info to dashboard.html:
```html
<!-- Add this at the top of dashboard.html for debugging -->
<div style="background: yellow; padding: 10px;">
    DEBUG: total_assets = {{ total_assets }}, 
    assigned_assets = {{ assigned_assets }}
</div>
```

### **Check Database Connection**
```python
# Run this in Python shell
from app import app, db, Asset
with app.app_context():
    print(f"Assets: {Asset.query.count()}")
```

---

## 📞 **Still Having Issues?**

### **Collect Debug Information**
```bash
# Run full diagnostic
python diagnose_dashboard.py > debug_output.txt

# Check system info
uname -a
python3 --version
pip list | grep -i flask
```

### **Browser Debug Info**
1. Open Developer Tools (F12)
2. Go to Network tab
3. Refresh page
4. Check for failed requests (red entries)
5. Go to Console tab
6. Look for JavaScript errors

### **Common Error Messages**
- **"Failed to load resource"**: CSS/JS loading issue
- **"Uncaught TypeError"**: JavaScript error
- **"Template not found"**: Missing template files
- **"Database error"**: Database connection issue

---

## ✅ **Success Checklist**

After applying fixes, you should see:
- ✅ Left sidebar with navigation menu
- ✅ Main content area with dashboard cards
- ✅ Asset statistics (numbers in cards)
- ✅ Responsive layout on mobile
- ✅ No JavaScript errors in console

---

## 🎯 **Quick Test Commands**

```bash
# 1. Run diagnostic
python diagnose_dashboard.py

# 2. Apply fixes
python fix_dashboard_display.py

# 3. Restart app
python app.py

# 4. Test access
curl -I http://localhost:5000/

# 5. Check in browser
# Visit: http://YOUR_EC2_PUBLIC_IP:5000
```

---

**💡 Most dashboard display issues are resolved by running the fix script and clearing browser cache!**
