import { CloneSortType, ClonesService, ConversationsService } from "@/client";
import { CharacterChat, SidebarClone } from "@/types";
import axios from "axios";
import useSWRInfinite from "swr/infinite"
  

interface SidebarClonesQueryParams {
    name?: string | null;
    cloneId?: string;
    limit: number
}

export const useSidebarClonesPagination = (queryParams: SidebarClonesQueryParams) => {
    const { name, cloneId, limit } = queryParams

    console.log("useSidebarClonesPagination -> queryParams: ", queryParams)

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
        let url = `http://localhost:8000/conversations/sidebar?convo_limit=1&offset=${pageIndex*limit}&limit=${limit}`
        if (name && name.length > 0) {
            url = url + `&name=${name}`
        }
        if (cloneId && cloneId.length > 0) {
            url = url + `&clone_id=${cloneId}`
        }
        return url
    }

    const { data, size, setSize, isLoading, mutate } = useSWRInfinite(getKey, fetcher)
    const paginatedData = data?.flat()

    const isLastPage = data && data[data.length - 1]?.length < limit // last batch if data < limit

    return {
        paginatedData,
        isLastPage,
        isLoading,
        size,
        setSize,
        mutate
    }
}