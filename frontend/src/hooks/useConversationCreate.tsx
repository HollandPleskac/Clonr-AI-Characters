import { useState } from 'react';
import axios from 'axios';

interface ConversationCreate {
    name: string;
    user_name: string;
}

export const useConversationCreate = () => {
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [createSuccess, setCreateSuccess] = useState(false);

  const createConversation = async (conversationData: ConversationCreate) => {
    setIsCreating(true);
    setCreateError(null);
    setCreateSuccess(false);

    try {
      const url = 'http://localhost:8000/conversations/';
      await axios.post(url, conversationData);

      setCreateSuccess(true);
    } catch (error) {
      setCreateError('Conversation creation failed, please try again!');
      console.error(error);
    }

    setIsCreating(false);
  };

  return { isCreating, createError, createSuccess, createConversation };
};