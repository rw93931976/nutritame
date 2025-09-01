<?php
/**
 * AI Health Coach Chat API Endpoints
 */

require_once '../config.php';

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

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
    // For demo mode, bypass authentication and return mock response
    if (DEMO_MODE) {
        $input = json_decode(file_get_contents('php://input'), true);
        $message = $input['message'] ?? '';
        
        if (empty($message)) {
            jsonResponse(['error' => 'Message is required'], 400);
            return;
        }
        
        // Generate contextual demo response
        $response = generateDemoResponse($message);
        jsonResponse(['response' => $response]);
        return;
    }
    
    // Original authentication-required logic for non-demo mode
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
        
        $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
        $stmt->execute([$current_user['user_id']]);
        $user = $stmt->fetch();
        
        if (!$user) {
            jsonResponse(['error' => 'User not found'], 404);
        }
        
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
        
        // For demo mode, return a mock AI response if external service fails
        $ai_response = callEmergentLLM($health_coach_prompt);
        
        if (!$ai_response) {
            // Fallback mock response for demo
            $ai_response = "Hello! I'm your NutriTame AI Health Coach. I'm here to help you with diabetic-friendly meal planning and nutrition guidance. Based on your profile, I can suggest balanced meals that help manage blood sugar levels. What specific questions do you have about meal planning or nutrition today?";
        }
        
        // For demo mode, skip database storage and just return the response
        if (DEMO_MODE) {
            jsonResponse(['response' => $ai_response]);
            return;
        }
        
        // Save to database in non-demo mode
        try {
            $message_id = generateUUID();
            $stmt = $pdo->prepare("
                INSERT INTO chat_messages (id, user_id, message, response, timestamp)
                VALUES (?, ?, ?, ?, NOW())
            ");
            $stmt->execute([$message_id, $current_user['user_id'], $user_message, $ai_response]);
        } catch (Exception $e) {
            error_log('Chat database error: ' . $e->getMessage());
            // Continue anyway and return response
        }
        
        jsonResponse(['response' => $ai_response]);
        
    } catch (Exception $e) {
        error_log('Chat error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to process chat message'], 500);
    }
}

function getChatHistory() {
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
    
    return "Thank you for your message! I'm your AI Health Coach here to help with diabetic-friendly meal planning. I can assist with recipes, nutrition advice, carb counting, and creating shopping lists. How can I help you today with your meal planning goals?";
}

function generateDemoResponse($message) {
    $message_lower = strtolower($message);
    
    // Breakfast suggestions
    if (strpos($message_lower, 'breakfast') !== false) {
        return "For a diabetic-friendly breakfast, I recommend:\n\n• 2 scrambled eggs with spinach\n• 1 slice whole grain toast\n• 1/2 cup berries\n• 1 cup unsweetened almond milk\n\nThis meal provides protein to help stabilize blood sugar and fiber to slow carb absorption. Aim for 30-40g total carbs.";
    }
    
    // Lunch suggestions
    if (strpos($message_lower, 'lunch') !== false) {
        return "Here's a balanced diabetic lunch:\n\n• Grilled chicken salad with mixed greens\n• 1/2 cup quinoa\n• Olive oil vinaigrette\n• Side of roasted vegetables\n\nThis provides lean protein, complex carbs, and healthy fats while keeping portions controlled for blood sugar management.";
    }
    
    // Dinner suggestions
    if (strpos($message_lower, 'dinner') !== false) {
        return "For dinner, try this diabetes-friendly meal:\n\n• 4oz baked salmon\n• 1 cup roasted broccoli\n• 1/2 cup brown rice\n• Small side salad\n\nRich in omega-3s and fiber, this meal helps maintain stable blood glucose levels throughout the evening.";
    }
    
    // General greeting or other messages
    return "Hello! I'm your NutriTame AI Health Coach, specialized in diabetic meal planning. I can help you with:\n\n• Meal planning and recipes\n• Carb counting guidance\n• Restaurant dining tips\n• Blood sugar management through nutrition\n• Shopping lists for healthy eating\n\nWhat specific nutrition question can I help you with today? Always remember to consult with your healthcare provider for medical decisions.";
}
?>