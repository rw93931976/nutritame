import axios from 'axios';

export const api = axios.create({
  baseURL: 'https://meal-plan-assist.preview.emergentagent.com/api',
});

export function setCoachAuthToken(token) {
  if (token) api.defaults.headers.common.Authorization = `Bearer ${token}`;
  else delete api.defaults.headers.common.Authorization;
}

let _sessionId = null;

function resolveUserId(explicitUserId) {
  return explicitUserId
    || window.__state?.userId
    || localStorage.getItem('nt_coach_user_id')
    || null;
}

export async function createSession(explicitUserId) {
  const user_id = resolveUserId(explicitUserId);
  if (!user_id) {
    console.error('[WIRE] createSession: missing user_id');
    throw new Error('Missing user_id; cannot create session');
  }
  const { data } = await api.post('/coach/sessions', { user_id });
  _sessionId = data?.session_id || data?.id || data?.sessionId;
  if (!_sessionId) throw new Error('Session ID not returned by /coach/sessions');
  return _sessionId;
}

export async function getOrCreateSessionId(explicitUserId) {
  if (_sessionId) return _sessionId;
  return createSession(explicitUserId);
}

export async function sendCoachMessage(message) {
  const text = (message || '').trim();
  if (!text) return;
  if (!api.defaults.headers.common.Authorization) {
    throw new Error('Auth token not set on API client');
  }
  const session_id = await getOrCreateSessionId();
  const { data } = await api.post('/coach/message', { session_id, message: text });
  return data;
}