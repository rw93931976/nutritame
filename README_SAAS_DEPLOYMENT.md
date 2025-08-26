# GlucoPlanner SaaS - Complete Deployment Guide

## 🚀 Overview

GlucoPlanner has been transformed into a full SaaS platform with:
- **Multi-tenant architecture** with isolated user environments
- **Stripe subscription billing** (Basic $9/month, Premium $19/month)
- **15-day free trial** with automatic user provisioning
- **Admin dashboard** for user and revenue management
- **GDPR/HIPAA compliance** with data export/deletion
- **Self-hosting ready** with Docker containerization

## 📋 Prerequisites

### Required Services:
1. **Stripe Account** - For payment processing
2. **Google Cloud Console** - For Maps/Places API
3. **MongoDB Database** - For data storage
4. **Domain/Subdomain** - For hosting (e.g., app.yourdomain.com)
5. **Hostinger Account** - For deployment

### Required API Keys:
- Stripe API Key (Publishable & Secret)
- Google Places API Key
- Google Maps JavaScript API Key
- Google Geocoding API Key
- Emergent LLM Key (provided in platform)

## 🔧 Environment Configuration

### Backend Environment Variables (.env):
```bash
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=glucoplanner_saas

# API Keys
STRIPE_API_KEY=sk_test_... # or sk_live_... for production
GOOGLE_PLACES_API_KEY=AIza...
USDA_API_KEY=your_usda_key
EMERGENT_LLM_KEY=your_emergent_key

# Security
JWT_SECRET=your_jwt_secret_key_here

# App Configuration
APP_ENV=production
APP_DOMAIN=app.yourdomain.com
```

### Frontend Environment Variables (.env):
```bash
REACT_APP_BACKEND_URL=https://app.yourdomain.com
```

## 🏗️ Architecture Overview

```
┌─────────────────┬──────────────────┬─────────────────┐
│   Frontend      │     Backend      │    Database     │
│   (React)       │   (FastAPI)      │   (MongoDB)     │
├─────────────────┼──────────────────┼─────────────────┤
│ - Landing Page  │ - Auth System    │ - Users         │
│ - Payment Flow  │ - Stripe API     │ - Transactions  │
│ - App Dashboard │ - Multi-tenancy  │ - Chat Sessions │
│ - Admin Panel   │ - AI Integration │ - Restaurants   │
└─────────────────┴──────────────────┴─────────────────┘
```

## 📦 Hostinger Deployment Steps

### 1. Domain Setup
```bash
# Add subdomain in Hostinger control panel
# Point app.yourdomain.com to your server IP
# Enable SSL certificate for the subdomain
```

### 2. File Upload
```bash
# Upload entire /app directory to your Hostinger server
# Recommended path: /public_html/app/

# Set proper permissions
chmod -R 755 /public_html/app/
chmod -R 777 /public_html/app/backend/logs/
```

### 3. Node.js Setup (for frontend)
```bash
# In Hostinger Node.js manager:
cd /public_html/app/frontend
npm install
npm run build

# Set startup file: build/index.html
# Set Node.js version: 18.x or higher
```

### 4. Python Setup (for backend)
```bash
# In Hostinger Python manager:
cd /public_html/app/backend
pip install -r requirements.txt

# Set startup file: server.py
# Set Python version: 3.11 or higher
```

### 5. Database Setup
```bash
# Option 1: Use Hostinger MongoDB (if available)
# Option 2: Use MongoDB Atlas (recommended)
# Option 3: Self-hosted MongoDB

# Update MONGO_URL in backend/.env accordingly
```

## 🔐 Stripe Configuration

### 1. Create Stripe Products
```javascript
// In Stripe Dashboard, create products:

// Basic Plan
{
  "name": "GlucoPlanner Basic",
  "price": "$9.00/month",
  "recurring": "monthly",
  "trial_period_days": 15
}

// Premium Plan  
{
  "name": "GlucoPlanner Premium",
  "price": "$19.00/month", 
  "recurring": "monthly",
  "trial_period_days": 15
}
```

### 2. Webhook Configuration
```bash
# Add webhook endpoint in Stripe Dashboard:
# URL: https://app.yourdomain.com/api/webhook/stripe
# Events: 
#   - checkout.session.completed
#   - customer.subscription.created
#   - customer.subscription.updated
#   - customer.subscription.deleted
#   - invoice.payment_succeeded
#   - invoice.payment_failed
```

### 3. API Keys Setup
```bash
# Get from Stripe Dashboard > Developers > API Keys
STRIPE_PUBLISHABLE_KEY=pk_test_... # or pk_live_...
STRIPE_SECRET_KEY=sk_test_...      # or sk_live_...

# Add webhook signing secret
STRIPE_WEBHOOK_SECRET=whsec_...
```

## 🗺️ Google API Configuration

### 1. Enable Required APIs
```bash
# In Google Cloud Console, enable:
- Maps JavaScript API
- Places API  
- Geocoding API
- Maps Static API (optional)
```

### 2. Create API Key
```bash
# Create API key with restrictions:
# HTTP referrers: app.yourdomain.com/*
# IP addresses: Your server IP
# APIs: Maps JavaScript, Places, Geocoding
```

### 3. Billing Setup
```bash
# Enable billing in Google Cloud Console
# Set up budget alerts for API usage
# Monitor usage in API Console
```

## 🚦 Application Flow

### 1. User Registration & Payment
```
Landing Page → Select Plan → Enter Email → Stripe Checkout → 
Payment Success → Auto Account Creation → App Access
```

### 2. Subscription Management
```
User Profile → Subscription Info → Upgrade/Downgrade → 
Stripe Customer Portal → Billing Management
```

### 3. Admin Management
```
/admin → Admin Login → Dashboard → User Management → 
Revenue Analytics → Support Tools
```

## 👨‍💼 Admin Access

### Default Admin Credentials:
```bash
Email: admin@glucoplanner.com
Password: admin123

# ⚠️ IMPORTANT: Change default password immediately!
```

### Admin Features:
- User management and analytics
- Revenue tracking and reports
- Subscription status monitoring
- Data export/deletion (GDPR)
- Customer support tools

## 🏃‍♂️ Quick Start Commands

### Development Mode:
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Frontend  
cd frontend
npm install
npm start

# Access:
# App: http://localhost:3000
# Admin: http://localhost:3000/admin
# API: http://localhost:8001/docs
```

### Production Mode:
```bash
# Use supervisor for process management
sudo supervisorctl start all
sudo supervisorctl status

# Logs
sudo supervisorctl tail backend
sudo supervisorctl tail frontend
```

## 🔒 Security Checklist

### Pre-Production:
- [ ] Change default admin password
- [ ] Use HTTPS (SSL certificate)
- [ ] Set strong JWT secret
- [ ] Configure CORS properly
- [ ] Use production Stripe keys
- [ ] Enable rate limiting
- [ ] Set up monitoring/logging
- [ ] Configure firewall rules
- [ ] Backup database regularly

### GDPR/HIPAA Compliance:
- [ ] Data encryption at rest
- [ ] Secure data transmission (HTTPS)
- [ ] User consent mechanisms
- [ ] Data export functionality
- [ ] Data deletion procedures
- [ ] Audit logging
- [ ] Privacy policy implementation
- [ ] Terms of service

## 📊 Monitoring & Analytics

### Health Checks:
```bash
# API Health
curl https://app.yourdomain.com/api/health

# Database Connection
curl https://app.yourdomain.com/api/admin/dashboard

# Stripe Webhook
Check Stripe Dashboard > Webhooks > Events
```

### Key Metrics to Monitor:
- User registration rate
- Subscription conversion rate
- Churn rate
- API usage/costs
- Error rates
- Response times

## 🚨 Troubleshooting

### Common Issues:

#### 1. Stripe Webhooks Not Working
```bash
# Check webhook URL is accessible
curl -X POST https://app.yourdomain.com/api/webhook/stripe

# Verify webhook secret in env vars
echo $STRIPE_WEBHOOK_SECRET
```

#### 2. Google API Quota Exceeded
```bash
# Check usage in Google Cloud Console
# Increase quotas or implement caching
# Add usage monitoring alerts
```

#### 3. Database Connection Issues
```bash
# Check MongoDB connection
mongosh $MONGO_URL

# Verify network access
telnet your-mongo-host 27017
```

#### 4. Frontend Build Issues
```bash
# Clear npm cache
npm cache clean --force

# Rebuild
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 💡 Scaling Considerations

### For 100+ Users:
- Use MongoDB Atlas or dedicated MongoDB server
- Implement Redis for session storage
- Set up load balancer
- Use CDN for static assets
- Enable database indexing

### For 1000+ Users:
- Horizontal scaling with multiple app instances
- Database sharding
- Implement caching layer (Redis)
- Use container orchestration (Docker Swarm/K8s)
- Set up monitoring (Prometheus/Grafana)

## 🔄 Updates & Maintenance

### Regular Tasks:
```bash
# Update dependencies monthly
npm audit fix
pip-audit --fix

# Monitor API usage
# Review user feedback  
# Update security patches
# Backup database weekly
```

### Feature Rollouts:
```bash
# Use feature flags for gradual rollout
# Test new features with subset of users
# Monitor error rates after deployment
# Have rollback plan ready
```

## 📞 Support & Help

### Resources:
- Stripe Documentation: https://stripe.com/docs
- Google Maps API: https://developers.google.com/maps
- FastAPI Docs: https://fastapi.tiangolo.com/
- React Documentation: https://reactjs.org/docs/

### Emergency Contacts:
- Server issues: Contact Hostinger support
- Payment issues: Check Stripe dashboard
- API issues: Monitor Google Cloud Console

---

## 🎯 Success Metrics

After deployment, you should see:
- ✅ Landing page loads at app.yourdomain.com
- ✅ Payment flow completes successfully
- ✅ Users can access their dashboard
- ✅ Admin panel shows user data
- ✅ Webhooks are processing payments
- ✅ All APIs are responding correctly

**Your GlucoPlanner SaaS is now ready for production! 🚀**