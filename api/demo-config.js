// Vercel API route for demo configuration and access
export default function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const { endpoint } = req.query;

  if (req.method === 'GET' && (!endpoint || endpoint === 'config')) {
    // Demo configuration
    res.status(200).json({
      demo_mode: true,
      launch_date: '2025-10-01',
      message: 'Currently in demo mode - full access without account creation',
      launch_requirements: {
        account_required: true,
        subscription_required: true,
        basic_plan: '$9/month',
        premium_plan: '$19/month',
        free_trial: '15 days'
      }
    });
  } else if (req.method === 'POST' && endpoint === 'access') {
    // Demo access creation
    const { email } = req.body || {};
    
    const userId = generateId();
    const tenantId = generateId();
    const token = generateToken(userId, tenantId);
    
    res.status(200).json({
      demo_access: true,
      access_token: token,
      user: {
        id: userId,
        email: email || `demo_${Math.random().toString(36).substr(2, 8)}@nutritame.com`,
        diabetes_type: 'type2',
        subscription_tier: 'premium',
        subscription_status: 'active'
      },
      expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      demo_notice: 'This is a demo account with full premium access until 2025-10-01',
      launch_date: '2025-10-01',
      message: 'Demo access created successfully! Enjoy full premium features.'
    });
  } else if (req.method === 'POST' && endpoint === 'profile') {
    // Profile creation for demo
    const profileData = req.body || {};
    
    const userId = generateId();
    
    res.status(201).json({
      id: userId,
      email: profileData.email || `profile_${Math.random().toString(36).substr(2, 8)}@nutritame.com`,
      tenant_id: generateId(),
      diabetes_type: profileData.diabetes_type || 'type2',
      age: profileData.age || null,
      gender: profileData.gender || null,
      activity_level: profileData.activity_level || null,
      health_goals: profileData.health_goals || [],
      food_preferences: profileData.food_preferences || [],
      cultural_background: profileData.cultural_background || null,
      allergies: profileData.allergies || [],
      dislikes: profileData.dislikes || [],
      cooking_skill: profileData.cooking_skill || null,
      phone_number: profileData.phone_number || null,
      subscription_tier: 'premium',
      subscription_status: 'active',
      is_demo_user: true,
      created_at: new Date().toISOString()
    });
  } else {
    res.status(404).json({ error: 'Endpoint not found' });
  }
}

function generateId() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function generateToken(userId, tenantId) {
  const header = btoa(JSON.stringify({ typ: 'JWT', alg: 'HS256' }));
  const payload = btoa(JSON.stringify({
    user_id: userId,
    tenant_id: tenantId,
    exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60),
    iat: Math.floor(Date.now() / 1000)
  }));
  return `${header}.${payload}.demo_signature`;
}