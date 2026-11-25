import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { api, clearToken, getToken, setToken } from './api.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getToken()));

  const clearSession = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  const logout = useCallback(async () => {
    await api.post('/auth/logout').catch(() => {});
    clearSession();
  }, [clearSession]);

  useEffect(() => {
    if (!getToken()) return;
    api
      .get('/auth/me')
      .then((data) => setUser(data.user))
      .catch(() => clearToken())
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    window.addEventListener('questlog:logout', clearSession);
    return () => window.removeEventListener('questlog:logout', clearSession);
  }, [clearSession]);

  const authenticate = useCallback(async (path, payload) => {
    const data = await api.post(path, payload);
    setToken(data.token);
    setUser(data.user);
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      logout,
      login: (payload) => authenticate('/auth/login', payload),
      register: (payload) => authenticate('/auth/register', payload),
    }),
    [user, loading, logout, authenticate],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
