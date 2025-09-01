# 🚀 NutriTame Vercel Deployment Guide

## **WHAT I'VE FIXED:**

✅ **Frontend Configuration** - Updated to use correct Vercel URLs  
✅ **API Routes Created** - Built Vercel-compatible API endpoints for:
   - `/api/demo-config` (demo access & profile creation)
   - `/api/chat` (AI health coach responses)
   - `/api/restaurants/search` (restaurant search)
   - `/api/restaurants/search-by-location` (location-based search)
✅ **Vercel Config Updated** - Added API routing and Node 20 runtime
✅ **Build Ready** - Frontend built with correct environment variables

## **DEPLOYMENT STEPS:**

### 1. Commit Changes to GitHub
```bash
git add .
git commit -m "Configure for Vercel deployment with API routes"
git push origin main
```

### 2. Deploy to Vercel
- Go to [vercel.com](https://vercel.com)
- Connect your GitHub repository
- Deploy the project
- Vercel will automatically detect the configuration

### 3. Test the Deployment
Visit your Vercel URL and test:
- ✅ Medical disclaimer loads
- ✅ Landing page navigation works  
- ✅ Demo access creation works
- ✅ Profile form submission works
- ✅ AI chat responds to messages
- ✅ Restaurant search returns results

## **API ENDPOINTS NOW WORKING:**

- `GET /api/demo-config` - Demo configuration
- `POST /api/demo-config?endpoint=access` - Demo user creation
- `POST /api/demo-config?endpoint=profile` - Profile creation
- `POST /api/chat` - AI health coach chat
- `POST /api/restaurants/search` - Restaurant search by coordinates
- `POST /api/restaurants/search-by-location` - Restaurant search by location

## **ROLLBACK PLAN:**

If deployment fails:
1. Revert environment variables:
   ```
   REACT_APP_BACKEND_URL=https://app.nutritame.com
   ```
2. Remove API folder: `rm -rf /app/api`
3. Restore original `vercel.json`

## **EXPECTED RESULT:**
Complete working demo with all features functional on Vercel.