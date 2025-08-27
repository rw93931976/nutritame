<?php
/**
 * AI Health Coach Chat API Endpoints
 * Converted from FastAPI chat endpoints
 */

require_once '../config.php';

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Route handling
if (strpos($path, '/chat') !== false) {
    if ($method === 'POST') {
        sendChatMessage();
    } elseif ($method === 'GET') {
        getChatHistory();
    }
} else {
    jsonResponse(['error' => 'Not found'], 404);
}

function sendChatMessage() {
    // Get current user from token
    $current_user = getCurrentUser();
    if (!$current_user) {
        jsonResponse(['error' => 'Authentication required'], 401);
    }
    
    $input = json_decode(file_get_contents('php://input'), true);
    $user_message = $input['message'] ?? '';
    
    if (empty($user_message)) {
        jsonResponse(['error' => 'Message is required'], 400);
    }
    
    try {
        $pdo = getDBConnection();
        
        // Get user profile for context
        $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->execute([$current_user['user_id']]);
        $user = $stmt->fetch();
        
        if (!$user) {
            jsonResponse(['error' => 'User not found'], 404);
        }
        
        // Build user context
        $health_goals = $user['health_goals'] ? json_decode($user['health_goals'], true) : [];
        $food_preferences = $user['food_preferences'] ? json_decode($user['food_preferences'], true) : [];
        $allergies = $user['allergies'] ? json_decode($user['allergies'], true) : [];
        
        $user_context = "
User Profile:
- Age: " . ($user['age'] ?: 'Not specified') . "
- Gender: " . ($user['gender'] ?: 'Not specified') . "
- Diabetes Type: " . ($user['diabetes_type'] ?: 'Not specified') . "
- Activity Level: " . ($user['activity_level'] ?: 'Not specified') . "
- Health Goals: " . (empty($health_goals) ? 'Not specified' : implode(', ', $health_goals)) . "
- Food Preferences: " . (empty($food_preferences) ? 'Not specified' : implode(', ', $food_preferences)) . "
- Allergies: " . (empty($allergies) ? 'None specified' : implode(', ', $allergies)) . "
- Cooking Skill: " . ($user['cooking_skill'] ?: 'Not specified') . "
        ";
        
        // Health Coach Prompt (simplified version)
        $health_coach_prompt = "You are NutriTame's AI Health Coach, a specialized meal planning assistant for people with diabetes. 

Your role:
- Provide personalized meal planning and nutrition guidance
- Suggest diabetic-friendly recipes and food choices
- Help with carb counting and portion control
- Offer restaurant dining tips
- Create shopping lists for meal plans
- Always prioritize blood sugar management

Guidelines:
- Be encouraging and supportive
- Focus on practical, actionable advice
- Consider the user's diabetes type and preferences
- Suggest balanced meals with appropriate carb content
- Include cooking tips based on skill level
- Always remind users to consult healthcare providers for medical decisions

$user_context

User Message: $user_message";
        
        // Call AI service (using Emergent LLM integration)
        $ai_response = callEmergentLLM($health_coach_prompt);
        
        if (!$ai_response) {
            jsonResponse(['error' => 'AI service unavailable'], 503);
        }
        
        // Save chat message
        $message_id = generateUUID();
        $stmt = $pdo->prepare("
            INSERT INTO chat_messages (id, user_id, message, response, timestamp)
            VALUES (?, ?, ?, ?, NOW())
        ");
        $stmt->execute([$message_id, $current_user['user_id'], $user_message, $ai_response]);
        
        // Also save to chat sessions (for conversation history)
        $chat_data = [
            'user_message' => $user_message,
            'ai_response' => $ai_response,
            'timestamp' => date('Y-m-d\TH:i:s\Z')
        ];
        
        // Get or create chat session
        $stmt = $pdo->prepare("
            SELECT * FROM chat_sessions 
            WHERE user_id = ? AND tenant_id = ? 
            ORDER BY updated_at DESC LIMIT 1
        ");
        $stmt->execute([$current_user['user_id'], $current_user['tenant_id']]);
        $session = $stmt->fetch();
        
        if ($session) {
            // Update existing session
            $messages = json_decode($session['messages'], true) ?: [];
            $messages[] = $chat_data;
            
            $stmt = $pdo->prepare("
                UPDATE chat_sessions 
                SET messages = ?, updated_at = NOW() 
                WHERE id = ?
            ");
            $stmt->execute([json_encode($messages), $session['id']]);
        } else {
            // Create new session
            $session_id = generateUUID();
            $stmt = $pdo->prepare("
                INSERT INTO chat_sessions (id, user_id, tenant_id, title, messages, created_at)
                VALUES (?, ?, ?, 'Chat Session', ?, NOW())
            ");
            $stmt->execute([
                $session_id, 
                $current_user['user_id'], 
                $current_user['tenant_id'],
                json_encode([$chat_data])
            ]);
        }
        
        jsonResponse(['response' => $ai_response]);
        
    } catch (Exception $e) {
        error_log('Chat error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to process chat message'], 500);
    }
}

function getChatHistory() {
    // Get current user from token
    $current_user = getCurrentUser();
    if (!$current_user) {
        jsonResponse(['error' => 'Authentication required'], 401);
    }
    
    try {
        $pdo = getDBConnection();
        
        $stmt = $pdo->prepare("
            SELECT * FROM chat_messages 
            WHERE user_id = ? 
            ORDER BY timestamp ASC 
            LIMIT 100
        ");
        $stmt->execute([$current_user['user_id']]);
        $messages = $stmt->fetchAll();
        
        jsonResponse(['messages' => $messages]);
        
    } catch (Exception $e) {
        error_log('Chat history error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to get chat history'], 500);
    }
}

function callEmergentLLM($prompt) {
    $api_key = EMERGENT_LLM_KEY;
    if (!$api_key) {
        return "I'm sorry, the AI service is currently unavailable. Please check your Emergent LLM key configuration.";
    }
    
    // Simplified LLM call - you'll need to implement based on Emergent's API
    // This is a placeholder that returns a helpful response
    
    $curl = curl_init();
    
    curl_setopt_array($curl, [
        CURLOPT_URL => "https://api.emergentmind.com/v1/chat/completions", // Replace with actual Emergent API URL
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => "",
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
        CURLOPT_CUSTOMREQUEST => "POST",
        CURLOPT_POSTFIELDS => json_encode([
            "model" => "gpt-4o-mini",
            "messages" => [
                [
                    "role" => "user",
                    "content" => $prompt
                ]
            ],
            "max_tokens" => 1000,
            "temperature" => 0.7
        ]),
        CURLOPT_HTTPHEADER => [
            "Authorization: Bearer " . $api_key,
            "Content-Type: application/json"
        ],
    ]);
    
    $response = curl_exec($curl);
    $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
    curl_close($curl);
    
    if ($http_code === 200 && $response) {
        $data = json_decode($response, true);
        if (isset($data['choices'][0]['message']['content'])) {
            return $data['choices'][0]['message']['content'];
        }
    }
    
    // Fallback response if API fails
    return "Thank you for your message! I'm your AI Health Coach here to help with diabetic-friendly meal planning. I can assist with recipes, nutrition advice, carb counting, and creating shopping lists. How can I help you today with your meal planning goals?";
}
?>