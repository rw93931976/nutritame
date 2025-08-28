# 📋 Step 1: Hostinger Database Setup - DETAILED GUIDE

## 🎯 What We're Doing
Setting up a MySQL database on Hostinger to store your NutriTame app data (user profiles, chat history, restaurant searches, etc.)

---

## Part A: Creating MySQL Database in Hostinger

### A1. Access Hostinger Control Panel
1. **Go to**: `https://hpanel.hostinger.com/`
2. **Login** with your Hostinger account credentials
3. **You'll see your hosting dashboard**

### A2. Navigate to Database Section
1. **Look for the "Databases" section** in your control panel
2. **Click on "MySQL Databases"** 
   - It might be under "Advanced" or "Database" section
   - Icon usually looks like a cylinder or database symbol

### A3. Create New Database
1. **You'll see a form with fields like:**
   ```
   Database Name: [input field]
   Database Username: [input field]  
   Database Password: [input field]
   ```

2. **Fill out the form:**
   ```
   Database Name: nutritame
   Database Username: nutritame
   Database Password: [click "Generate" or create strong password]
   ```

3. **Click "Create Database"**

### A4. Note Your Generated Credentials
**Hostinger will show you the FULL credentials like:**
```
Database Name: u123456789_nutritame
Database Username: u123456789_nutritame  
Database Password: aB3$kL9#mN2@pQ7!
Database Host: localhost
```

**📝 CRITICAL: Write these down exactly as shown!**

---

## Part B: Import Database Schema

### B1. Access phpMyAdmin
1. **In your Hostinger control panel**, look for **"phpMyAdmin"**
2. **Click to open phpMyAdmin** (opens in new tab)
3. **You'll see the phpMyAdmin interface**

### B2. Select Your Database
1. **On the left sidebar**, you'll see your database: `u123456789_nutritame`
2. **Click on it** to select it
3. **The main area will show "No tables found in database"** - this is normal!

### B3. Import Database Schema
1. **Click on the "SQL" tab** at the top of phpMyAdmin
2. **You'll see a large text box for SQL commands**
3. **Open the file**: `/app/php-backend/database_setup.sql` 
4. **Copy ALL the contents** of that file
5. **Paste it into the SQL text box**
6. **Click "Go" button** to execute

### B4. Verify Tables Created
1. **Look at the left sidebar again**
2. **You should now see tables like:**
   - `users`
   - `chat_messages`
   - `restaurants`  
   - `shopping_lists`
   - `admin_users`
   - And more...

**✅ If you see these tables, database setup is complete!**

---

## Part C: Update Configuration Files

### C1. Get Your Exact Database Details
**From Hostinger, you should have:**
```
Database Host: localhost
Database Name: u123456789_nutritame    ← Your actual cpanel user number
Database User: u123456789_nutritame    ← Same as database name
Database Password: aB3$kL9#mN2@pQ7!    ← The generated password
```

### C2. Update config.php
**Edit the file `/app/php-backend/config.php`:**

**FIND these lines:**
```php
define('DB_HOST', 'localhost');
define('DB_NAME', 'u123456789_nutritame'); // Replace with your Hostinger DB name
define('DB_USER', 'u123456789_nutritame'); // Replace with your Hostinger DB user
define('DB_PASS', 'your_password_here');   // Replace with your Hostinger DB password
```

**CHANGE to your actual values:**
```php
define('DB_HOST', 'localhost');
define('DB_NAME', 'u123456789_nutritame');    // Your EXACT database name
define('DB_USER', 'u123456789_nutritame');    // Your EXACT database user  
define('DB_PASS', 'aB3$kL9#mN2@pQ7!');       // Your EXACT database password
```

### C3. Update Domain Settings
**FIND these lines:**
```php
define('API_BASE_URL', 'https://app.yoursite.com/api'); // Replace with your domain
define('CORS_ORIGIN', 'https://app.yoursite.com');     // Replace with your domain
```

**CHANGE to your actual domain:**
```php
define('API_BASE_URL', 'https://app.nutritame.com/api'); // Your actual domain
define('CORS_ORIGIN', 'https://app.nutritame.com');     // Your actual domain
```

### C4. Add Required API Keys

#### Emergent LLM Key (Required)
1. **Go to your Emergent profile** (where you're using this AI)
2. **Click on your profile icon** → **Universal Key**
3. **Copy the key**
4. **In config.php, FIND:**
   ```php
   define('EMERGENT_LLM_KEY', 'your_emergent_llm_key_here');
   ```
5. **CHANGE to:**
   ```php
   define('EMERGENT_LLM_KEY', 'your_actual_copied_key_here');
   ```

#### JWT Secret (Required)  
1. **Generate a random string** (64+ characters)
   - Use: https://www.allkeysgenerator.com/Random/Security-Encryption-Key-Generator.aspx
   - Select "256-bit" and click "Generate"
2. **In config.php, FIND:**
   ```php
   define('JWT_SECRET', 'your_jwt_secret_key_here_make_it_long_and_random');
   ```
3. **CHANGE to your generated key:**
   ```php
   define('JWT_SECRET', 'your_very_long_random_generated_key_here');
   ```

---

## Part D: Update Frontend Environment

### D1. Update React Environment File
**Edit `/app/frontend/.env`:**

**FIND:**
```
REACT_APP_BACKEND_URL=https://app.nutritame.com/api
```

**CHANGE to your domain:**
```
REACT_APP_BACKEND_URL=https://yourdomain.com/api
```
*(Replace `yourdomain.com` with your actual domain)*

---

## 🔍 What You Should Have Now

### ✅ Completed Items:
- [ ] Hostinger database created with name like `u123456789_nutritame`
- [ ] Database password saved securely  
- [ ] phpMyAdmin accessed successfully
- [ ] Database schema imported (tables visible in phpMyAdmin)
- [ ] `config.php` updated with your database credentials
- [ ] Domain name updated in config files
- [ ] Emergent LLM key added to config.php
- [ ] JWT secret generated and added
- [ ] Frontend `.env` file updated with your domain

### 📝 Information You Should Have Written Down:
```
Database Host: localhost
Database Name: u[your_number]_nutritame
Database User: u[your_number]_nutritame  
Database Password: [your_generated_password]
Your Domain: https://yourdomain.com
Emergent LLM Key: [your_copied_key]
JWT Secret: [your_generated_secret]
```

---

## 🚨 Common Issues & Solutions

### Issue: "Can't find MySQL Databases option"
**Solution:** Look under "Advanced Features" or "Database Management" section

### Issue: "Database name already exists"
**Solution:** Add a number like `nutritame2` or `nutritame_app`

### Issue: "Can't access phpMyAdmin"  
**Solution:** Wait 2-3 minutes after creating database, then try again

### Issue: "SQL import failed"
**Solution:** Make sure you selected your database first (left sidebar)

### Issue: "Where do I get Emergent LLM key?"
**Solution:** 
1. Click your profile picture (top right in this chat)
2. Select "Universal Key" 
3. Copy the key shown

---

## ✅ Step 1 Complete When:
- Database created in Hostinger ✅
- Tables imported successfully ✅  
- Config files updated with real values ✅
- All credentials saved securely ✅

**Ready for Step 2: File Upload & Deployment!**

---

## 🆘 Need Help?

If you get stuck:
1. **Take a screenshot** of what you're seeing
2. **Note the exact error message**
3. **Tell me which part you're on** (A1, A2, B1, etc.)
4. **I'll help you troubleshoot!**