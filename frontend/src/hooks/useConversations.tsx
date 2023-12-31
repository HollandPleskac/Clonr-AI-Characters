'use client'

import { useState } from 'react';
import axios from 'axios';
import useSWR from 'swr';
import { ConversationsService } from '@/client/services/ConversationsService'
import { Conversation } from '@/client/models/Conversation'
import { ConversationCreate } from '@/client/models/ConversationCreate'

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

interface ConvesationsSidebarQueryParams {
  offset?: number;
  limit?: number;
}

export function useQueryConversationsContinue(queryParams: ConvesationsSidebarQueryParams) {
  const {
    offset,
    limit
  } = queryParams;

  const fetcher = async (url: string) => {
    try {
      // const response = await ConversationsService.getContinueConversationsConversationsContinueGet(
      //   offset,
      //   limit
      // );
      const res = await axios.get<string>(
        url,
        {
          withCredentials: true
        }
      );

    return res.data;
    } catch (error) {
      throw new Error('Error fetching conversation continue: ' + error.message);
    }
  };

  const { data, error } = useSWR(`http://localhost:8000/conversations/continue?offset=${offset}&limit=${limit}`, fetcher);

  return {
    data: data,
    isLoading: !error && !data,
    error: error
  };
}

// TODO: edit this
export function createNewConversation(conversationData: ConversationCreate) {
  const fetcher = async () => {
    try {
      const response = await ConversationsService.createConversationConversationsPost(
        conversationData
      );
      return response;
    } catch (error) {
      throw new Error('Error creating conversation: ' + error.message);
    }
  };

  const { data, error } = useSWR(['createConversation'], fetcher);

  return {
    data: data,
    isLoading: !error && !data,
    error: error
  };
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

          return response.data.id;
        } catch (error) {
          throw new Error('Error creating conversation: ' + error.message);
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
    
      return {
        createConversation,
        createMessage,
        generateCloneMessage
      };
};
