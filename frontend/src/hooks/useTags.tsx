import { useState } from 'react';
import axios from 'axios';
import { Tag } from '@/types';
import useSWR from 'swr';

interface TagCreate {
    name: string;
    color_code: string;
}

export function useQueryTags() {
  const fetcher = async (url: string) => {
    const response = await axios.get<Tag[]>(url, { withCredentials: true });
    return response.data;
  };

  const url = `http://localhost:8000/tags?offset=0&limit=50`;

  const { data, error } = useSWR(url, fetcher);

  return {
    data: data,
    isLoading: !error && !data,
    error: error,
  };
}


export default function useTags() {
    const queryTags = async (): Promise<Tag[]> => {
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
  
    const createTag = async (tagData: TagCreate): Promise<Tag> => {
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