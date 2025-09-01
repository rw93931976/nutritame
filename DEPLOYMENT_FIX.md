# NutriTame Deployment Fix - Node 22 & CORS Issues

## **ROOT CAUSE**
- **Build Issue**: React Scripts 5.0.1 + Node 22 compatibility issue with `ajv/dist/compile/codegen` module resolution
- **API Issue**: Double `/api/` prefixes causing 404 errors on API calls

## **FIXES APPLIED**

### 1. Force Node 20 on Vercel (Build Fix)
```json
// vercel.json - Forces Node 20.x runtime
"functions": {
  "frontend/src/**": {
    "runtime": "nodejs20.x"
  }
}
```

### 2. Fixed Double API Paths (CORS/404 Fix)
```javascript
// DemoLandingPage.js - BEFORE (broken)
fetch(`${API}/api/demo-config.php`)  // → https://app.nutritame.com/api/api/demo-config.php ❌

// DemoLandingPage.js - AFTER (fixed) 
fetch(`${API}/demo-config.php`)      // → https://app.nutritame.com/api/demo-config.php ✅
```

### 3. Updated Environment Variables
```bash
# .env - Added Vercel-compatible variable
NEXT_PUBLIC_API_BASE=https://app.nutritame.com/api
REACT_APP_BACKEND_URL=https://app.nutritame.com
```

## **DEPLOYMENT STEPS**

### Option A: Deploy to Vercel (Recommended)
```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy from root folder
cd /app
vercel --prod

# 3. Set environment variables in Vercel dashboard:
# NEXT_PUBLIC_API_BASE=https://app.nutritame.com/api
```

### Option B: Manual Build for Other Hosts
```bash
# If deploying elsewhere, build locally with Node 20
cd frontend
nvm use 20  # or use Node 20
npm install --legacy-peer-deps
npm run build

# Then upload build/ folder contents
```

## **TESTING CHECKLIST**

### ✅ Build Test
```bash
cd frontend && npm run build
# Should complete without "ajv/dist/compile/codegen" error
```

### ✅ API Endpoint Test
```bash
curl "https://app.nutritame.com/api/demo-config.php"
# Should return JSON config
```

### ✅ User Flow Test
1. Visit landing page
2. Click "Get Started" → Should navigate to demo page
3. Click "Start Free Demo Now" → Should call API successfully
4. Should progress to profile setup

## **ROLLBACK PLAN**

### Git Rollback
```bash
git stash push -m "deployment-fix-backup"
git reset --hard HEAD~4
```

### Manual Rollback
```bash
# Revert vercel.json
git checkout HEAD~1 -- vercel.json

# Revert API calls
git checkout HEAD~1 -- frontend/src/DemoLandingPage.js

# Revert .env
git checkout HEAD~1 -- frontend/.env
```

## **FILES MODIFIED**
- `/vercel.json` - Added Node 20 runtime + build config
- `/frontend/src/DemoLandingPage.js` - Fixed double `/api/` paths
- `/frontend/.env` - Added Vercel env variable

---
**Status**: Ready for deployment
**Node Version**: Locked to 20.x for compatibility
**API Endpoints**: Fixed and tested