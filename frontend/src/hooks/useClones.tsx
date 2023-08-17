import { useState } from 'react';
import axios from 'axios';
import { Character } from '@/types';

interface Tag {
  id: string;
  created_at: string;
  updated_at: string;
  name: string;
  color_code: string;
}

interface CloneCreate {
    name: string;
    short_description: string;
    long_description: string;
    greeting_message: string;
    avatar_uri: string;
    is_active: boolean;
    is_public: boolean;
    is_short_description_generated: boolean;
    is_long_description_generated: boolean;
    is_greeting_message_generated: boolean;
    tags: Tag[];
}

interface Clone {
  id: string;
  created_at: string;
  updated_at: string;
  creator_id: string;
  name: string;
  short_description: string;
  avatar_uri: string;
  num_messages: number;
  num_conversations: number;
  tags: Tag[];
}

interface Monologue {
  id: string;
  content: string;
  source: string;
  created_at: string;
  updated_at: string;
  clone_id: string;
}

interface Document {
  id: string;
  content: string;
  name: string;
  description: string;
  type: string;
  url: string;
  created_at: string;
  updated_at: string;
  clone_id: string;
}

export default function useClones() {
  const createClone = async (cloneData: CloneCreate) => {
    try {
      const response = await axios.post<Character[]>(
        `http://localhost:8000/clones/`,
        cloneData,
        {
            withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error fetching clone: ' + error.message);
    }
  };

  const queryClones = async (queryParams: any) => {
    const {
        tags = null,
        name = null,
        sort = 'top',
        similar = null,
        offset = 0,
        limit = 20
    } = queryParams;
    try {
      const response = await axios.get<Character[]>(
        `http://localhost:8000/clones/`,
        {
          withCredentials: true,
          params: {
            tags,
            name,
            sort,
            similar,
            offset,
            limit
          }
        }
      );
      console.log("Response from queryClones(): ", response)
      return response.data;
    } catch (error) {
      throw new Error('Error fetching clone: ' + error.message);
    }
  };

  const queryCloneById = async (clone_id: string) => {
    try {
      const response = await axios.get<Character>(
        `http://localhost:8000/clones/${clone_id}`,
        {
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error fetching clone: ' + error.message);
    }
  };

  const generateLongDescription = async (cloneId: string) => {
    try {
      const response = await axios.post(
        `http://localhost:8000/clones/${cloneId}/generate_long_description`,
        null,
        {
          withCredentials: true
        }
      );
      return response.status === 200;
    } catch (error) {
      throw new Error('Error generating long description: ' + error.message);
    }
  };

  const queryGeneratedLongDescription = async (cloneId: string) => {
    try {
      const response = await axios.get<string>(
        `http://localhost:8000/clones/${cloneId}/generate_long_description`,
        {
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error fetching generated long description: ' + error.message);
    }
  };

  const createDocument = async (cloneId: string, content: string) => {
    try {
      const response = await axios.post<Document>(
        `http://localhost:8000/clones/${cloneId}/documents`,
        { content },
        {
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error creating document: ' + error.message);
    }
  };

  const queryDocuments = async (cloneId: string) => {
    try {
      const response = await axios.get<Document[]>(
        `http://localhost:8000/clones/${cloneId}/documents`,
        {
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error fetching documents: ' + error.message);
    }
  };

  const queryDocument = async (cloneId: string, documentId: string) => {
    try {
      const response = await axios.get<Document>(
        `http://localhost:8000/clones/${cloneId}/documents/${documentId}`,
        {
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error fetching document: ' + error.message);
    }
  };

  const queryMonologue = async (cloneId: string, monologueId: string) => {
    try {
      const response = await axios.get<Monologue>(
        `http://localhost:8000/clones/${cloneId}/monologues/${monologueId}`,
        {
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error fetching monologue: ' + error.message);
    }
  };

  const queryMonologues = async (cloneId: string) => {
    try {
      const response = await axios.get<Monologue[]>(
        `http://localhost:8000/clones/${cloneId}/monologues`,
        {
          withCredentials: true
        }
      );
      return response.data;
    } catch (error) {
      throw new Error('Error fetching monologues: ' + error.message);
    }
  };

  return {
    createClone,
    queryClones,
    queryCloneById,
    generateLongDescription,
    queryGeneratedLongDescription,
    createDocument,
    queryDocuments,
    queryDocument,
    queryMonologue,
    queryMonologues
  };
}
