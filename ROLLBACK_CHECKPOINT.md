# NutriTame Rollback Checkpoints

## Available Rollback Points

### v2.1-ai-health-coach (Current - PRODUCTION READY)
**Date**: September 3, 2025
**Commit**: e4d2588
**Bundle**: main.917c49ee.js
**Status**: ✅ STABLE - AI Health Coach Feature Complete

**Features**:
- ✅ **Real AI Health Coach**: OpenAI GPT-4o-mini integration via Emergent LLM Key
- ✅ **Plan Gating System**: Standard (10/month) vs Premium (unlimited) consultations
- ✅ **Complete Frontend Interface**: Accessible at /coach with full functionality
- ✅ **Conversation Management**: History, search, session management
- ✅ **Medical Compliance**: Proper disclaimers and safety information
- ✅ **Backend API**: 100% success rate on all 9 endpoints
- ✅ **Database Schema**: MongoDB with proper ObjectId handling
- ✅ **Mobile Responsive**: All viewport sizes supported

**Critical Fixes**:
- ✅ Build cache corruption resolved
- ✅ ObjectId serialization bug fixed in search endpoint
- ✅ Routing issues resolved for /coach access
- ✅ Backend URL configuration cleaned up

**To Use**: `git checkout v2.1-ai-health-coach`

---

### v2.0-working-rollback (Previous Stable Point)
**Date**: August 25, 2025  
**Status**: ✅ STABLE - Post Bug Fixes
**Features**: 
- ✅ Demo Mode Working
- ✅ Profile System Fixed
- ✅ Shopping Lists Display Fixed
- ✅ Navigation Links Working
- ✅ Landing Page Optimized

**To Use**: `git checkout v2.0-working-rollback`

---

## Rollback Instructions

1. **Choose your rollback point** from the list above
2. **Run the rollback command**: `git checkout [tag-name]`
3. **Restart services**: `sudo supervisorctl restart all`
4. **Verify functionality** by testing key features

## Emergency Recovery

If you need to quickly return to the last known working state:
```bash
git checkout v2.1-ai-health-coach
sudo supervisorctl restart all
```