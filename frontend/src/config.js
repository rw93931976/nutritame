// Environment configuration for React 19 compatibility
const getEnvVar = (name, defaultValue = '') => {
  // Try different ways to access environment variables
  if (typeof process !== 'undefined' && process.env && process.env[name]) {
    return process.env[name];
  }
  
  if (typeof import !== 'undefined' && import.meta && import.meta.env && import.meta.env[name]) {
    return import.meta.env[name];
  }
  
  // Fallback to window object (for runtime injection)
  if (typeof window !== 'undefined' && window.env && window.env[name]) {
    return window.env[name];
  }
  
  return defaultValue;
};

export const BACKEND_URL = getEnvVar('REACT_APP_BACKEND_URL', 'https://diabeticmeal-app.preview.emergentagent.com');
export const API = `${BACKEND_URL}/api`;

export default {
  BACKEND_URL,
  API
};