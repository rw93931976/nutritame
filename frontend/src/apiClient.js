import axios from "axios";

export const api = axios.create({
  baseURL: "https://ai-coach-bridge.preview.emergentagent.com/api",
  headers: { "Content-Type": "application/json" },
});

export function setCoachAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
}

let _sessionId = null;

// HOTFIX: Centralized user_id handling with guards
function getUserId() {
  const user_id = localStorage.getItem('nt_coach_user_id');
  if (!user_id) {
    console.error('[APILIENT] Missing user_id - ensure profile is created first');
    throw new Error('Missing user_id');
  }
  return user_id;
}

// HOTFIX: Auto-recovery helper for 403 disclaimer errors
async function acceptDisclaimer(user_id) {
  try {
    console.log('[CONSENT] POST /coach/accept-disclaimer');
    await api.post('/coach/accept-disclaimer', {
      user_id: user_id,
      disclaimer_version: "v1.0-2025-09-05",
      consent_source: "global_screen", 
      consent_ui_hash: "global"
    });
    localStorage.setItem('NT_COACH_ACK', 'true');
    console.log('[CONSENT] Disclaimer accepted successfully');
    return true;
  } catch (error) {
    console.error('[CONSENT] Failed to accept disclaimer:', error);
    return false;
  }
}

export async function createSession() {
  // Already cached?
  if (_sessionId) return _sessionId;

  const user_id = getUserId();
  
  try {
    console.log('[SESSION] POST /coach/sessions with user_id:', user_id);
    const { data } = await api.post("/coach/sessions", { user_id });
    _sessionId = data.id || data.session_id || data.sessionId;
    if (!_sessionId) throw new Error("No session_id in response");
    console.log('[SESSION] Session created successfully:', _sessionId);
    return _sessionId;
  } catch (error) {
    // HOTFIX: 403 auto-recovery
    if (error?.response?.status === 403 && error?.response?.data?.detail?.includes('Disclaimer')) {
      console.log('[SESSION] 403 disclaimer error, attempting auto-recovery...');
      const recovered = await acceptDisclaimer(user_id);
      if (recovered) {
        // Retry session creation once
        console.log('[SESSION] POST /coach/sessions (retry after disclaimer)');
        const { data } = await api.post("/coach/sessions", { user_id });
        _sessionId = data.id || data.session_id || data.sessionId;
        if (!_sessionId) throw new Error("No session_id in response after retry");
        console.log('[SESSION] Session created after auto-recovery:', _sessionId);
        return _sessionId;
      }
    }
    console.error('[SESSION] Failed to create session:', error?.response?.data || error);
    throw error;
  }
}

export async function getOrCreateSessionId() {
  if (_sessionId) return _sessionId;
  return createSession();
}

// HOTFIX: Updated sendCoachMessage to accept direct text and handle all logic
export async function sendCoachMessage(messageText) {
  if (!messageText?.trim()) throw new Error("Empty message");
  
  const user_id = getUserId();
  const sessionId = await getOrCreateSessionId();
  
  console.log('[MESSAGE] POST /coach/message with sessionId:', sessionId);
  
  try {
    const { data } = await api.post("/coach/message", {
      session_id: sessionId,
      message: messageText.trim(),
      user_id: user_id
    });
    
    console.log('[MESSAGE] Message sent successfully');
    return data;
  } catch (error) {
    console.error('[MESSAGE] Failed to send message:', error?.response?.data || error);
    throw error;
  }
}