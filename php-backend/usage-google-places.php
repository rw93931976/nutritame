<?php
/**
 * Google Places API Usage Monitor - Direct routing for React frontend
 */

require_once 'config.php';

$method = $_SERVER['REQUEST_METHOD'];

if ($method !== 'GET') {
    jsonResponse(['error' => 'Method not allowed'], 405);
    exit;
}

try {
    // Demo usage statistics
    $usage_data = [
        'monthly_limit' => 2000,
        'calls_made' => 150,
        'calls_remaining' => 1850,
        'percentage_used' => 7.5,
        'status' => 'low_usage',
        'reset_date' => date('Y-m-d', strtotime('first day of next month')),
        'current_period_start' => date('Y-m-01'),
        'current_period_end' => date('Y-m-t')
    ];
    
    jsonResponse($usage_data);
    
} catch (Exception $e) {
    error_log('Usage monitoring error: ' . $e->getMessage());
    jsonResponse(['error' => 'Failed to get usage statistics'], 500);
}
?>