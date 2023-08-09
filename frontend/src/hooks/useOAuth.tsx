import { useState } from 'react';
import axios from 'axios';

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthResponse {
  user: User;
  token: string;
}

interface OAuthConfig {
  provider: string;
  authorizeUrl: string;
  callbackUrl: string;
}

export const useOAuth = (config: OAuthConfig) => {
  const [user, setUser] = useState<User | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);

  const loginWithOAuth = async () => {
    setAuthError(null);

    try {
      window.location.href = config.authorizeUrl;
    } catch (error) {
      setAuthError(`${config.provider} authentication failed, please try again!`);
      console.error(error);
    }
  };

  const handleOAuthCallback = async (code: string) => {
    try {
      const response = await axios.get<AuthResponse>(
        `${config.callbackUrl}?code=${code}`
      );

      setUser(response.data.user);
    } catch (error) {
      setAuthError(`${config.provider} authentication failed, please try again!`);
      console.error(error);
    }
  };

  return { user, authError, loginWithOAuth, handleOAuthCallback };
};
