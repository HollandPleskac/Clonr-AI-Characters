import { useState } from 'react';
import axios from 'axios';

interface AuthResponse {
  token: string;
}

export const useAuth = () => {
  const [token, setToken] = useState<any | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);

  const login = async (username: string, password: string) => {
    setAuthError(null);

    try {
      const url = 'http://localhost:8000/auth/cookies/login';
      const response = await axios.post<AuthResponse>(url, { username, password });

      setToken(response.data.token);
    } catch (error) {
      setAuthError('Login failed, please check your credentials!');
      console.error(error);
    }
  };

  const logout = async () => {
    setAuthError(null);

    try {
      const url = 'http://localhost:8000/auth/cookies/logout';
      await axios.post(url);

      setToken(null);
    } catch (error) {
      console.error(error);
    }
  };

  return { token, authError, login, logout };
};