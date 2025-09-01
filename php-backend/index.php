<?php
/**
 * NutriTame PHP Backend Main Router
 * Handles all API requests and routes them to appropriate endpoints
 */

require_once 'config.php';

// Get the request path and method
$request_uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

// Remove /api prefix if present
$path = preg_replace('#^/api#', '', $request_uri);
$path = trim($path, '/');
$path_parts = explode('/', $path);

// Route to appropriate handler
try {
    switch ($path_parts[0]) {
        case 'demo':
            if ($path_parts[1] === 'config' || $path_parts[1] === 'access' || $path_parts[1] === 'profile') {
                include 'api/demo.php';
            } else {
                jsonResponse(['error' => 'Demo endpoint not found'], 404);
            }
            break;
            
        case 'users':
            include 'api/users.php';
            break;
            
        case 'chat':
            include 'api/chat.php';
            break;
            
        case 'restaurants':
            include 'api/restaurants.php';
            break;
            
        case 'nutrition':
            include 'api/nutrition.php';
            break;
            
        case 'shopping-lists':
            include 'api/shopping_lists.php';
            break;
            
        case 'auth':
            include 'api/auth.php';
            break;
            
        case 'health':
            // Health check endpoint
            jsonResponse(['status' => 'OK', 'timestamp' => date('Y-m-d H:i:s')]);
            break;
            
        case '':
            // Root endpoint - API info
            jsonResponse([
                'name' => 'NutriTame API',
                'version' => '1.0.0',
                'status' => 'running',
                'demo_mode' => DEMO_MODE,
                'endpoints' => [
                    '/api/demo/config',
                    '/api/demo/access', 
                    '/api/users',
                    '/api/chat',
                    '/api/restaurants',
                    '/api/nutrition',
                    '/api/auth'
                ]
            ]);
            break;
            
        default:
            jsonResponse(['error' => 'API endpoint not found', 'requested_path' => $path], 404);
    }
    
} catch (Exception $e) {
    error_log('API Error: ' . $e->getMessage());
    jsonResponse(['error' => 'Internal server error'], 500);
}
?>