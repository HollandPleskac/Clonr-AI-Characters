'use client'

import { useState } from 'react';
import axios from 'axios';

interface ConversationCreate {
    name: string;
    user_name: string;
    memory_strategy: string;
    information_strategy: string,
    adaptation_strategy: string | null,
    clone_id: string;
}

interface Conversation {
    id: string;
    name: string;
    user_name: string;
    memory_strategy: string;
    information_strategy: string,
    adaptation_strategy: string | null,
    clone_id: string;
    created_at: string;
    updated_at: string;
    user_id: string;
    is_active: boolean
}
  
interface Message {
    id: string;
    content: string;
    created_at: string;
    updated_at: string;
    sender_name: string;
    timestamp: string;
    is_clone: boolean;
    is_main: boolean;
    is_active: boolean;
    parent_id: string;
    clone_id: string;
    user_id: string;
    conversation_id: string;
}

export default function useConversations() {
    const createConversation = async (conversationData: ConversationCreate): Promise<string> => {
        try {
          const response = await axios.post<{ conversationId: string }>(
            `http://localhost:8000/conversations/`,
            conversationData,
            {
              withCredentials: true
            }
          );
          console.log("response: ", response)

          return response.data.id;
        } catch (error) {
          throw new Error('Error creating conversation: ' + error.message);
        }
      };

    const queryConversation = async (conversationId: string) => {
        try {
          const response = await axios.get<Conversation>(
            `http://localhost:8000/conversations/${conversationId}`,
            {
              withCredentials: true
            }
          );
          return response.data;
        } catch (error) {
          throw new Error('Error fetching conversation: ' + error.message);
        }
      };
    
      const queryConversationMessages = async (conversation_id: string) => {
        try {
          const response = await axios.get<Message[]>(
            `http://localhost:8000/conversations/${conversation_id}/messages`,
            {
              withCredentials: true
            }
          );
          return response.data;
        } catch (error) {
          throw new Error('Error fetching conversation messages: ' + error.message);
        }
      };
    
      const createMessage = async (conversationId: string, content: string) => {
        try {
          const response = await axios.post<Message>(
            `http://localhost:8000/conversations/${conversationId}/messages`,
            { content },
            {
              withCredentials: true
            }
          );
          return response.data;
        } catch (error) {
          throw new Error('Error creating message: ' + error.message);
        }
      };
    
      const generateCloneMessage = async (conversationId: string) => {
        try {
          const payload = {
            is_revision: false,
          };
      
          const response = await axios.post(
            `http://localhost:8000/conversations/${conversationId}/generate`,
            payload,
            {
              withCredentials: true,
              headers: {
                'Content-Type': 'application/json',
                'accept': 'application/json',
              },
            }
          );

          return response.data;
        } catch (error) {
          throw new Error('Error generating conversation: ' + error.message);
        }
      };
    
      const queryCurrentRevisions = async (conversationId: string) => {
        try {
          const response = await axios.get<any[]>(
            `http://localhost:8000/conversations/${conversationId}/current_revisions`,
            {
              withCredentials: true
            }
          );
          return response.data;
        } catch (error) {
          throw new Error('Error fetching current revisions: ' + error.message);
        }
      };
    
      return {
        createConversation,
        queryConversation,
        queryConversationMessages,
        createMessage,
        generateCloneMessage,
        queryCurrentRevisions
      };
};
