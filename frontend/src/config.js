// Environment configuration for React 19 compatibility
export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://ai-coach-bridge.preview.emergentagent.com';
export const API = `${BACKEND_URL}/api`;

export default {
  BACKEND_URL,
  API
};