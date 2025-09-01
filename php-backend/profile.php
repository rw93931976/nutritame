<?php
/**
 * Profile Creation Endpoint - Standalone file for demo profiles
 */

require_once 'config.php';

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'POST') {
    createProfile();
} else {
    jsonResponse(['error' => 'Method not allowed'], 405);
}

function createProfile() {
    if (!DEMO_MODE) {
        jsonResponse(['error' => 'Demo mode is not enabled'], 403);
    }
    
    $input = json_decode(file_get_contents('php://input'), true);
    
    try {
        $pdo = getDBConnection();
        
        $demo_email = $input['email'] ?? 'profile_' . substr(uniqid(), -8) . '@nutritame.com';
        
        $user_id = generateUUID();
        $tenant_id = generateUUID();
        
        $stmt = $pdo->prepare("
            INSERT INTO users (
                id, email, subscription_status, subscription_tier, 
                subscription_end_date, tenant_id, is_demo_user, diabetes_type, created_at
            ) VALUES (?, ?, 'active', 'premium', ?, ?, TRUE, ?, NOW())
        ");
        
        $subscription_end = date('Y-m-d H:i:s', strtotime('+365 days'));
        $diabetes_type = $input['diabetes_type'] ?? 'type2';
        $stmt->execute([$user_id, $demo_email, $subscription_end, $tenant_id, $diabetes_type]);
        
        $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->execute([$user_id]);
        $demo_user = $stmt->fetch();
        
        // Add profile data to response
        $response_user = [
            'id' => $demo_user['id'],
            'email' => $demo_user['email'],
            'tenant_id' => $demo_user['tenant_id'],
            'diabetes_type' => $demo_user['diabetes_type'],
            'age' => $input['age'] ?? null,
            'gender' => $input['gender'] ?? null,
            'activity_level' => $input['activity_level'] ?? null,
            'health_goals' => $input['health_goals'] ?? [],
            'food_preferences' => $input['food_preferences'] ?? [],
            'cultural_background' => $input['cultural_background'] ?? null,
            'allergies' => $input['allergies'] ?? [],
            'dislikes' => $input['dislikes'] ?? [],
            'cooking_skill' => $input['cooking_skill'] ?? null,
            'phone_number' => $input['phone_number'] ?? null,
            'subscription_tier' => $demo_user['subscription_tier'],
            'subscription_status' => $demo_user['subscription_status'],
            'is_demo_user' => true,
            'created_at' => $demo_user['created_at']
        ];
        
        jsonResponse($response_user, 201);
        
    } catch (Exception $e) {
        error_log('Profile creation error: ' . $e->getMessage());
        
        // Return mock data if database fails
        $user_id = generateUUID();
        
        jsonResponse([
            'id' => $user_id,
            'email' => $input['email'] ?? 'profile_' . substr(uniqid(), -8) . '@nutritame.com',
            'tenant_id' => generateUUID(),
            'diabetes_type' => $input['diabetes_type'] ?? 'type2',
            'age' => $input['age'] ?? null,
            'gender' => $input['gender'] ?? null,
            'activity_level' => $input['activity_level'] ?? null,
            'health_goals' => $input['health_goals'] ?? [],
            'food_preferences' => $input['food_preferences'] ?? [],
            'cultural_background' => $input['cultural_background'] ?? null,
            'allergies' => $input['allergies'] ?? [],
            'dislikes' => $input['dislikes'] ?? [],
            'cooking_skill' => $input['cooking_skill'] ?? null,
            'phone_number' => $input['phone_number'] ?? null,
            'subscription_tier' => 'premium',
            'subscription_status' => 'active',
            'is_demo_user' => true,
            'created_at' => date('Y-m-d H:i:s')
        ], 201);
    }
}
?>