import { useState } from 'react';
import axios from 'axios';

interface CloneCreate {
  name: string;
  short_description: string;
  long_description?: string | null;
  greeting_message?: string | null;
  avatar_uri?: string | null;
}

export const useConversationCreate = () => {
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [createSuccess, setCreateSuccess] = useState(false);

  const createConversation = async (cloneData: CloneCreate) => {
    setIsCreating(true);
    setCreateError(null);
    setCreateSuccess(false);

    try {
      const url = 'http://localhost:8000/conversations/';
      await axios.post(url, cloneData);

      setCreateSuccess(true);
    } catch (error) {
      setCreateError('Conversation creation failed. Please try again.'); // You can customize this error message
      console.error(error);
    }

    setIsCreating(false);
  };

  return { isCreating, createError, createSuccess, createConversation };
};
