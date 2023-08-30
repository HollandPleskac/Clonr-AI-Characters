import { CloneSortType, ClonesService, ConversationsService, MsgSortType } from "@/client";
import { CharacterChat } from "@/types";
import axios from "axios";
import useSWRInfinite from "swr/infinite"

interface MessagesQueryParams {
    limit: number,
    conversationId: string,
    q?: (string | null),
    sort?: MsgSortType,
    sentAfter?: (string | null),
    sentBefore?: (string | null),
    offset?: number,
    isActive?: boolean,
    isMain?: boolean,
}

export const useMessagesPagination = (queryParams: MessagesQueryParams) => {
    const { limit } = queryParams

    const fetcher = async (params: MessagesQueryParams & { offset: number }) => {
        try {
            console.log("params", params)
            // const res = await ConversationsService.getMessagesConversationsConversationIdMessagesGet(
            //     params.conversationId,
            //     params.q,
            //     params.sort,
            //     params.sentAfter,
            //     params.sentBefore,
            //     params.offset,
            //     params.limit,
            //     params.isActive,
            //     params.isMain
            // );
            const res = await axios.get(`http://localhost:8000/conversations/${params.conversationId}/messages?offset=${params.offset}`, {
                params: {
                    offset: params.offset,
                    limit: params.limit,
                    is_active: true,
                    is_main: true
                },
                withCredentials: true
            });
            console.log("message res", res)

            return res.data;
        } catch (error) {
            console.log('error fetching messages', error.message)
            throw new Error('error fetching messages ' + error);
        }
    };

    // handle offset for pagination
    const getKey = (pageIndex: number, previousPageData: any[]) => {
        if (previousPageData && !previousPageData.length) return null
        return { ...queryParams, offset: pageIndex * limit }
    }

    const { data, size, setSize, isLoading, mutate } = useSWRInfinite(getKey, fetcher)
    const paginatedData = data?.flat()
    console.log("paginated data", paginatedData?.length, limit)

    const isLastPage = data && data[data.length - 1]?.length < limit  // last batch if data < limit

    return {
        paginatedData,
        isLastPage,
        isLoading,
        size,
        setSize,
        mutate
    }
}