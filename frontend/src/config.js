// Environment configuration for React 19 compatibility
export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://coach-routing-fix.preview.emergentagent.com';
export const API = `${BACKEND_URL}/api`;

// Debug logging
console.log('Config loaded:', { BACKEND_URL, API });

export default {
  BACKEND_URL,
  API
};