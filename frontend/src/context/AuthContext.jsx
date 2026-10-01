import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  getAuthToken,
  setAuthToken,
  removeAuthToken,
  login as apiLogin,
  register as apiRegister,
  getCurrentUser as apiGetCurrentUser,
  logout as apiLogout,
} from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setTokenState] = useState(() => getAuthToken());
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state on mount / refresh
  const checkAuth = useCallback(async () => {
    const storedToken = getAuthToken();
    if (!storedToken) {
      setUser(null);
      setTokenState(null);
      setIsLoading(false);
      return;
    }

    try {
      const profile = await apiGetCurrentUser();
      setUser(profile);
      setTokenState(storedToken);
    } catch (err) {
      // Invalid or expired token
      removeAuthToken();
      setUser(null);
      setTokenState(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (credentials) => {
    const response = await apiLogin(credentials);
    setTokenState(response.token);
    setUser({
      username: response.username,
      email: response.email,
      role: response.role,
    });
    return response;
  };

  const register = async (userData) => {
    const response = await apiRegister(userData);
    setTokenState(response.token);
    setUser({
      username: response.username,
      email: response.email,
      role: response.role,
    });
    return response;
  };

  const logout = () => {
    apiLogout();
    removeAuthToken();
    setUser(null);
    setTokenState(null);
  };

  const value = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    register,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
