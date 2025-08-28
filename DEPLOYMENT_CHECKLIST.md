# 🚀 NutriTame Hostinger Deployment Checklist

## Pre-Deployment Setup

### ✅ Database Setup
- [ ] Created MySQL database in Hostinger control panel
- [ ] Database name: `u[cpanel_user]_nutritame`
- [ ] Database user: `u[cpanel_user]_nutritame`  
- [ ] Strong password generated and saved
- [ ] Opened phpMyAdmin
- [ ] Imported `database_setup.sql` successfully
- [ ] Verified all tables created (users, chat_messages, restaurants, etc.)

### ✅ Backend Configuration  
- [ ] Updated `/php-backend/config.php` with:
  - [ ] Hostinger database credentials
  - [ ] Your domain name (replace app.nutritame.com)
  - [ ] Emergent LLM API key
  - [ ] Random JWT secret (64+ characters)
- [ ] All PHP files ready for upload

### ✅ Frontend Configuration
- [ ] Updated `/frontend/.env` with your domain
- [ ] Built React app: `npm run build`
- [ ] Build folder contents ready for upload

---

## Deployment Steps

### 🗂️ File Upload
- [ ] **Backend**: Uploaded `/php-backend/` contents to `/public_html/api/`
  - [ ] `config.php` in `/public_html/api/`
  - [ ] `demo-config.php` in `/public_html/api/`
  - [ ] `demo-access.php` in `/public_html/api/`
  - [ ] All other PHP files uploaded
  - [ ] `.htaccess` file uploaded
- [ ] **Frontend**: Uploaded `/frontend/build/` contents to `/public_html/`
  - [ ] `index.html` in root `/public_html/`
  - [ ] `static/` folder in root
  - [ ] All other build files in root

### 🔧 File Structure Verification
Your `/public_html/` should look like:
```
/public_html/
├── index.html              ← React app entry
├── static/                 ← React assets  
├── manifest.json           ← React manifest
├── favicon.ico             ← React favicon
└── api/                    ← PHP backend
    ├── config.php          ← Database config
    ├── demo-config.php     ← Demo endpoint
    ├── demo-access.php     ← Demo endpoint
    ├── geocode.php         ← Geocoding
    ├── shopping-lists.php  ← Shopping lists
    ├── usage-google-places.php ← API usage
    ├── .htaccess          ← Apache config
    └── api/               ← Sub endpoints
        ├── users.php      ← User profiles
        ├── chat.php       ← AI chat
        ├── restaurants.php ← Restaurant search
        └── demo.php       ← Demo routing
```

---

## Testing & Verification

### 🧪 Backend API Tests
Test these URLs in your browser:

- [ ] `https://yourdomain.com/api/demo-config.php`
  - Should return JSON with demo configuration
- [ ] `https://yourdomain.com/api/usage-google-places.php`  
  - Should return API usage stats
- [ ] `https://yourdomain.com/api/geocode.php` (POST test with tools like Postman)

### 🎨 Frontend Tests  
- [ ] `https://yourdomain.com` loads NutriTame landing page
- [ ] No 404 errors in browser console
- [ ] CSS and images load correctly
- [ ] Navigation works properly

### 🔄 Integration Tests
- [ ] Click "Start Free Demo Now" button
- [ ] Demo access creation works (connects to backend)
- [ ] User profile setup page appears
- [ ] Profile creation saves successfully
- [ ] AI chat interface loads
- [ ] Restaurant search returns demo data
- [ ] Shopping list generation works

---

## 🔑 API Keys (Optional but Recommended)

### Required for AI Chat
- [ ] **Emergent LLM Key**: Added to config.php
  - Get from: Emergent Profile → Universal Key
  - Required for AI health coach functionality

### Optional Enhancements  
- [ ] **Google Places API Key**: For real restaurant data
  - Get from: Google Cloud Console
  - Without this: Uses demo restaurant data
- [ ] **USDA API Key**: For detailed nutrition data
  - Get from: USDA FoodData Central
  - Without this: Uses basic nutrition info

---

## 🚨 Troubleshooting

### If backend endpoints return errors:
- [ ] Check Hostinger error logs
- [ ] Verify database connection in phpMyAdmin
- [ ] Ensure config.php has correct credentials
- [ ] Test direct file access: `/api/demo-config.php`

### If frontend doesn't load:
- [ ] Verify index.html in root `/public_html/`
- [ ] Check static files uploaded correctly
- [ ] Update CORS_ORIGIN in config.php to match domain

### If demo flow fails:
- [ ] Check browser console for JavaScript errors
- [ ] Verify API endpoints accessible
- [ ] Test database connection
- [ ] Check CORS headers

---

## ✅ Success Indicators

### Backend Working:
- `/api/demo-config.php` returns JSON response
- Database connection successful
- No 500 errors in Hostinger logs

### Frontend Working:  
- Landing page loads without errors
- Static assets load correctly
- Console shows no 404 errors

### Integration Working:
- Demo access button creates user successfully
- Profile setup saves to database  
- AI chat interface appears and responds
- Restaurant search displays results

---

## 🎉 Deployment Complete!

When all checkboxes are ✅, your NutriTame app is successfully deployed on Hostinger!

**Next Steps:**
- Share the demo with users
- Monitor error logs for any issues
- Add real API keys for enhanced functionality
- Prepare for official launch on October 1, 2025