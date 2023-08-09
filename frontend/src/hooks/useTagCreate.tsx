import { useState } from 'react';
import axios from 'axios';

interface TagCreate {
  name: string;
}

export const useTagCreate = () => {
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [createSuccess, setCreateSuccess] = useState(false);

  const createTag = async (tagData: TagCreate) => {
    setIsCreating(true);
    setCreateError(null);
    setCreateSuccess(false);

    try {
      const url = 'http://localhost:8000/tags/';
      await axios.post(url, tagData);

      setCreateSuccess(true);
    } catch (error) {
      setCreateError('Tag creation failed, please try again!');
      console.error(error);
    }

    setIsCreating(false);
  };

  return { isCreating, createError, createSuccess, createTag };
};
