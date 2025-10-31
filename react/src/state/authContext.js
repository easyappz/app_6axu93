import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { login as apiLogin, register as apiRegister, me as apiMe } from '../api/auth';

const AuthContext = createContext({});

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token') || '');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!token);

  const saveToken = useCallback((t) => {
    if (t) {
      localStorage.setItem('token', t);
      setToken(t);
    } else {
      localStorage.removeItem('token');
      setToken('');
    }
  }, []);

  const loadMe = useCallback(async () => {
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const data = await apiMe();
      setUser(data);
    } catch (e) {
      // invalid token or 401
      saveToken('');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [token, saveToken]);

  useEffect(() => {
    loadMe();
  }, [loadMe]);

  const loginWithCredentials = useCallback(async ({ email, password }) => {
    const data = await apiLogin({ email, password });
    if (data?.token) {
      saveToken(data.token);
      setUser(data.user || null);
    }
    return data;
  }, [saveToken]);

  const registerWithCredentials = useCallback(async ({ email, password, name }) => {
    const data = await apiRegister({ email, password, name });
    if (data?.token) {
      saveToken(data.token);
      setUser(data.user || null);
    }
    return data;
  }, [saveToken]);

  const logout = useCallback(() => {
    saveToken('');
    setUser(null);
  }, [saveToken]);

  const value = useMemo(() => ({ token, user, loading, loginWithCredentials, registerWithCredentials, logout }), [token, user, loading, loginWithCredentials, registerWithCredentials, logout]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
