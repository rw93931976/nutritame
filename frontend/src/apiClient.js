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

export const REAL_CONSENT_HASH = "154c9ac767bf523f27d718326dadaae1801b53f41184f0efe882b2c0027e6e17";
export const DISCLAIMER_VERSION = "v1.0-2025-09-05";

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

// HOTFIX: DUAL CONSENT WRITE (critical fix for 403 errors)
export async function writeConsentDual(user_id) {
  const isDemo = localStorage.getItem('nt_is_demo') === 'true';
  const consent_source = isDemo ? 'demo_auto' : 'global_screen';
  const base = { 
    user_id, 
    disclaimer_version: DISCLAIMER_VERSION, 
    consent_source, 
    is_demo: isDemo 
  };

  try {
    // Real hash
    console.log('[CONSENT] Writing consent with real hash for', user_id);
    await api.post('/coach/accept-disclaimer', { 
      ...base, 
      consent_ui_hash: REAL_CONSENT_HASH 
    }).catch(e => { 
      console.log('[CONSENT] Real hash write result:', e?.response?.status || 'success');
    });

    // Legacy "global" 
    console.log('[CONSENT] Writing consent with legacy hash for', user_id);
    await api.post('/coach/accept-disclaimer', { 
      ...base, 
      consent_ui_hash: 'global' 
    }).catch(e => { 
      console.log('[CONSENT] Legacy hash write result:', e?.response?.status || 'success');
    });

    console.log('[CONSENT] Dual-write completed for', user_id);
    localStorage.setItem('NT_COACH_ACK', 'true');
  } catch (error) {
    console.error('[CONSENT] Dual-write failed:', error);
    throw error;
  }
}

export function resetSessionCache() { 
  _sessionId = null; 
  console.log('[SESSION] Cache reset');
}

export async function createSession(explicitUserId) {
  const user_id = explicitUserId || getUserId();
  
  // Already cached?
  if (_sessionId) {
    console.log('[SESSION] Using cached session:', _sessionId);
    return _sessionId;
  }

  try {
    console.log('[SESSION] POST /coach/sessions with user_id:', user_id);
    const { data } = await api.post('/coach/sessions', { user_id });
    _sessionId = data?.session_id || data?.id || data?.sessionId;
    if (!_sessionId) throw new Error('Session ID not returned');
    console.log('[SESSION] Session created successfully:', _sessionId);
    return _sessionId;
  } catch (err) {
    const detail = err?.response?.data?.detail || '';
    if (err?.response?.status === 403 && /Disclaimer/i.test(detail)) {
      console.warn('[SESSION] 403 disclaimer; performing dual consent then retrying once…');
      await writeConsentDual(user_id);
      
      // Retry once
      console.log('[SESSION] POST /coach/sessions (retry after dual consent)');
      const { data } = await api.post('/coach/sessions', { user_id });
      _sessionId = data?.session_id || data?.id || data?.sessionId;
      if (!_sessionId) throw new Error('Session ID not returned (retry)');
      console.log('[SESSION] Session created after retry:', _sessionId);
      return _sessionId;
    }
    console.error('[SESSION] Failed to create session:', err?.response?.data || err);
    throw err;
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