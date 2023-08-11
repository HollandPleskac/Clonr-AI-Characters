import { useState } from 'react';
import axios from 'axios';

interface Tag {
  id: string;
  created_at: string;
  updated_at: string;
  name: string;
  color_code: string;
}

export default function useTags() {
    const queryTags = async (searchInput: string) => {
      try {
        const response = await axios.get<Tag[]>(
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
  
    const createTag = async (tagData: Tag): Promise<Tag> => {
      try {
        const response = await axios.post<Tag>(
          'http://localhost:8000/tags',
          tagData,
          {
            withCredentials: true
          }
        );
        return response.data;
      } catch (error) {
        throw new Error('Error creating tag: ' + error.message);
      }
    };
  
    const getTagByName = async (tagName: string): Promise<Tag | null> => {
      try {
        const response = await axios.get<Tag>(
          `http://localhost:8000/tags/${tagName}`,
          {
            withCredentials: true
          }
        );
        return response.data;
      } catch (error) {
        console.error('Error fetching tag by name:', error);
        return null;
      }
    };
  
    return { queryTags, createTag, getTagByName };
  }