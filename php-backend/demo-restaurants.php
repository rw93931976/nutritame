<?php
/**
 * Demo Restaurant Search Endpoint - Simplified for demo mode
 */

require_once 'config.php';

$method = $_SERVER['REQUEST_METHOD'];
$request_uri = $_SERVER['REQUEST_URI'];

if ($method === 'POST') {
    // Handle both /restaurants/search and /restaurants/search-by-location
    if (strpos($request_uri, '/search') !== false) {
        $input = json_decode(file_get_contents('php://input'), true);
        
        // Get location data
        $latitude = $input['latitude'] ?? 40.7128;
        $longitude = $input['longitude'] ?? -74.0060;
        $location = $input['location'] ?? 'Demo City';
        $keyword = $input['keyword'] ?? '';
        
        // Generate demo restaurant data
        $restaurants = generateDemoRestaurants($latitude, $longitude, $keyword);
        
        jsonResponse($restaurants);
    } else {
        jsonResponse(['error' => 'Invalid endpoint'], 404);
    }
} else {
    jsonResponse(['error' => 'Method not allowed'], 405);
}

function generateDemoRestaurants($lat, $lng, $keyword = '') {
    $restaurants = [
        [
            'place_id' => 'demo_restaurant_1',
            'name' => 'Healthy Harvest Cafe',
            'address' => '123 Wellness Blvd, Demo City',
            'latitude' => $lat + 0.001,
            'longitude' => $lng + 0.001,
            'rating' => 4.5,
            'price_level' => 2,
            'phone_number' => '(555) 123-4567',
            'website' => 'https://healthyharvest.demo',
            'types' => ['restaurant', 'healthy_food', 'cafe'],
            'diabetic_friendly' => true,
            'opening_hours' => [
                'open_now' => true,
                'weekday_text' => [
                    'Monday: 7:00 AM – 8:00 PM',
                    'Tuesday: 7:00 AM – 8:00 PM',
                    'Wednesday: 7:00 AM – 8:00 PM',
                    'Thursday: 7:00 AM – 8:00 PM',
                    'Friday: 7:00 AM – 9:00 PM',
                    'Saturday: 8:00 AM – 9:00 PM',
                    'Sunday: 8:00 AM – 7:00 PM'
                ]
            ],
            'description' => 'Farm-to-table restaurant specializing in diabetic-friendly meals with detailed nutrition information.',
            'special_features' => ['Carb counts on menu', 'Portion control options', 'Sugar-free desserts']
        ],
        [
            'place_id' => 'demo_restaurant_2',
            'name' => 'Mediterranean Garden',
            'address' => '456 Olive Street, Demo City',
            'latitude' => $lat - 0.002,
            'longitude' => $lng + 0.003,
            'rating' => 4.7,
            'price_level' => 3,
            'phone_number' => '(555) 234-5678',
            'website' => 'https://medgarden.demo',
            'types' => ['restaurant', 'mediterranean', 'healthy'],
            'diabetic_friendly' => true,
            'opening_hours' => [
                'open_now' => true,
                'weekday_text' => [
                    'Monday: 11:00 AM – 10:00 PM',
                    'Tuesday: 11:00 AM – 10:00 PM',
                    'Wednesday: 11:00 AM – 10:00 PM',
                    'Thursday: 11:00 AM – 10:00 PM',
                    'Friday: 11:00 AM – 11:00 PM',
                    'Saturday: 11:00 AM – 11:00 PM',
                    'Sunday: 12:00 PM – 9:00 PM'
                ]
            ],
            'description' => 'Authentic Mediterranean cuisine with heart-healthy options and customizable portions.',
            'special_features' => ['Grilled proteins', 'Fresh vegetables', 'Whole grain options']
        ],
        [
            'place_id' => 'demo_restaurant_3',
            'name' => 'Green Leaf Bistro',
            'address' => '789 Nutrition Ave, Demo City',
            'latitude' => $lat + 0.003,
            'longitude' => $lng - 0.001,
            'rating' => 4.3,
            'price_level' => 2,
            'phone_number' => '(555) 345-6789',
            'website' => 'https://greenleaf.demo',
            'types' => ['restaurant', 'organic', 'vegetarian'],
            'diabetic_friendly' => true,
            'opening_hours' => [
                'open_now' => false,
                'weekday_text' => [
                    'Monday: 8:00 AM – 6:00 PM',
                    'Tuesday: 8:00 AM – 6:00 PM',
                    'Wednesday: 8:00 AM – 6:00 PM',
                    'Thursday: 8:00 AM – 6:00 PM',
                    'Friday: 8:00 AM – 7:00 PM',
                    'Saturday: 9:00 AM – 7:00 PM',
                    'Sunday: Closed'
                ]
            ],
            'description' => 'Organic cafe with extensive salad bar and build-your-own bowl options.',
            'special_features' => ['Organic ingredients', 'Customizable meals', 'Nutrition calculator']
        ],
        [
            'place_id' => 'demo_restaurant_4',
            'name' => 'Protein Palace',
            'address' => '321 Fitness Way, Demo City',
            'latitude' => $lat - 0.001,
            'longitude' => $lng - 0.002,
            'rating' => 4.4,
            'price_level' => 2,
            'phone_number' => '(555) 456-7890',
            'website' => 'https://proteinpalace.demo',
            'types' => ['restaurant', 'healthy', 'sports_nutrition'],
            'diabetic_friendly' => true,
            'opening_hours' => [
                'open_now' => true,
                'weekday_text' => [
                    'Monday: 6:00 AM – 9:00 PM',
                    'Tuesday: 6:00 AM – 9:00 PM',
                    'Wednesday: 6:00 AM – 9:00 PM',
                    'Thursday: 6:00 AM – 9:00 PM',
                    'Friday: 6:00 AM – 10:00 PM',
                    'Saturday: 7:00 AM – 10:00 PM',
                    'Sunday: 7:00 AM – 8:00 PM'
                ]
            ],
            'description' => 'High-protein, low-carb meals perfect for blood sugar management.',
            'special_features' => ['Macro tracking', 'Lean proteins', 'Low-carb alternatives']
        ]
    ];
    
    // Filter by keyword if provided
    if (!empty($keyword)) {
        $keyword_lower = strtolower($keyword);
        $restaurants = array_filter($restaurants, function($restaurant) use ($keyword_lower) {
            return strpos(strtolower($restaurant['name']), $keyword_lower) !== false ||
                   strpos(strtolower($restaurant['description']), $keyword_lower) !== false ||
                   in_array($keyword_lower, array_map('strtolower', $restaurant['types']));
        });
        $restaurants = array_values($restaurants); // Reindex array
    }
    
    return $restaurants;
}
?>