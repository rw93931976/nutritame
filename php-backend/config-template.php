<?php
/**
 * NutriTame PHP Backend Configuration Template
 * Copy this file to config.php and update with your Hostinger details
 */

// =====================================
// HOSTINGER DATABASE CONFIGURATION
// =====================================
// Get these from Hostinger control panel → MySQL Databases
define('DB_HOST', 'localhost');
define('DB_NAME', 'u123456789_nutritame');    // REPLACE: Your Hostinger DB name
define('DB_USER', 'u123456789_nutritame');    // REPLACE: Your Hostinger DB user
define('DB_PASS', 'YOUR_DB_PASSWORD_HERE');   // REPLACE: Your strong database password

// =====================================
// DOMAIN CONFIGURATION  
// =====================================
// REPLACE with your actual domain
define('API_BASE_URL', 'https://app.nutritame.com/api');
define('CORS_ORIGIN', 'https://app.nutritame.com');

// =====================================
// DEMO MODE SETTINGS
// =====================================
define('DEMO_MODE', true);
define('LAUNCH_DATE', '2025-10-01');

// =====================================
// API KEYS (Add your real keys here)
// =====================================
// Get Emergent LLM key from your Emergent profile → Universal Key
define('EMERGENT_LLM_KEY', 'your_emergent_llm_key_here');

// Optional: Google Places API (for real restaurant data)
// Get from Google Cloud Console → Enable Places API  
define('GOOGLE_PLACES_API_KEY', 'your_google_places_api_key_here');

// Optional: USDA Nutrition API (for detailed nutrition data)
define('USDA_API_KEY', 'your_usda_api_key_here');

// =====================================
// JWT SECURITY CONFIGURATION
// =====================================
// Generate a random 64-character string for JWT_SECRET
// Use: openssl rand -base64 64
define('JWT_SECRET', 'REPLACE_WITH_64_CHARACTER_RANDOM_STRING');
define('JWT_ALGORITHM', 'HS256');
define('JWT_EXPIRY', 86400); // 24 hours

// =====================================
// CORS HEADERS (Auto-configured)
// =====================================
header('Access-Control-Allow-Origin: ' . CORS_ORIGIN);
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
header('Access-Control-Allow-Credentials: true');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// =====================================
// DATABASE CONNECTION FUNCTION
// =====================================
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

// =====================================
// UTILITY FUNCTIONS
// =====================================
function jsonResponse($data, $status = 200) {
    http_response_code($status);
    header('Content-Type: application/json');
    echo json_encode($data);
    exit();
}

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

// =====================================
// JWT HELPER FUNCTIONS
// =====================================
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

function getCurrentUser() {
    $headers = getallheaders();
    $authHeader = $headers['Authorization'] ?? '';
    
    if (!preg_match('/Bearer\s+(.*)$/i', $authHeader, $matches)) {
        return null;
    }
    
    $token = $matches[1];
    return verifyJWT($token);
}

// =====================================
// ERROR HANDLER
// =====================================
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