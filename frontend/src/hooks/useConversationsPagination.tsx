import { CloneSortType, ClonesService, ConversationsService } from "@/client";
import { CharacterChat, SidebarClone } from "@/types";
import axios from "axios";
import useSWRInfinite from "swr/infinite"
  

interface ConversationsQueryParams {
    limit: number
    cloneId: string,
}

export const useConversationsPagination = (queryParams: ConversationsQueryParams) => {
    const { limit } = queryParams

    const fetcher = async (url:string) => {
        try {
            const res = await axios.get<string>(
                url,
                {
                  withCredentials: true
                }
              );

            return res.data;
        } catch (error) {
            throw new Error('Error fetching clones: ' + error);
        }
    };

    // handle offset for pagination
    const getKey = (pageIndex: number, previousPageData: any[]) => {
        if (previousPageData && !previousPageData.length) return null
        const url = `http://localhost:8000/conversations?offset=${pageIndex*limit}&limit=${limit}&clone_id=${queryParams.cloneId}`
        console.log("url",url)
        return url
    }

    const { data, size, setSize, isLoading } = useSWRInfinite(getKey, fetcher)
    const paginatedData = data?.flat()

    const isLastPage = data && data[data.length - 1]?.length < limit // last batch if data < limit

    return {
        paginatedData,
        isLastPage,
        isLoading,
        size,
        setSize,
    }
}