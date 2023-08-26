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

interface ConversationMessageQueryParams {
    conversationId: string;
}

export function useQueryConversationMessages(queryParams: ConversationMessageQueryParams) {
  const {
    conversationId
  } = queryParams;

  console.log("queryParams: ", queryParams)

  const fetcher = async () => {
    try {
      const response = await ConversationsService.getMessagesConversationsConversationIdMessagesGet(
        conversationId
      );
      return response;
    } catch (error) {
      throw new Error('Error fetching clones: ' + error.message);
    }
  };

  const { data, error } = useSWR([conversationId, 'conversationMessagesByConvoId'], fetcher);

  console.log("ERROR IS: ", error)
  console.log("data is: ", data);

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
      console.log("IN createNewConversation(), response is: ", response)
      return response;
    } catch (error) {
      console.log("ERROR IN createNewConversation(): ", error)
      throw new Error('Error creating conversation: ' + error.message);
    }
  };

  const { data, error } = useSWR(['createConversation'], fetcher);

  console.log("IN createNewConversation(), ERROR IS: ", error)
  console.log("IN createNewConversation(), data is: ", data);

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
    
      const queryConversationMessages = async (conversationId: string) => {
        try {
          const response = await axios.get<Message[]>(
            `http://localhost:8000/conversations/${conversationId}/messages`,
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
