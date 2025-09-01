# 🚀 NutriTame Deployment Instructions - FINAL FIX

## ✅ **ISSUES RESOLVED**

### 1. **Build Error Fixed** (`ajv/dist/compile/codegen`)
- **Root Cause**: React Scripts 5.0.1 incompatible with Node 22
- **Solution**: Force Node 20.x runtime in Vercel configuration

### 2. **API 404 Errors Fixed** (Double `/api/` paths)
- **Root Cause**: `${API}/api/demo-config.php` created double paths
- **Solution**: Changed to `${API}/demo-config.php`

### 3. **CORS Issues Addressed** 
- **Solution**: Updated environment variables for proper API routing

---

## 🎯 **DEPLOYMENT OPTIONS**

### **OPTION A: Vercel (Recommended - Handles Node 22 automatically)**

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy from root directory
cd /app
vercel --prod

# 3. Set environment variables in Vercel dashboard:
# NEXT_PUBLIC_API_BASE = https://app.nutritame.com/api
```

### **OPTION B: Manual Build (Any host including Hostinger)**

```bash
# Use Node 20 (critical for build success)
nvm use 20  # or ensure Node 20.x is active

# Build the project
cd /app/frontend
rm -f package-lock.json
npm install --legacy-peer-deps
npm run build

# Upload contents of frontend/build/ folder to your host
# For Hostinger: Upload to public_html/app/
```

---

## 📋 **TEST CHECKLIST**

### ✅ **Build Test** (Already Passed)
```bash
cd /app/frontend && npm run build
# ✅ Completes without ajv error
# ✅ Generates build folder successfully
```

### ✅ **API Test** (Already Passed)
```bash
curl "https://app.nutritame.com/api/demo-config.php"
# ✅ Returns: {"demo_mode":true,"launch_date":"2025-10-01"...}

curl -X POST "https://app.nutritame.com/api/demo-config.php?endpoint=access" \
  -H "Content-Type: application/json" -d '{"email":""}'
# ✅ Returns: {"demo_access":true,"access_token":"..."}
```

### ✅ **User Flow Test** (Next Steps)
1. **Landing Page** → Should show "Your Personal Diabetes Health Coach"
2. **Click "Get Started"** → Should navigate to demo landing page
3. **Demo Landing Page** → Should show "Test Drive the Future of Diabetes Management"  
4. **Click "Start Free Demo Now"** → Should call API successfully and progress to profile setup

---

## 📁 **FILES MODIFIED**

```
✅ /vercel.json              - Added Node 20 runtime configuration
✅ /frontend/.env            - Updated API endpoint variables  
✅ /frontend/src/DemoLandingPage.js - Fixed double /api/ paths
✅ /DEPLOYMENT_FIX.md        - Technical documentation
✅ /DEPLOYMENT_INSTRUCTIONS.md - This file
```

---

## 🔄 **ROLLBACK PLAN**

### Quick Git Rollback
```bash
# Save current state as backup
git stash push -m "deployment-fix-backup"

# Rollback to previous state
git reset --hard HEAD~5
```

### Selective Rollback
```bash
# Revert specific files if needed
git checkout HEAD~1 -- vercel.json
git checkout HEAD~1 -- frontend/src/DemoLandingPage.js  
git checkout HEAD~1 -- frontend/.env
```

---

## ⚠️ **CRITICAL NOTES**

1. **Node Version**: Must use **Node 20.x** for building (not Node 22)
2. **API Endpoints**: Backend PHP is working correctly at `https://app.nutritame.com/api/`
3. **Environment Variables**: Set `NEXT_PUBLIC_API_BASE=https://app.nutritame.com/api` in production
4. **Build Command**: Always use `npm install --legacy-peer-deps` due to React 19 peer dependencies

---

## 🎉 **READY FOR DEPLOYMENT**

The build works locally and API endpoints are confirmed functional. You can now:

1. **Deploy to Vercel** (automatic Node 20 handling) **OR**
2. **Build locally with Node 20** and upload to Hostinger

**Status**: ✅ **READY** - All critical issues resolved
**Next Step**: Choose deployment method and deploy!