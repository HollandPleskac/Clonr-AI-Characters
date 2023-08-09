'use client'

const axios = require('axios').default;

export default function useClones() {
  const queryClones = async (searchInput: string, sortType: string = 'top') => {
    try {
      const response = await axios.get(
        'http://localhost:8000/clones',
        {
          params: { similar: searchInput, sort: sortType, limit: 50 },
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error fetching clones: ' + error.message);
    }
  };

  const fetchCloneById = async (cloneId: string): Promise<Clone | null> => {
    try {
      const response = await axios.get(
        `http://localhost:8000/clones/${cloneId}`,
        {
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching clone by ID:', error);
      return null;
    }
  };

  return { queryClones, fetchCloneById };
};
