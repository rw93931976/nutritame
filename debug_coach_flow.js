// Debug script to test AI Health Coach flow
// Run in browser console to debug the issues

console.log('🔍 AI Health Coach Debug Test Starting...');

// 1. Check localStorage state
console.log('📦 localStorage state:');
console.log('- nt_coach_disclaimer_ack:', localStorage.getItem('nt_coach_disclaimer_ack'));
console.log('- nt_coach_pending_question:', localStorage.getItem('nt_coach_pending_question'));

// 2. Check if we're on the right page
console.log('🌐 Current location:', window.location.href);

// 3. Check if coach interface elements exist
const inputField = document.querySelector('input[placeholder*="nutrition"]');
const sendButton = document.querySelector('button[aria-label="Send message"]');
const disclaimerModal = document.querySelector('div:has-text("AI Health Coach Disclaimer")');

console.log('🎯 UI Elements found:');
console.log('- Input field:', !!inputField);
console.log('- Send button:', !!sendButton);
console.log('- Disclaimer modal visible:', !!disclaimerModal);

// 4. Test input field functionality
if (inputField) {
  console.log('📝 Testing input field...');
  inputField.value = 'Test question for debugging';
  inputField.dispatchEvent(new Event('input', { bubbles: true }));
  
  setTimeout(() => {
    console.log('- Input value after change:', inputField.value);
    console.log('- localStorage after typing:', localStorage.getItem('nt_coach_pending_question'));
  }, 100);
}

// 5. Check app mode and user state
console.log('🏗️ App state (if available):');
try {
  const appElement = document.querySelector('#root');
  if (appElement && appElement._reactInternalInstance) {
    console.log('- React component tree available');
  }
} catch (e) {
  console.log('- Cannot access React state:', e.message);
}

// 6. Test backend connectivity
console.log('🌐 Testing backend connectivity...');
fetch('/api/coach/feature-flags')
  .then(response => {
    console.log('- Backend status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('- Feature flags:', data);
  })
  .catch(error => {
    console.log('- Backend error:', error.message);
  });

console.log('🔍 Debug test complete. Check results above.');