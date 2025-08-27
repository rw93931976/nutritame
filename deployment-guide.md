# NutriTame Self-Hosting Deployment Guide for Hostinger

## Overview
This guide will help you deploy your full NutriTame app on your Hostinger Business hosting plan at `app.yoursite.com`.

## What We've Converted
- ✅ **FastAPI Backend → PHP Backend**: All API endpoints converted to PHP
- ✅ **MongoDB → MySQL**: Database schema created for Hostinger MySQL
- ✅ **React Frontend**: Ready to build and deploy as static files
- ✅ **All Features Preserved**: Demo Countdown Timer, AI Health Coach, Restaurant Search, etc.

## Step 1: Prepare Your Hostinger Account

### 1.1 Create MySQL Database
1. Log into your Hostinger control panel
2. Go to "Databases" → "MySQL Databases"
3. Create a new database: `u[your_id]_nutritame`
4. Create a database user with full permissions
5. Note down: database name, username, password

### 1.2 Create Subdomain
1. In Hostinger control panel, go to "Subdomains"
2. Create subdomain: `app` (will create `app.yoursite.com`)
3. Point it to a new folder: `/public_html/app`

## Step 2: Set Up the Database

### 2.1 Import Database Schema
1. In Hostinger control panel, go to "phpMyAdmin"
2. Select your NutriTame database
3. Go to "Import" tab
4. Upload and run the `database_setup.sql` file

### 2.2 Update Configuration
1. Edit `php-backend/config.php`:
```php
define('DB_HOST', 'localhost');
define('DB_NAME', 'u123456789_nutritame'); // Your actual DB name
define('DB_USER', 'u123456789_nutritame'); // Your actual DB user
define('DB_PASS', 'your_actual_password'); // Your actual DB password
```

## Step 3: Deploy Backend (PHP API)

### 3.1 Upload PHP Backend
1. Upload entire `php-backend` folder to `/public_html/app/api/`
2. Your structure should be:
```
/public_html/app/
├── api/
│   ├── config.php
│   ├── index.php
│   ├── .htaccess
│   ├── api/
│   │   ├── demo.php
│   │   ├── users.php
│   │   ├── chat.php
│   │   └── ... (other endpoint files)
│   └── database_setup.sql
└── (frontend files will go here)
```

### 3.2 Configure API Keys
Edit `config.php` and add your API keys:
```php
define('EMERGENT_LLM_KEY', 'your_actual_emergent_key');
define('GOOGLE_PLACES_API_KEY', 'your_actual_google_key');
define('USDA_API_KEY', 'your_actual_usda_key');
```

### 3.3 Test Backend
Visit: `https://app.yoursite.com/api/health`
Should return: `{"status":"OK","timestamp":"..."}`

## Step 4: Deploy Frontend (React App)

### 4.1 Update Frontend Configuration
Edit `frontend/.env`:
```
REACT_APP_BACKEND_URL=https://app.yoursite.com/api
```

### 4.2 Build React App
Run in your local environment:
```bash
cd frontend
npm run build
```

### 4.3 Upload Frontend
1. Upload contents of `frontend/build/` folder to `/public_html/app/`
2. Your structure should be:
```
/public_html/app/
├── api/ (backend files)
├── index.html
├── static/
│   ├── css/
│   ├── js/
│   └── media/
└── manifest.json
```

### 4.4 Configure Frontend Routing
Create `/public_html/app/.htaccess`:
```apache
RewriteEngine On

# Handle React Router
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_URI} !^/api/
RewriteRule . /index.html [L]

# Cache static assets
<IfModule mod_expires.c>
    ExpiresActive on
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
</IfModule>
```

## Step 5: Test Your Deployment

### 5.1 Test API Endpoints
- `https://app.yoursite.com/api/health` → Should return OK
- `https://app.yoursite.com/api/demo/config` → Should return demo config

### 5.2 Test Frontend
- `https://app.yoursite.com` → Should show your NutriTame app
- Medical disclaimer should appear
- Demo mode should work
- All features should be functional

## Step 6: Configure Your Main Website

### 6.1 Link from WordPress
In your WordPress site, add a prominent button/menu item:
- Text: "Launch NutriTame App" 
- Link: `https://app.yoursite.com`

### 6.2 Optional: Embed Preview
You can embed a preview in WordPress using iframe:
```html
<iframe src="https://app.yoursite.com" width="100%" height="600px" frameborder="0"></iframe>
```

## Troubleshooting

### Backend Issues
- Check PHP error logs in Hostinger control panel
- Verify database connection details
- Ensure all files uploaded correctly

### Frontend Issues  
- Check browser console for errors
- Verify REACT_APP_BACKEND_URL points to your API
- Ensure .htaccess rules are working

### CORS Issues
- Backend `.htaccess` handles CORS headers
- Verify your domain matches in config

## Cost Breakdown
- **Hostinger Business Hosting**: You already have this
- **Domain**: You already have this  
- **API Keys**: Free tiers available for Google Places, USDA
- **Emergent LLM**: Use your existing key
- **Total Additional Cost**: $0/month

## Next Steps After Deployment
1. Test all features thoroughly
2. Add your app link to your WordPress navigation
3. Monitor usage and performance
4. Update API keys as needed

Your NutriTame app will be fully self-hosted on your domain with zero ongoing costs!