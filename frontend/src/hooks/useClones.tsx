'use client';

import { useState } from 'react';
import axios from 'axios';
import { Character } from '@/types';
import useSWR from 'swr';
import { ClonesService } from '@/client/services/ClonesService'
import { CloneSearchResult } from '@/client/models/CloneSearchResult'
import { CloneSortType } from '@/client/models/CloneSortType'

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

interface CloneQueryByIdParams {
  cloneId: string;
}

interface CloneQueryParams {
  tags?: number[] | null;
  name?: string;
  sort?: CloneSortType;
  similar?: string;
  offset?: number;
  limit?: number;
} 

export function useQueryClones(queryParams: CloneQueryParams) {
  const {
    tags,
    name,
    sort,
    similar,
    offset,
    limit
  } = queryParams;

  const fetcher = async () => {
    try {
      const response = await ClonesService.queryClonesClonesGet(
        tags,
        name,
        sort,
        similar,
        null, // createdAfter
        null, // createdBefore
        offset,
        limit
      );
      return response;
    } catch (error) {
      throw new Error('Error fetching clones: ' + error.message);
    }
  };

  const { data, error } = useSWR([tags, name, sort, similar, offset, limit, 'clones'], fetcher);

  return {
    data: data,
    isLoading: !error && !data,
    error: error
  };
}

export function useQueryClonesById(queryParams: CloneQueryByIdParams) {
  const {
    cloneId
  } = queryParams;

  const fetcher = async (url: string) => {
    try {
      // const response = await ClonesService.getCloneByIdClonesCloneIdGet(
      //   cloneId
      // );
      // return response;

      const response = await axios.get(
        url,
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
      console.log("error",error)
      throw new Error('Error fetching clones by id: ' + error.message);
    }
  };

  const { data, error } = useSWR(`http://localhost:8000/clones/${cloneId}`, fetcher);

  return {
    data: data,
    isLoading: !error && !data,
    error: error
  };
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

  return {
    createClone,
    generateLongDescription,
  };
}
