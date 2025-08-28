<?php
/**
 * Shopping Lists API Endpoints - Direct routing for React frontend
 */

require_once 'config.php';

$method = $_SERVER['REQUEST_METHOD'];
$request_uri = $_SERVER['REQUEST_URI'];

// Parse user ID from URL (e.g., /shopping-lists/123)
$user_id = null;
if (preg_match('/\/shopping-lists\/([a-zA-Z0-9\-]+)/', $request_uri, $matches)) {
    $user_id = $matches[1];
}

// Parse list ID for updates (e.g., /shopping-lists/update/123)
$list_id = null;
if (preg_match('/\/shopping-lists\/update\/([a-zA-Z0-9\-]+)/', $request_uri, $matches)) {
    $list_id = $matches[1];
}

try {
    switch ($method) {
        case 'GET':
            if ($user_id) {
                getShoppingLists($user_id);
            } else {
                jsonResponse(['error' => 'User ID required'], 400);
            }
            break;
        case 'POST':
            if (strpos($request_uri, '/generate') !== false) {
                generateShoppingList();
            } else {
                jsonResponse(['error' => 'Invalid endpoint'], 404);
            }
            break;
        case 'PUT':
            if ($list_id) {
                updateShoppingList($list_id);
            } else {
                jsonResponse(['error' => 'List ID required'], 400);
            }
            break;
        default:
            jsonResponse(['error' => 'Method not allowed'], 405);
    }
} catch (Exception $e) {
    error_log('Shopping List API error: ' . $e->getMessage());
    jsonResponse(['error' => 'Internal server error'], 500);
}

function getShoppingLists($user_id) {
    try {
        $pdo = getDBConnection();
        
        $stmt = $pdo->prepare("
            SELECT * FROM shopping_lists 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ");
        $stmt->execute([$user_id]);
        $lists = $stmt->fetchAll();
        
        // Parse JSON items for each list
        foreach ($lists as &$list) {
            $list['items'] = json_decode($list['items'], true) ?: [];
        }
        
        jsonResponse($lists);
        
    } catch (Exception $e) {
        error_log('Get shopping lists error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to get shopping lists'], 500);
    }
}

function generateShoppingList() {
    $input = json_decode(file_get_contents('php://input'), true);
    $user_id = $input['user_id'] ?? '';
    $meal_plan_text = $input['meal_plan_text'] ?? '';
    
    if (!$user_id || !$meal_plan_text) {
        jsonResponse(['error' => 'User ID and meal plan text required'], 400);
    }
    
    try {
        // Generate shopping list from meal plan (simplified for demo)
        $items = generateShoppingItemsFromMealPlan($meal_plan_text);
        
        $pdo = getDBConnection();
        
        $list_id = generateUUID();
        $title = 'Shopping List - ' . date('M j, Y');
        
        $stmt = $pdo->prepare("
            INSERT INTO shopping_lists (id, user_id, title, items, created_at)
            VALUES (?, ?, ?, ?, NOW())
        ");
        $stmt->execute([$list_id, $user_id, $title, json_encode($items)]);
        
        $list = [
            'id' => $list_id,
            'title' => $title,
            'items' => $items,
            'created_at' => date('Y-m-d H:i:s')
        ];
        
        jsonResponse($list, 201);
        
    } catch (Exception $e) {
        error_log('Generate shopping list error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to generate shopping list'], 500);
    }
}

function updateShoppingList($list_id) {
    $input = json_decode(file_get_contents('php://input'), true);
    $items = $input['items'] ?? [];
    
    try {
        $pdo = getDBConnection();
        
        $stmt = $pdo->prepare("
            UPDATE shopping_lists 
            SET items = ?, updated_at = NOW()
            WHERE id = ?
        ");
        $stmt->execute([json_encode($items), $list_id]);
        
        if ($stmt->rowCount() === 0) {
            jsonResponse(['error' => 'Shopping list not found'], 404);
        }
        
        jsonResponse(['success' => true]);
        
    } catch (Exception $e) {
        error_log('Update shopping list error: ' . $e->getMessage());
        jsonResponse(['error' => 'Failed to update shopping list'], 500);
    }
}

function generateShoppingItemsFromMealPlan($meal_plan_text) {
    // Simple demo implementation - parse ingredients from meal plan
    $items = [];
    
    // Basic ingredient detection (simplified for demo)
    $common_ingredients = [
        'produce' => ['spinach', 'tomatoes', 'onions', 'garlic', 'bell peppers', 'broccoli', 'carrots', 'lettuce'],
        'proteins' => ['chicken breast', 'salmon', 'eggs', 'tofu', 'greek yogurt', 'cottage cheese'],
        'pantry' => ['olive oil', 'quinoa', 'brown rice', 'whole wheat bread', 'almonds', 'chia seeds'],
        'frozen' => ['frozen berries', 'frozen vegetables']
    ];
    
    $meal_plan_lower = strtolower($meal_plan_text);
    
    foreach ($common_ingredients as $category => $ingredients) {
        foreach ($ingredients as $ingredient) {
            if (strpos($meal_plan_lower, $ingredient) !== false) {
                $items[] = [
                    'item' => ucfirst($ingredient),
                    'category' => $category,
                    'quantity' => '1 lb',
                    'checked' => false
                ];
            }
        }
    }
    
    // If no items found, add some default healthy items
    if (empty($items)) {
        $items = [
            ['item' => 'Mixed greens', 'category' => 'produce', 'quantity' => '1 bag', 'checked' => false],
            ['item' => 'Chicken breast', 'category' => 'proteins', 'quantity' => '2 lbs', 'checked' => false],
            ['item' => 'Brown rice', 'category' => 'pantry', 'quantity' => '1 bag', 'checked' => false],
            ['item' => 'Olive oil', 'category' => 'pantry', 'quantity' => '1 bottle', 'checked' => false]
        ];
    }
    
    return $items;
}
?>