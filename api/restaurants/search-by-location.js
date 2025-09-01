// Vercel API route for restaurant search by location
export default function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'POST') {
    const { location = 'Demo City', keyword = '' } = req.body || {};
    
    // Mock coordinates for demo (defaulting to Dallas, TX area)
    const coordinates = {
      latitude: 32.7767,
      longitude: -96.7970
    };
    
    const restaurants = [
      {
        place_id: 'demo_location_1',
        name: 'Local Healthy Eats',
        address: `${location} Area`,
        latitude: coordinates.latitude + 0.001,
        longitude: coordinates.longitude + 0.001,
        rating: 4.3,
        price_level: 2,
        types: ['restaurant', 'healthy'],
        diabetic_friendly: true,
        description: 'Local restaurant with diabetic-friendly options'
      },
      {
        place_id: 'demo_location_2',
        name: 'Nutrition Corner',
        address: `${location} Downtown`,
        latitude: coordinates.latitude - 0.001,
        longitude: coordinates.longitude + 0.002,
        rating: 4.6,
        price_level: 2,
        types: ['restaurant', 'healthy', 'organic'],
        diabetic_friendly: true,
        description: 'Organic meals with detailed nutrition information'
      }
    ];
    
    res.status(200).json(restaurants);
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}