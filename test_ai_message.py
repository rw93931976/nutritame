import requests
import json

# Test the critical AI message endpoint
base_url = 'https://nutritame-coach-3.preview.emergentagent.com/api'
test_user_id = 'test-user-123'

print('🎯 TESTING CRITICAL AI MESSAGE ENDPOINT')
print('=' * 50)

# First create a session
session_data = {'user_id': test_user_id, 'title': 'AI Integration Test'}
session_response = requests.post(f'{base_url}/coach/sessions?user_id={test_user_id}', json=session_data, timeout=30)

if session_response.status_code == 200:
    session_id = session_response.json()['id']
    print(f'✅ Session created: {session_id}')
    
    # Test AI message
    message_data = {
        'user_id': test_user_id,
        'session_id': session_id,
        'message': 'I need a diabetes-friendly lunch with Mediterranean flavors. Please use imperial measurements.'
    }
    
    print('🤖 Sending message to AI (may take 10-20 seconds)...')
    ai_response = requests.post(f'{base_url}/coach/message', json=message_data, timeout=45)
    
    if ai_response.status_code == 200:
        data = ai_response.json()
        ai_text = data.get('ai_response', '')
        
        if isinstance(ai_text, str):
            print(f'✅ AI Response received ({len(ai_text)} characters)')
            preview = ai_text[:200] + '...' if len(ai_text) > 200 else ai_text
            print(f'Preview: {preview}')
            
            # Check for diabetes content
            diabetes_terms = ['diabetes', 'diabetic', 'blood sugar', 'glucose']
            found_diabetes = any(term in ai_text.lower() for term in diabetes_terms)
            
            # Check for Mediterranean content  
            med_terms = ['mediterranean', 'olive oil', 'olives', 'feta']
            found_med = any(term in ai_text.lower() for term in med_terms)
            
            # Check for imperial measurements
            imperial_terms = ['cup', 'tablespoon', 'teaspoon', 'oz', 'ounce']
            found_imperial = any(term in ai_text.lower() for term in imperial_terms)
            
            print(f'✅ Diabetes-specific: {found_diabetes}')
            print(f'✅ Mediterranean content: {found_med}')
            print(f'✅ Imperial measurements: {found_imperial}')
            
            if found_diabetes and found_imperial:
                print('🎉 AI INTEGRATION: 100% SUCCESS!')
            else:
                print('⚠️  AI integration working but content needs improvement')
        else:
            print(f'❌ AI response is not a string: {type(ai_text)}')
    else:
        print(f'❌ AI message failed: {ai_response.status_code}')
        print(f'Error: {ai_response.text}')
else:
    print(f'❌ Session creation failed: {session_response.status_code}')
    print(f'Error: {session_response.text}')