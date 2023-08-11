import { useState } from 'react';
import axios from 'axios';

interface Creator {
  id: string;
  username: string;
  is_public: boolean;
  user_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function useCreators() {
  const getMyCreatorInfo = async () => {
    try {
      const response = await axios.get<Creator>(
        'http://localhost:8000/creators/me',
        {
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error fetching creator info: ' + error.message);
    }
  };

  const getCreatorInfo = async (creatorId: string) => {
    try {
      const response = await axios.get<Creator>(
        `http://localhost:8000/creators/${creatorId}`,
        {
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error fetching creator info: ' + error.message);
    }
  };

  const upgradeCreator = async () => {
    try {
      const response = await axios.post(
        'http://localhost:8000/creators/upgrade',
        null,
        {
          withCredentials: true
        }
      );
      return response.status === 200;
    } catch (error) {
      throw new Error('Error upgrading creator: ' + error.message);
    }
  };

  return {
    getMyCreatorInfo,
    getCreatorInfo,
    upgradeCreator
  };
}
