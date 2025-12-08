// API configuration
// Uses Vite proxy in development so cookies work properly across devices

// For API calls - use relative URLs (proxied through Vite)
export const API_BASE = "";

// For WebSocket - need the actual backend host
const WS_PORT = 8000;
export const WS_BASE = `ws://${window.location.hostname}:${WS_PORT}`;

// Helper function to build API URLs
export function apiUrl(path) {
  return `${API_BASE}${path}`;
}

// Helper function to build WebSocket URLs
export function wsUrl(path) {
  return `${WS_BASE}${path}`;
}
