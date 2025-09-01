<?php
/**
 * User Profile API Endpoints - Direct routing for React frontend
 */

require_once '../config.php';

$method = $_SERVER['REQUEST_METHOD'];

// Get user ID from URL if present (e.g., /api/users/123)
$user_id = null;
$request_uri = $_SERVER['REQUEST_URI'];
if (preg_match('/\/users\/([a-zA-Z0-9\-]+)/', $request_uri, $matches)) {
    $user_id = $matches[1];
}

switch ($method) {
    case 'POST':
        if (!$user_id) {
            createUserProfile();
        } else {
            jsonResponse(['error' => 'Method not allowed'], 405);
        }
        break;
    case 'GET':
        if ($user_id) {
            getUserProfile($user_id);
        } else {
            listUserProfiles();
        }
        break;
    case 'PUT':
        if ($user_id) {
            updateUserProfile($user_id);
        } else {
            jsonResponse(['error' => 'User ID required'], 400);
        }
        break;
    default:
        jsonResponse(['error' => 'Method not allowed'], 405);
}

function createUserProfile() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    // Debug logging
    error_log('Create profile input: ' . json_encode($input));
    
    try {
        $pdo = getDBConnection();
        
function createUserProfile() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    // Debug logging
    error_log('Create profile input: ' . json_encode($input));
    
    try {
        $pdo = getDBConnection();
        
function createUserProfile() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    // Debug logging
    error_log('Create profile input: ' . json_encode($input));
    
    try {
        $pdo = getDBConnection();
        
function createUserProfile() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!DEMO_MODE) {
        jsonResponse(['error' => 'Demo mode is not enabled'], 403);
    }
    
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
        
        // Return the user in the expected format
        $user = formatUserResponse($demo_user);
        
        jsonResponse($user, 201);
        
    } catch (Exception $e) {
        error_log('Create user error: ' . $e->getMessage());
        error_log('Stack trace: ' . $e->getTraceAsString());
        jsonResponse(['error' => 'Failed to create user profile', 'details' => $e->getMessage()], 500);
    }
}

function getUserProfile($user_id) {
    try {
        $pdo = getDBConnection();
        
        $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->execute([$user_id]);
        $user = $stmt->fetch();
        
        if (!$user) {
            jsonResponse(['error' => 'User not found'], 404);
        }
        
        $user = formatUserResponse($user);
        
        jsonResponse($user);
        
    } catch (Exception $e) {
        error_log('Get user error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to get user profile'], 500);
    }
}

function updateUserProfile($user_id) {
    try {
        $pdo = getDBConnection();
        
        $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->execute([$user_id]);
        $existing_user = $stmt->fetch();
        
        if (!$existing_user) {
            jsonResponse(['error' => 'User not found'], 404);
        }
        
        $input = json_decode(file_get_contents('php://input'), true);
        
        $update_fields = [];
        $update_values = [];
        
        $allowed_fields = [
            'diabetes_type', 'age', 'gender', 'activity_level', 'cultural_background',
            'cooking_skill', 'phone_number'
        ];
        
        $json_fields = ['health_goals', 'food_preferences', 'allergies', 'dislikes'];
        
        foreach ($allowed_fields as $field) {
            if (isset($input[$field])) {
                $update_fields[] = "$field = ?";
                $update_values[] = $input[$field];
            }
        }
        
        foreach ($json_fields as $field) {
            if (isset($input[$field])) {
                $update_fields[] = "$field = ?";
                $update_values[] = json_encode($input[$field]);
            }
        }
        
        if (empty($update_fields)) {
            jsonResponse(['error' => 'No valid fields to update'], 400);
        }
        
        $update_fields[] = "updated_at = NOW()";
        $update_values[] = $user_id;
        
        $query = "UPDATE users SET " . implode(', ', $update_fields) . " WHERE id = ?";
        $stmt = $pdo->prepare($query);
        $stmt->execute($update_values);
        
        $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->execute([$user_id]);
        $user = $stmt->fetch();
        
        $user = formatUserResponse($user);
        
        jsonResponse($user);
        
    } catch (Exception $e) {
        error_log('Update user error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to update user profile'], 500);
    }
}

function listUserProfiles() {
    try {
        $pdo = getDBConnection();
        
        $stmt = $pdo->prepare("SELECT * FROM users ORDER BY created_at DESC LIMIT 100");
        $stmt->execute();
        $users = $stmt->fetchAll();
        
        $formatted_users = array_map('formatUserResponse', $users);
        
        jsonResponse($formatted_users);
        
    } catch (Exception $e) {
        error_log('List users error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to list user profiles'], 500);
    }
}

function formatUserResponse($user) {
    if (!$user) return null;
    
    $json_fields = ['health_goals', 'food_preferences', 'allergies', 'dislikes'];
    foreach ($json_fields as $field) {
        if ($user[$field]) {
            $user[$field] = json_decode($user[$field], true);
        } else {
            $user[$field] = [];
        }
    }
    
    return $user;
}
?>