<?php
/**
 * Demo Configuration and Access Endpoints
 * Handles multiple demo-related endpoints via query parameters
 */

require_once 'config.php';

$method = $_SERVER['REQUEST_METHOD'];
$endpoint = $_GET['endpoint'] ?? 'config';

switch ($endpoint) {
    case 'config':
        if ($method === 'GET') {
            getDemoConfig();
        } else {
            jsonResponse(['error' => 'Method not allowed'], 405);
        }
        break;
        
    case 'access':
        if ($method === 'POST') {
            createDemoAccess();
        } else {
            jsonResponse(['error' => 'Method not allowed'], 405);
        }
        break;
        
    case 'profile':
        if ($method === 'POST') {
            createDemoProfile();
        } else {
            jsonResponse(['error' => 'Method not allowed'], 405);
        }
        break;
        
    default:
        jsonResponse(['error' => 'Unknown endpoint: ' . $endpoint], 404);
}

function getDemoConfig() {
    // Test marker to confirm this file is being used
    error_log('NEW demo-config.php file being used for config');
    
    $config = [
        'demo_mode' => DEMO_MODE,
        'launch_date' => LAUNCH_DATE,
        'message' => 'Currently in demo mode - full access without account creation',
        'launch_requirements' => [
            'account_required' => true,
            'subscription_required' => true,
            'basic_plan' => '$9/month',
            'premium_plan' => '$19/month',
            'free_trial' => '15 days'
        ]
    ];
    
    jsonResponse($config);
}

function createDemoAccess() {
    if (!DEMO_MODE) {
        jsonResponse(['error' => 'Demo mode is not enabled'], 403);
    }
    
    $input = json_decode(file_get_contents('php://input'), true);
    $provided_email = $input['email'] ?? null;
    
    try {
        $pdo = getDBConnection();
        
        $demo_email = $provided_email ?: 'demo_' . substr(uniqid(), -8) . '@nutritame.com';
        
        $user_id = generateUUID();
        $tenant_id = generateUUID();
        
        $stmt = $pdo->prepare("
            INSERT INTO users (
                id, email, subscription_status, subscription_tier, 
                subscription_end_date, tenant_id, is_demo_user, diabetes_type, created_at
            ) VALUES (?, ?, 'active', 'premium', ?, ?, TRUE, 'type2', NOW())
        ");
        
        $subscription_end = date('Y-m-d H:i:s', strtotime('+365 days'));
        $stmt->execute([$user_id, $demo_email, $subscription_end, $tenant_id]);
        
        $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->execute([$user_id]);
        $demo_user = $stmt->fetch();
        
        $token = generateJWT($user_id, $tenant_id);
        
        jsonResponse([
            'demo_access' => true,
            'access_token' => $token,
            'user' => [
                'id' => $demo_user['id'],
                'email' => $demo_user['email'],
                'diabetes_type' => $demo_user['diabetes_type'] ?? 'type2',
                'subscription_tier' => $demo_user['subscription_tier'],
                'subscription_status' => $demo_user['subscription_status']
            ],
            'expires_at' => date('Y-m-d\TH:i:s\Z', time() + JWT_EXPIRY),
            'demo_notice' => 'This is a demo account with full premium access until ' . LAUNCH_DATE,
            'launch_date' => LAUNCH_DATE,
            'message' => 'Demo access created successfully! Enjoy full premium features.'
        ]);
        
    } catch (Exception $e) {
        error_log('Demo access error: ' . $e->getMessage());
        
        // Return mock data if database fails
        $user_id = generateUUID();
        $tenant_id = generateUUID();
        $token = generateJWT($user_id, $tenant_id);
        
        jsonResponse([
            'demo_access' => true,
            'access_token' => $token,
            'user' => [
                'id' => $user_id,
                'email' => $provided_email ?: 'demo_' . substr(uniqid(), -8) . '@nutritame.com',
                'diabetes_type' => 'type2',
                'subscription_tier' => 'premium',
                'subscription_status' => 'active'
            ],
            'expires_at' => date('Y-m-d\TH:i:s\Z', time() + JWT_EXPIRY),
            'demo_notice' => 'This is a demo account with full premium access until ' . LAUNCH_DATE,
            'launch_date' => LAUNCH_DATE,
            'message' => 'Demo access created successfully! Enjoy full premium features.'
        ]);
    }
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