import { User } from "@/types";
import axios from "axios";
import useSWR from "swr";

export function useUser() {
    const fetcher = async (url: string): Promise<User> => {
        const res = await axios.get(url, {
            withCredentials: true
        })
        return res.data
    }

    const { data, isLoading, error } = useSWR('http://localhost:8000/users/me', fetcher);

    return {
        userObject: data,
        isUserLoading: isLoading,
        isError: error
      }
}