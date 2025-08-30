// Environment configuration for React 19 compatibility
const getEnvVar = (name, defaultValue) => {
  try {
    if (process && process.env && process.env[name]) {
      return process.env[name];
    }
  } catch (e) {
    // process not available
  }
  
  return defaultValue || '';
};

export const BACKEND_URL = getEnvVar('REACT_APP_BACKEND_URL', 'https://app.nutritame.com');
export const API = `${BACKEND_URL}/api`;

// Debug logging
console.log('Config loaded:', { BACKEND_URL, API });

export default {
  BACKEND_URL,
  API
};