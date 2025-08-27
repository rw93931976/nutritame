<?php
/**
 * NutriTame PHP Backend Configuration
 * Converted from FastAPI for Hostinger Business Hosting
 */

// Database Configuration
define('DB_HOST', 'localhost');
define('DB_NAME', 'u123456789_nutritame'); // Replace with your Hostinger DB name
define('DB_USER', 'u123456789_nutritame'); // Replace with your Hostinger DB user
define('DB_PASS', 'your_password_here');   // Replace with your Hostinger DB password

// API Configuration
define('API_BASE_URL', 'https://app.yoursite.com/api'); // Replace with your domain
define('CORS_ORIGIN', 'https://app.yoursite.com');     // Replace with your domain

// Demo Mode Configuration
define('DEMO_MODE', true);
define('LAUNCH_DATE', '2025-10-01');

// External API Keys (add your actual keys)
define('EMERGENT_LLM_KEY', 'your_emergent_llm_key_here');
define('GOOGLE_PLACES_API_KEY', 'your_google_places_key_here');
define('USDA_API_KEY', 'your_usda_api_key_here');

// JWT Configuration
define('JWT_SECRET', 'your_jwt_secret_key_here_make_it_long_and_random');
define('JWT_ALGORITHM', 'HS256');
define('JWT_EXPIRY', 86400); // 24 hours

// CORS Headers
header('Access-Control-Allow-Origin: ' . CORS_ORIGIN);
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Access-Control-Allow-Credentials: true');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Database Connection Function
function getDBConnection() {
    try {
        $pdo = new PDO(
            "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8mb4",
            DB_USER,
            DB_PASS,
            [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false,
            ]
        );
        return $pdo;
    } catch (PDOException $e) {
        http_response_code(500);
        echo json_encode(['error' => 'Database connection failed']);
        exit();
    }
}

// JSON Response Helper
function jsonResponse($data, $status = 200) {
    http_response_code($status);
    header('Content-Type: application/json');
    echo json_encode($data);
    exit();
}

// Generate UUID Helper
function generateUUID() {
    return sprintf(
        '%04x%04x-%04x-%04x-%04x-%04x%04x%04x',
        mt_rand(0, 0xffff), mt_rand(0, 0xffff),
        mt_rand(0, 0xffff),
        mt_rand(0, 0x0fff) | 0x4000,
        mt_rand(0, 0x3fff) | 0x8000,
        mt_rand(0, 0xffff), mt_rand(0, 0xffff), mt_rand(0, 0xffff)
    );
}

// JWT Helper Functions
function generateJWT($user_id, $tenant_id = null) {
    $header = json_encode(['typ' => 'JWT', 'alg' => JWT_ALGORITHM]);
    $payload = json_encode([
        'user_id' => $user_id,
        'tenant_id' => $tenant_id,
        'exp' => time() + JWT_EXPIRY,
        'iat' => time()
    ]);
    
    $headerEncoded = str_replace(['+', '/', '='], ['-', '_', ''], base64_encode($header));
    $payloadEncoded = str_replace(['+', '/', '='], ['-', '_', ''], base64_encode($payload));
    
    $signature = hash_hmac('sha256', $headerEncoded . "." . $payloadEncoded, JWT_SECRET, true);
    $signatureEncoded = str_replace(['+', '/', '='], ['-', '_', ''], base64_encode($signature));
    
    return $headerEncoded . "." . $payloadEncoded . "." . $signatureEncoded;
}

function verifyJWT($token) {
    $parts = explode('.', $token);
    if (count($parts) !== 3) {
        return false;
    }
    
    $header = $parts[0];
    $payload = $parts[1];
    $signature = $parts[2];
    
    $expectedSignature = hash_hmac('sha256', $header . "." . $payload, JWT_SECRET, true);
    $expectedSignatureEncoded = str_replace(['+', '/', '='], ['-', '_', ''], base64_encode($expectedSignature));
    
    if ($signature !== $expectedSignatureEncoded) {
        return false;
    }
    
    $payloadData = json_decode(base64_decode(str_replace(['-', '_'], ['+', '/'], $payload)), true);
    
    if ($payloadData['exp'] < time()) {
        return false; // Token expired
    }
    
    return $payloadData;
}

// Get current user from Authorization header
function getCurrentUser() {
    $headers = getallheaders();
    $authHeader = $headers['Authorization'] ?? '';
    
    if (!preg_match('/Bearer\s+(.*)$/i', $authHeader, $matches)) {
        return null;
    }
    
    $token = $matches[1];
    return verifyJWT($token);
}

// Error handler
set_error_handler(function($severity, $message, $file, $line) {
    if (!(error_reporting() & $severity)) {
        return;
    }
    
    error_log("PHP Error: $message in $file on line $line");
    
    if (!headers_sent()) {
        jsonResponse(['error' => 'Internal server error'], 500);
    }
});

?>