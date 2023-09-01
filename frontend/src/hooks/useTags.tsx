import axios from 'axios';
import { Tag } from '@/types';
import useSWR from 'swr';


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
