// Vercel API route for AI chat
export default function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'POST') {
    const { message } = req.body || {};
    
    if (!message) {
      res.status(400).json({ error: 'Message is required' });
      return;
    }

    const response = generateDemoResponse(message);
    res.status(200).json({ response });
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}

function generateDemoResponse(message) {
  const messageLower = message.toLowerCase();
  
  // Breakfast suggestions
  if (messageLower.includes('breakfast')) {
    return "For a diabetic-friendly breakfast, I recommend:\n\n• 2 scrambled eggs with spinach\n• 1 slice whole grain toast\n• 1/2 cup berries\n• 1 cup unsweetened almond milk\n\nThis meal provides protein to help stabilize blood sugar and fiber to slow carb absorption. Aim for 30-40g total carbs.";
  }
  
  // Lunch suggestions
  if (messageLower.includes('lunch')) {
    return "Here's a balanced diabetic lunch:\n\n• Grilled chicken salad with mixed greens\n• 1/2 cup quinoa\n• Olive oil vinaigrette\n• Side of roasted vegetables\n\nThis provides lean protein, complex carbs, and healthy fats while keeping portions controlled for blood sugar management.";
  }
  
  // Dinner suggestions
  if (messageLower.includes('dinner')) {
    return "For dinner, try this diabetes-friendly meal:\n\n• 4oz baked salmon\n• 1 cup roasted broccoli\n• 1/2 cup brown rice\n• Small side salad\n\nRich in omega-3s and fiber, this meal helps maintain stable blood glucose levels throughout the evening.";
  }
  
  // Snack suggestions
  if (messageLower.includes('snack')) {
    return "Great diabetic snack options:\n\n• Apple slices with 1 tbsp almond butter\n• Greek yogurt with cinnamon\n• Handful of mixed nuts\n• Vegetable sticks with hummus\n\nThese combine protein and fiber to help prevent blood sugar spikes.";
  }
  
  // Carb counting
  if (messageLower.includes('carb') || messageLower.includes('count')) {
    return "Carb counting basics:\n\n• Aim for 45-60g carbs per meal\n• 15-30g for snacks\n• Focus on complex carbs (whole grains, legumes)\n• Pair carbs with protein or healthy fats\n• Read nutrition labels carefully\n\nConsistent carb intake helps maintain stable blood sugar levels.";
  }
  
  // Restaurant dining
  if (messageLower.includes('restaurant') || messageLower.includes('dining')) {
    return "Restaurant tips for diabetics:\n\n• Check menus online beforehand\n• Ask for dressings and sauces on the side\n• Choose grilled over fried options\n• Request steamed vegetables\n• Consider sharing entrees or taking half home\n\nDon't hesitate to ask your server about preparation methods and ingredients!";
  }
  
  // General greeting or other messages
  return "Hello! I'm your NutriTame AI Health Coach, specialized in diabetic meal planning. I can help you with:\n\n• Meal planning and recipes\n• Carb counting guidance\n• Restaurant dining tips\n• Blood sugar management through nutrition\n• Shopping lists for healthy eating\n\nWhat specific nutrition question can I help you with today? Always remember to consult with your healthcare provider for medical decisions.";
}