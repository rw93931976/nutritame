// Manual QA Test Script for v2.2.5-ack-gate-fix-2
// Run this in browser console at http://localhost:3000/coach

console.log("🧪 Starting Manual QA Test for v2.2.5-ack-gate-fix-2");

// Step 1: Clear disclaimer state and reload
console.log("Step 1: Clearing disclaimer state...");
localStorage.removeItem('nt_coach_disclaimer_ack');
localStorage.removeItem('nt_coach_pending_question');
console.log("Disclaimer state cleared. Reloading page...");
location.reload();

// Note: After reload, run the next part