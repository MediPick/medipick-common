/**
 * MediPick Universal JWT Token Storage & Session Manager
 */

const ACCESS_TOKEN_KEY = 'medipick_access_token';
const REFRESH_TOKEN_KEY = 'medipick_refresh_token';
const USER_KEY = 'medipick_user_session';

export const tokenStorage = {
  getAccessToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },

  setAccessToken(token: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(ACCESS_TOKEN_KEY, token);
  },

  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },

  setRefreshToken(token: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  },

  getUserSession<T>(): T | null {
    if (typeof window === 'undefined') return null;
    const str = localStorage.getItem(USER_KEY);
    try {
      return str ? JSON.parse(str) : null;
    } catch {
      return null;
    }
  },

  setUserSession<T>(user: T): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  clearAll(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
};
