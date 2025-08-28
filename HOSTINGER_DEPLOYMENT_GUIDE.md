# NutriTame Hostinger Deployment Guide

## 🎯 Overview
This guide will help you deploy the NutriTame application to Hostinger Business Hosting with PHP backend + MySQL database + React frontend.

## 📋 Prerequisites
- Hostinger Business Hosting account
- Domain name configured
- Access to Hostinger control panel
- FTP/File Manager access

---

## Step 1: Database Setup

### 1.1 Create MySQL Database
1. **Log into Hostinger control panel**
2. **Navigate to Databases → MySQL Databases**
3. **Create new database:**
   - Database name: `u[your_cpanel_user]_nutritame` 
   - Username: `u[your_cpanel_user]_nutritame`
   - Password: `[generate_strong_password]`
   - **📝 Save these credentials!**

### 1.2 Run Database Schema
1. **Open phpMyAdmin** (from Hostinger control panel)
2. **Select your database** (`u[your_cpanel_user]_nutritame`)
3. **Go to SQL tab**
4. **Copy and paste** the contents of `/php-backend/database_setup.sql`
5. **Click Execute** to create all tables

---

## Step 2: Backend Configuration

### 2.1 Update config.php
**Edit `/php-backend/config.php` with your Hostinger details:**

```php
<?php
// Database Configuration - UPDATE THESE VALUES
define('DB_HOST', 'localhost');
define('DB_NAME', 'u[YOUR_CPANEL_USER]_nutritame');     // Replace with actual DB name
define('DB_USER', 'u[YOUR_CPANEL_USER]_nutritame');     // Replace with actual DB user  
define('DB_PASS', 'YOUR_DATABASE_PASSWORD');            // Replace with actual password

// API Configuration - UPDATE YOUR DOMAIN
define('API_BASE_URL', 'https://app.nutritame.com/api'); // Your actual domain
define('CORS_ORIGIN', 'https://app.nutritame.com');     // Your actual domain

// Demo Mode Configuration
define('DEMO_MODE', true);
define('LAUNCH_DATE', '2025-10-01');

// External API Keys - ADD YOUR REAL KEYS
define('EMERGENT_LLM_KEY', 'your_emergent_llm_key_here');
define('GOOGLE_PLACES_API_KEY', 'your_google_places_key_here');
define('USDA_API_KEY', 'your_usda_api_key_here');

// JWT Configuration - GENERATE RANDOM SECRET
define('JWT_SECRET', 'your_very_long_random_jwt_secret_key_at_least_64_characters');
define('JWT_ALGORITHM', 'HS256');
define('JWT_EXPIRY', 86400); // 24 hours
?>
```

### 2.2 Upload PHP Backend Files
**Using File Manager or FTP:**
1. **Navigate to** `/public_html/` (or your domain's folder)
2. **Create folder** `/public_html/api/`
3. **Upload ALL files from `/php-backend/`** to `/public_html/api/`

**Final structure should be:**
```
/public_html/
├── api/
│   ├── config.php
│   ├── demo-config.php
│   ├── demo-access.php
│   ├── geocode.php
│   ├── shopping-lists.php
│   ├── usage-google-places.php
│   ├── .htaccess
│   └── api/
│       ├── users.php
│       ├── chat.php
│       ├── restaurants.php
│       └── demo.php
```

---

## Step 3: Frontend Configuration

### 3.1 Update React Environment
**Edit `/frontend/.env`:**
```env
REACT_APP_BACKEND_URL=https://app.nutritame.com/api
```
*(Replace `app.nutritame.com` with your actual domain)*

### 3.2 Build React App
**Run locally (before upload):**
```bash
cd frontend
npm install
npm run build
```

### 3.3 Upload React Frontend
1. **Upload contents of `/frontend/build/`** to `/public_html/`
2. **DO NOT upload the build folder itself** - upload its contents
3. **Final structure:**
```
/public_html/
├── index.html          (from build/)
├── static/             (from build/)
├── manifest.json       (from build/)
├── favicon.ico         (from build/)
└── api/               (PHP backend)
```

---

## Step 4: Testing & Verification

### 4.1 Test Backend Endpoints
**Open browser and test:**
1. `https://yourdomain.com/api/demo-config.php` → Should return JSON
2. `https://yourdomain.com/api/usage-google-places.php` → Should return usage stats
3. Check browser console for any errors

### 4.2 Test Frontend
1. **Navigate to** `https://yourdomain.com`
2. **Should load** the NutriTame landing page
3. **Click "Start Free Demo Now"** 
4. **Should connect** to backend and create demo access

### 4.3 Test Full Flow
1. **Demo landing page** loads configuration
2. **Demo access creation** works  
3. **User profile setup** saves to database
4. **AI chat interface** appears
5. **Restaurant search** returns demo data

---

## Step 5: API Keys Configuration

### 5.1 Required API Keys

**For full functionality, you'll need:**

#### Emergent LLM Key (Required for AI chat)
- Get from: User Profile → Universal Key in Emergent platform
- Add to: `EMERGENT_LLM_KEY` in config.php

#### Google Places API Key (Optional - for real restaurant data)
- Get from: Google Cloud Console → Enable Places API
- Add to: `GOOGLE_PLACES_API_KEY` in config.php
- *Without this, app uses demo restaurant data*

#### USDA API Key (Optional - for nutrition data)  
- Get from: USDA FoodData Central API
- Add to: `USDA_API_KEY` in config.php
- *Without this, app uses basic nutrition info*

### 5.2 JWT Secret Generation
**Generate a random 64-character string:**
```bash
# Use online generator or run:
openssl rand -base64 64
```

---

## 🚨 Troubleshooting

### Database Connection Issues
- ✅ Verify database credentials in config.php
- ✅ Check database exists in Hostinger panel
- ✅ Run database_setup.sql script
- ✅ Check phpMyAdmin for tables

### CORS Issues  
- ✅ Update CORS_ORIGIN in config.php to match your domain
- ✅ Ensure .htaccess file is uploaded
- ✅ Check browser console for CORS errors

### 404 Errors on API Calls
- ✅ Verify file structure: `/public_html/api/demo-config.php` exists
- ✅ Check .htaccess uploaded correctly
- ✅ Test direct file access: `yourdomain.com/api/demo-config.php`

### Frontend Not Loading
- ✅ Verify index.html in `/public_html/` (not in build/ subfolder)
- ✅ Check static files uploaded correctly  
- ✅ Update REACT_APP_BACKEND_URL in frontend/.env

---

## 📞 Support

If you encounter issues:

1. **Check Hostinger error logs** (in control panel)
2. **Test individual endpoints** directly in browser
3. **Verify database connection** through phpMyAdmin
4. **Check browser console** for JavaScript errors

---

## ✅ Success Checklist

- [ ] Database created and schema imported
- [ ] config.php updated with Hostinger credentials  
- [ ] PHP backend uploaded to `/public_html/api/`
- [ ] React build uploaded to `/public_html/`
- [ ] Demo endpoints accessible via browser
- [ ] Frontend loads and connects to backend
- [ ] Demo flow works end-to-end
- [ ] API keys added (at least Emergent LLM key)

## 🎉 You're Ready!

Once all checklist items are complete, your NutriTame app should be fully functional on Hostinger!