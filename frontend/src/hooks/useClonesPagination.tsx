import { CloneSortType, ClonesService } from "@/client";
import useSWRInfinite from "swr/infinite"

interface CloneQueryParams {
    limit: number
    tags?: number[] | null;
    name?: string;
    sort?: CloneSortType;
    similar?: string;
}

export const useClonesPagination = (queryParams: CloneQueryParams) => {
    const {limit} = queryParams

    const fetcher = async (params:CloneQueryParams&{offset:number}) => {
        try {
            const res = await ClonesService.queryClonesClonesGet(
                params.tags,
                params.name,
                params.sort,
                params.similar,
                null,
                null,
                params.offset,
                params.limit
                );
            console.log("response",res)
            return res;
        } catch (error) {
            throw new Error('Error fetching clones: ' + error);
        }
    };

    // handle offset for pagination
    const getKey = (pageIndex: number, previousPageData: any[]) => {
        if (previousPageData && !previousPageData.length) return null
        return {...queryParams, offset:pageIndex*10 }
    }

    const { data, size, setSize, isLoading } = useSWRInfinite(getKey, fetcher)
    const paginatedData = data?.flat()

    const isLastPage = data && data[data.length - 1]?.length < limit // last batch if data < limit

    return {
        paginatedData,
        isLastPage,
        isLoading,
        size,
        setSize
    }
}