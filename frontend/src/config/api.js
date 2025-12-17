/**
 * API Configuration
 * 
 * This file configures the API URL for different environments.
 * - In development: Uses the proxy configured in package.json (localhost:5000)
 * - In production: Uses the environment variable REACT_APP_API_URL
 */

const config = {
  // API Base URL
  // In production, this should be set via REACT_APP_API_URL environment variable
  // In development, the proxy in package.json handles routing to localhost:5000
  apiUrl: process.env.REACT_APP_API_URL || '',
  
  // Whether we're in production mode
  isProduction: process.env.NODE_ENV === 'production',
  
  // Whether we're in development mode
  isDevelopment: process.env.NODE_ENV === 'development',
};

/**
 * Get the full API endpoint URL
 * @param {string} path - The API path (e.g., '/api/synth/health')
 * @returns {string} The full URL for the API endpoint
 */
export const getApiUrl = (path) => {
  // Remove leading slash if present to avoid double slashes
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  
  // In development, return the path as-is (proxy will handle it)
  // In production, prepend the API URL
  if (config.isDevelopment) {
    return `/${cleanPath}`;
  }
  
  return config.apiUrl ? `${config.apiUrl}/${cleanPath}` : `/${cleanPath}`;
};

/**
 * Get the API base URL
 * @returns {string} The base URL for API calls
 */
export const getApiBaseUrl = () => {
  return config.apiUrl || '';
};

export default config;
