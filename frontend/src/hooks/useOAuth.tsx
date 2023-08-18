'use client';

import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';

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
  const router = useRouter();

  const loginWithOAuth = async () => {
    setAuthError(null);

    const response = await axios.get<{ authorization_url: string }>(
      config.authorizeUrl
    );
    
    try {
      router.push(response.data.authorization_url);
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
      router.push('/account');

    } catch (error) {
      setAuthError(`${config.provider} authentication failed, please try again!`);
      console.error(error);
    }
  };

  return { user, authError, loginWithOAuth, handleOAuthCallback };
};
