<?php
/**
 * Restaurant Search API Endpoints - Direct routing for React frontend
 */

require_once '../config.php';

$method = $_SERVER['REQUEST_METHOD'];
$request_uri = $_SERVER['REQUEST_URI'];

try {
    if ($method === 'POST') {
        if (strpos($request_uri, '/search-by-location') !== false) {
            searchRestaurantsByLocation();
        } elseif (strpos($request_uri, '/search') !== false) {
            searchRestaurantsByCoordinates();
        } else {
            jsonResponse(['error' => 'Invalid endpoint'], 404);
        }
    } else {
        jsonResponse(['error' => 'Method not allowed'], 405);
    }
} catch (Exception $e) {
    error_log('Restaurant API error: ' . $e->getMessage());
    jsonResponse(['error' => 'Internal server error'], 500);
}

function searchRestaurantsByCoordinates() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    $latitude = $input['latitude'] ?? 0;
    $longitude = $input['longitude'] ?? 0;
    $radius = $input['radius'] ?? 2000;
    $keyword = $input['keyword'] ?? '';
    
    if (!$latitude || !$longitude) {
        jsonResponse(['error' => 'Latitude and longitude are required'], 400);
        return;
    }
    
    try {
        // For demo mode, return mock restaurant data if external service fails
        $restaurants = findNearbyRestaurants($latitude, $longitude, $radius, $keyword);
        
        if (!$restaurants || empty($restaurants)) {
            // Mock restaurant data for demo
            $restaurants = [
                [
                    'place_id' => 'demo_restaurant_1',
                    'name' => 'Healthy Bites Cafe',
                    'address' => '123 Main St, Demo City',
                    'latitude' => $latitude + 0.001,
                    'longitude' => $longitude + 0.001,
                    'rating' => 4.5,
                    'price_level' => 2,
                    'types' => ['restaurant', 'health_food'],
                    'diabetic_friendly' => true,
                    'description' => 'Specializes in low-carb and diabetic-friendly meals'
                ],
                [
                    'place_id' => 'demo_restaurant_2',
                    'name' => 'Green Garden Restaurant',
                    'address' => '456 Oak Ave, Demo City',
                    'latitude' => $latitude - 0.001,
                    'longitude' => $longitude - 0.001,
                    'rating' => 4.2,
                    'price_level' => 2,
                    'types' => ['restaurant', 'vegetarian'],
                    'diabetic_friendly' => true,
                    'description' => 'Fresh salads and grilled proteins with nutrition info'
                ],
                [
                    'place_id' => 'demo_restaurant_3',
                    'name' => 'Mediterranean Kitchen',
                    'address' => '789 Pine St, Demo City',
                    'latitude' => $latitude + 0.002,
                    'longitude' => $longitude - 0.002,
                    'rating' => 4.7,
                    'price_level' => 3,
                    'types' => ['restaurant', 'mediterranean'],
                    'diabetic_friendly' => true,
                    'description' => 'Heart-healthy Mediterranean cuisine with portion control options'
                ]
            ];
        }
        
        jsonResponse($restaurants);
        
    } catch (Exception $e) {
        error_log('Restaurant coordinate search error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to search restaurants'], 500);
    }
}

function searchRestaurantsByLocation() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    $location = $input['location'] ?? '';
    $radius = $input['radius'] ?? 2000;
    $keyword = $input['keyword'] ?? '';
    
    if (empty($location)) {
        jsonResponse(['error' => 'Location is required'], 400);
        return;
    }
    
    try {
        // First geocode the location
        $coordinates = geocodeLocation($location);
        
        if (!$coordinates) {
            // Mock coordinates for demo (defaulting to Dallas, TX area)
            $coordinates = [
                'latitude' => 32.7767,
                'longitude' => -96.7970
            ];
        }
        
        // Then find restaurants near those coordinates
        $restaurants = findNearbyRestaurants($coordinates['latitude'], $coordinates['longitude'], $radius, $keyword);
        
        if (!$restaurants || empty($restaurants)) {
            // Mock restaurant data for location-based search
            $restaurants = [
                [
                    'place_id' => 'demo_location_1',
                    'name' => 'Local Healthy Eats',
                    'address' => $location . ' Area',
                    'latitude' => $coordinates['latitude'] + 0.001,
                    'longitude' => $coordinates['longitude'] + 0.001,
                    'rating' => 4.3,
                    'price_level' => 2,
                    'types' => ['restaurant', 'healthy'],
                    'diabetic_friendly' => true,
                    'description' => 'Local restaurant with diabetic-friendly options'
                ]
            ];
        }
        
        jsonResponse($restaurants);
        
    } catch (Exception $e) {
        error_log('Restaurant location search error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to search restaurants'], 500);
    }
}

function findNearbyRestaurants($latitude, $longitude, $radius, $keyword = '') {
    // Demo restaurant data - in production, use Google Places API
    $base_restaurants = [
        [
            'place_id' => 'demo_place_1',
            'name' => 'Healthy Harvest Cafe',
            'address' => '123 Main St, Dallas, TX',
            'latitude' => 32.7767 + (rand(-50, 50) / 10000),
            'longitude' => -96.7970 + (rand(-50, 50) / 10000),
            'rating' => 4.5,
            'price_level' => 2,
            'phone_number' => '(555) 123-4567',
            'website' => 'https://healthyharvest.com',
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
            'photos' => ['https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400'],
            'cuisine_types' => ['healthy', 'american', 'salad'],
            'diabetic_friendly_score' => 4.2
        ],
        [
            'place_id' => 'demo_place_2',
            'name' => 'Fresh Garden Bistro',
            'address' => '456 Oak Ave, Dallas, TX',
            'latitude' => 32.7589 + (rand(-50, 50) / 10000),
            'longitude' => -73.9851 + (rand(-50, 50) / 10000),
            'rating' => 4.3,
            'price_level' => 3,
            'phone_number' => '(555) 987-6543',
            'website' => 'https://freshgarden.com',
            'opening_hours' => [
                'open_now' => false,
                'weekday_text' => [
                    'Monday: 11:00 AM – 10:00 PM',
                    'Tuesday: 11:00 AM – 10:00 PM',
                    'Wednesday: 11:00 AM – 10:00 PM',
                    'Thursday: 11:00 AM – 10:00 PM',
                    'Friday: 11:00 AM – 11:00 PM',
                    'Saturday: 10:00 AM – 11:00 PM',
                    'Sunday: 10:00 AM – 9:00 PM'
                ]
            ],
            'photos' => ['https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=400'],
            'cuisine_types' => ['mediterranean', 'vegetarian', 'healthy'],
            'diabetic_friendly_score' => 4.0
        ],
        [
            'place_id' => 'demo_place_3',
            'name' => 'Green Leaf Kitchen',
            'address' => '789 Pine St, Dallas, TX',
            'latitude' => 32.7831 + (rand(-50, 50) / 10000),
            'longitude' => -96.8067 + (rand(-50, 50) / 10000),
            'rating' => 4.1,
            'price_level' => 2,
            'phone_number' => '(555) 456-7890',
            'website' => 'https://greenleafkitchen.com',
            'opening_hours' => [
                'open_now' => true,
                'weekday_text' => [
                    'Monday: 8:00 AM – 9:00 PM',
                    'Tuesday: 8:00 AM – 9:00 PM',
                    'Wednesday: 8:00 AM – 9:00 PM',
                    'Thursday: 8:00 AM – 9:00 PM',
                    'Friday: 8:00 AM – 10:00 PM',
                    'Saturday: 8:00 AM – 10:00 PM',
                    'Sunday: 9:00 AM – 8:00 PM'
                ]
            ],
            'photos' => ['https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400'],
            'cuisine_types' => ['organic', 'vegan', 'healthy'],
            'diabetic_friendly_score' => 4.4
        ],
        [
            'place_id' => 'demo_place_4',
            'name' => 'Nutrient Bowl Co.',
            'address' => '321 Elm St, Dallas, TX',
            'latitude' => 32.7955 + (rand(-50, 50) / 10000),
            'longitude' => -96.7665 + (rand(-50, 50) / 10000),
            'rating' => 4.6,
            'price_level' => 2,
            'phone_number' => '(555) 321-0987',
            'website' => 'https://nutrientbowl.com',
            'opening_hours' => [
                'open_now' => true,
                'weekday_text' => [
                    'Monday: 10:00 AM – 8:00 PM',
                    'Tuesday: 10:00 AM – 8:00 PM',
                    'Wednesday: 10:00 AM – 8:00 PM',
                    'Thursday: 10:00 AM – 8:00 PM',
                    'Friday: 10:00 AM – 9:00 PM',
                    'Saturday: 9:00 AM – 9:00 PM',
                    'Sunday: 9:00 AM – 7:00 PM'
                ]
            ],
            'photos' => ['https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400'],
            'cuisine_types' => ['bowls', 'healthy', 'grain_bowls'],
            'diabetic_friendly_score' => 4.7
        ]
    ];
    
    // Filter by keyword if provided
    if (!empty($keyword)) {
        $keyword_lower = strtolower($keyword);
        $base_restaurants = array_filter($base_restaurants, function($restaurant) use ($keyword_lower) {
            return strpos(strtolower($restaurant['name']), $keyword_lower) !== false ||
                   array_filter($restaurant['cuisine_types'], function($cuisine) use ($keyword_lower) {
                       return strpos($cuisine, $keyword_lower) !== false;
                   });
        });
    }
    
    return array_values($base_restaurants); // Reset array keys
}

function geocodeLocation($location) {
    // Demo coordinates for common locations
    $demo_locations = [
        'dallas' => ['latitude' => 32.7767, 'longitude' => -96.7970],
        'texas' => ['latitude' => 31.9686, 'longitude' => -99.9018],
        'houston' => ['latitude' => 29.7604, 'longitude' => -95.3698],
        'austin' => ['latitude' => 30.2672, 'longitude' => -97.7431],
        'new york' => ['latitude' => 40.7128, 'longitude' => -74.0060],
        'los angeles' => ['latitude' => 34.0522, 'longitude' => -118.2437],
        'chicago' => ['latitude' => 41.8781, 'longitude' => -87.6298],
        'miami' => ['latitude' => 25.7617, 'longitude' => -80.1918]
    ];
    
    $location_lower = strtolower(trim($location));
    
    // Check for exact matches first
    if (isset($demo_locations[$location_lower])) {
        return $demo_locations[$location_lower];
    }
    
    // Check for partial matches
    foreach ($demo_locations as $city => $coords) {
        if (strpos($location_lower, $city) !== false) {
            return $coords;
        }
    }
    
    // Default to Dallas coordinates
    return ['latitude' => 32.7767, 'longitude' => -96.7970];
}
?>