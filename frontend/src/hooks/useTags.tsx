'use client'

const axios = require('axios').default;

export default function useTags() {
  const queryTags = async (searchInput: string) => {
    try {
      const response = await axios.get(
        'http://localhost:8000/tags',
        {
          params: { offset: 0, limit: 50 },
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error fetching tags: ' + error.message);
    }
  };

  return { queryTags };
};
