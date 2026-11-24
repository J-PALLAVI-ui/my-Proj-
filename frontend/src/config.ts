/**
 * FujiNova Frontend API Configuration.
 *
 * - In local development: VITE_API_BASE_URL is empty or undefined, so apiUrl('/api/...')
 *   returns '/api/...', routed through the local Vite development proxy to localhost:8000.
 * - In production: VITE_API_BASE_URL is set in Render environment settings to the public
 *   backend URL (e.g. https://fujinova-api.onrender.com).
 */

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');

export function apiUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return API_BASE_URL ? `${API_BASE_URL}${cleanPath}` : cleanPath;
}
