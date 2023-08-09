'use client'

const axios = require('axios').default;

export default function useConversations() {
  const queryConversations = async (conversationId: string) => {
    try {
      const response = await axios.get(
        'http://localhost:8000/conversations/' + conversationId,
        {
          params: {},
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error fetching conversations: ' + error.message);
    }
  };

  return { queryConversations };
};
