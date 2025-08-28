<?php
/**
 * Geocoding API Endpoint - Direct routing for React frontend
 */

require_once 'config.php';

$method = $_SERVER['REQUEST_METHOD'];

if ($method !== 'POST') {
    jsonResponse(['error' => 'Method not allowed'], 405);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
$location = $input['location'] ?? '';

if (empty($location)) {
    jsonResponse(['error' => 'Location is required'], 400);
    exit;
}

try {
    // Demo geocoding - in production, use Google Geocoding API
    $coordinates = geocodeLocation($location);
    jsonResponse($coordinates);
    
} catch (Exception $e) {
    error_log('Geocoding error: ' . $e->getMessage());
    jsonResponse(['error' => 'Failed to geocode location'], 500);
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
    
    // Default to Dallas coordinates with slight randomization
    return [
        'latitude' => 32.7767 + (rand(-100, 100) / 10000),
        'longitude' => -96.7970 + (rand(-100, 100) / 10000)
    ];
}
?>