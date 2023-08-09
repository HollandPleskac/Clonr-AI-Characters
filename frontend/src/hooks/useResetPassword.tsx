import { useState } from 'react';
import axios from 'axios';

interface ResetPassword {
    token: string;
    password: string;
}

export const useResetPassword = () => {
  const [isResetting, setIsResetting] = useState(false);
  const [resetError, setResetError] = useState<string | null>(null);
  const [resetSuccess, setResetSuccess] = useState(false);

  const resetPassword = async (resetPasswordData: ResetPassword) => {
    setIsResetting(true);
    setResetError(null);
    setResetSuccess(false);

    try {
      const url = 'http://localhost:8000/auth/reset-password';
      await axios.post(url, resetPasswordData);

      setResetSuccess(true);
    } catch (error) {
      setResetError('Password reset failed, please try again!');
      console.error(error);
    }

    setIsResetting(false);
  };

  return { isResetting, resetError, resetSuccess, resetPassword };
};