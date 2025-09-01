<?php
/**
 * Demo Profile Creation Endpoint - Direct file like demo-config.php
 */

require_once 'config.php';

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'POST') {
    createDemoProfile();
} else {
    jsonResponse(['error' => 'Method not allowed'], 405);
}

function createDemoProfile() {
    if (!DEMO_MODE) {
        jsonResponse(['error' => 'Demo mode is not enabled'], 403);
    }
    
    $input = json_decode(file_get_contents('php://input'), true);
    
    try {
        $pdo = getDBConnection();
        
        // Create a new demo profile user
        $user_id = generateUUID();
        $tenant_id = generateUUID();
        
        $email = $input['email'] ?? 'profile_' . substr(uniqid(), -8) . '@nutritame.com';
        $diabetes_type = $input['diabetes_type'] ?? 'type2';
        $age = $input['age'] ?? null;
        $gender = $input['gender'] ?? null;
        $activity_level = $input['activity_level'] ?? null;
        $health_goals = isset($input['health_goals']) ? json_encode($input['health_goals']) : null;
        $food_preferences = isset($input['food_preferences']) ? json_encode($input['food_preferences']) : null;
        $cultural_background = $input['cultural_background'] ?? null;
        $allergies = isset($input['allergies']) ? json_encode($input['allergies']) : null;
        $dislikes = isset($input['dislikes']) ? json_encode($input['dislikes']) : null;
        $cooking_skill = $input['cooking_skill'] ?? null;
        $phone_number = $input['phone_number'] ?? null;
        
        $stmt = $pdo->prepare("
            INSERT INTO users (
                id, email, tenant_id, diabetes_type, age, gender, activity_level,
                health_goals, food_preferences, cultural_background, allergies,
                dislikes, cooking_skill, phone_number, subscription_tier,
                subscription_status, subscription_end_date, is_demo_user, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'premium', 'active', ?, TRUE, NOW())
        ");
        
        $subscription_end = date('Y-m-d H:i:s', strtotime('+365 days'));
        $stmt->execute([
            $user_id, $email, $tenant_id, $diabetes_type, $age, $gender, 
            $activity_level, $health_goals, $food_preferences, $cultural_background,
            $allergies, $dislikes, $cooking_skill, $phone_number, $subscription_end
        ]);
        
        $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->execute([$user_id]);
        $user = $stmt->fetch();
        
        // Format JSON fields
        $json_fields = ['health_goals', 'food_preferences', 'allergies', 'dislikes'];
        foreach ($json_fields as $field) {
            if ($user[$field]) {
                $user[$field] = json_decode($user[$field], true);
            } else {
                $user[$field] = [];
            }
        }
        
        jsonResponse($user, 201);
        
    } catch (Exception $e) {
        error_log('Demo profile error: ' . $e->getMessage());
        
        // Return mock profile data if database fails
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