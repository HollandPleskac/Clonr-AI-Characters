'use client'
import { ClonesService, CloneSortType } from "@/client"
import { useClonesPagination } from "@/hooks/useClonesPagination"
import { Character } from "@/types"
import InfiniteScroll from "react-infinite-scroll-component"
import useSWRInfinite from "swr/infinite"

export default function Test() {



  const queryParams = {
    // tags: activeTag ? [activeTag.id] : null,
    // sort: CloneSortType[activeSortType],
    limit: 8
}

  const {
    paginatedData: clones,
    isLastPage,
    size,
    setSize
  } = useClonesPagination(queryParams)


  return (
    <div>
      <h1 className="text-white" >TEST</h1>
      <InfiniteScroll
        next={() => setSize(size + 1)}
        hasMore={!isLastPage}
        loader={<h1 className="text-red-400" >LOADING</h1>}
        endMessage={<p className="text-green-400" >Reached to the end</p>}
        dataLength={clones?.length ?? 0}
      >
        {clones?.map((clone, index) => {
          return <h1 className="text-white border h-[100px]" key={index} >{clone.name}</h1>
        })}

      </InfiniteScroll>
    </div>
  )
}
