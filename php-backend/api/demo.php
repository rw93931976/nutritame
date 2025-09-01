<?php
/**
 * Demo Mode API Endpoints
 */

require_once '../config.php';

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path_parts = explode('/', trim($path, '/'));

if (end($path_parts) === 'config') {
    if ($method === 'GET') {
        getDemoConfig();
    }
} elseif (end($path_parts) === 'access') {
    if ($method === 'POST') {
        createDemoAccess();
    }
} elseif (end($path_parts) === 'profile') {
    if ($method === 'POST') {
        createDemoProfile();
    }
} else {
    jsonResponse(['error' => 'Not found'], 404);
}

function getDemoConfig() {
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
        
        $demo_email = $provided_email ?: 'demo_' . substr(uniqid(), -8) . '@demo.nutritame.com';
        
        $user_id = generateUUID();
        $tenant_id = generateUUID();
        
        $stmt = $pdo->prepare("
            INSERT INTO users (
                id, email, subscription_status, subscription_tier, 
                subscription_end_date, tenant_id, is_demo_user, created_at
            ) VALUES (?, ?, 'active', 'premium', ?, ?, TRUE, NOW())
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
            'user' => $demo_user,
            'expires_at' => date('Y-m-d\TH:i:s\Z', time() + JWT_EXPIRY),
            'demo_notice' => 'This is a demo account with full premium access.',
            'launch_date' => LAUNCH_DATE
        ]);
        
    } catch (Exception $e) {
        error_log('Demo access error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to create demo access'], 500);
    }
}
?>