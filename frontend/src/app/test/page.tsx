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


  const {
    paginatedData: messages,
    isLastPage,
    isLoading,
    size,
    setSize,
    mutate
  } = useMessagesPagination(queryParamsMessages)

  console.log("messages", messages)

  async function testAxios() {
    const res = await axios.get('http://localhost:8000/conversations/3226e0df-9f3a-4c76-8e0f-121027c19f7a/messages', {
      params: {
        offset: 0,
        limit: 10,
        is_active: true,
        is_main: true
      },
      withCredentials: true
    });
    console.log("res", res)
  }

  const { createMessage } = useConversations();


  console.log("islast", isLastPage)

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
