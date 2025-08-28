<?php
/**
 * Restaurant Search API Endpoints
 */

require_once '../config.php';

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    searchRestaurants();
} else {
    jsonResponse(['error' => 'Method not allowed'], 405);
}

function searchRestaurants() {
    $location = $_GET['location'] ?? '';
    $cuisine = $_GET['cuisine'] ?? '';
    
    if (empty($location)) {
        jsonResponse(['error' => 'Location is required'], 400);
    }
    
    try {
        $pdo = getDBConnection();
        
        // Check cache first
        $stmt = $pdo->prepare("
            SELECT * FROM restaurants 
            WHERE address LIKE ? 
            AND cached_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
            LIMIT 20
        ");
        $stmt->execute(["%$location%"]);
        $cached_results = $stmt->fetchAll();
        
        if (!empty($cached_results)) {
            jsonResponse(['restaurants' => $cached_results]);
            return;
        }
        
        // Simulate Google Places API call
        $restaurants = simulateGooglePlacesSearch($location, $cuisine);
        
        // Cache results
        foreach ($restaurants as $restaurant) {
            $stmt = $pdo->prepare("
                INSERT IGNORE INTO restaurants (
                    id, place_id, name, address, latitude, longitude, 
                    rating, price_level, phone_number, website, 
                    opening_hours, photos, cuisine_types, diabetic_friendly_score, cached_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())
            ");
            $stmt->execute([
                generateUUID(),
                $restaurant['place_id'],
                $restaurant['name'],
                $restaurant['address'],
                $restaurant['latitude'],
                $restaurant['longitude'],
                $restaurant['rating'],
                $restaurant['price_level'],
                $restaurant['phone_number'],
                $restaurant['website'],
                json_encode($restaurant['opening_hours']),
                json_encode($restaurant['photos']),
                json_encode($restaurant['cuisine_types']),
                $restaurant['diabetic_friendly_score']
            ]);
        }
        
        jsonResponse(['restaurants' => $restaurants]);
        
    } catch (Exception $e) {
        error_log('Restaurant search error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to search restaurants'], 500);
    }
}

function simulateGooglePlacesSearch($location, $cuisine = '') {
    // Simulate restaurant search results
    return [
        [
            'place_id' => 'demo_place_1',
            'name' => 'Healthy Bites Cafe',
            'address' => '123 Main St, ' . $location,
            'latitude' => 40.7128,
            'longitude' => -74.0060,
            'rating' => 4.5,
            'price_level' => 2,
            'phone_number' => '(555) 123-4567',
            'website' => 'https://healthybites.com',
            'opening_hours' => ['Mon-Fri: 8am-8pm', 'Sat-Sun: 9am-6pm'],
            'photos' => ['https://example.com/photo1.jpg'],
            'cuisine_types' => ['healthy', 'american'],
            'diabetic_friendly_score' => 4.2
        ],
        [
            'place_id' => 'demo_place_2',
            'name' => 'Fresh Garden Restaurant',
            'address' => '456 Oak Ave, ' . $location,
            'latitude' => 40.7589,
            'longitude' => -73.9851,
            'rating' => 4.3,
            'price_level' => 3,
            'phone_number' => '(555) 987-6543',
            'website' => 'https://freshgarden.com',
            'opening_hours' => ['Daily: 11am-10pm'],
            'photos' => ['https://example.com/photo2.jpg'],
            'cuisine_types' => ['mediterranean', 'vegetarian'],
            'diabetic_friendly_score' => 4.0
        ]
    ];
}
?>