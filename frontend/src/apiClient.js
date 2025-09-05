import axios from "axios";

export const api = axios.create({
  baseURL: "https://meal-plan-assist.preview.emergentagent.com/api",
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

function pickSessionId(data) {
  return data?.session_id || data?.id || data?.sessionId || null;
}

function logApiError(prefix, error) {
  const status = error?.response?.status;
  const data = error?.response?.data;
  console.error(`${prefix} status=${status}`, data ?? error?.message ?? error);
}

export async function createSession(explicitUserId) {
  const user_id =
    explicitUserId ||
    window.__state?.userId ||
    localStorage.getItem("nt_coach_user_id");

  if (!user_id) {
    console.error("[WIRE] createSession: missing user_id");
    throw new Error("Missing user_id; cannot create session");
  }

  // Already cached?
  if (_sessionId) return _sessionId;

  // Use the CORRECT format identified by testing: { user_id } in request body
  try {
    console.debug("[WIRE] createSession → POST /coach/sessions (body.user_id)");
    const { data } = await api.post("/coach/sessions", { user_id });
    const sid = pickSessionId(data);
    if (!sid) throw new Error("No session_id in response");
    _sessionId = sid;
    console.debug("[WIRE] session created successfully:", sid);
    return _sessionId;
  } catch (error) {
    logApiError("[WIRE] createSession failed", error);
    throw error;
  }
}

export async function getOrCreateSessionId(explicitUserId) {
  if (_sessionId) return _sessionId;
  return createSession(explicitUserId);
}

export async function sendCoachMessage({ sessionId, message }) {
  if (!sessionId) throw new Error("Missing sessionId");
  if (!message?.trim()) throw new Error("Empty message");
  console.debug("[WIRE] sendCoachMessage → POST /coach/message", { sessionId });

  const { data } = await api.post("/coach/message", {
    session_id: sessionId,
    message,
  });

  return data;
}