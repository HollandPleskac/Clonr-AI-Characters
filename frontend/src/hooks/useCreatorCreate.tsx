import { useState } from 'react';
import axios from 'axios';

interface CreatorCreate {
  name: string;
}

export const useCreatorCreate = () => {
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [createSuccess, setCreateSuccess] = useState(false);

  const createCreator = async (creatorData: CreatorCreate) => {
    setIsCreating(true);
    setCreateError(null);
    setCreateSuccess(false);

    try {
      const url = 'http://localhost:8000/creators/upgrade';
      await axios.post(url, creatorData);

      setCreateSuccess(true);
    } catch (error) {
      setCreateError('Creator creation failed, please try again!');
      console.error(error);
    }

    setIsCreating(false);
  };

  return { isCreating, createError, createSuccess, createCreator };
};
