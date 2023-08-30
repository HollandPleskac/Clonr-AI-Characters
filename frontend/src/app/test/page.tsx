'use client'
import { ClonesService, CloneSortType, ConversationsService } from "@/client"
import { useSidebarClonesPagination } from "@/hooks/useSidebarClonesPagination"
import { useClonesPagination } from "@/hooks/useClonesPagination"
import useConversations from "@/hooks/useConversations"
import { useMessagesPagination } from "@/hooks/useMessagesPagination"
import { Character } from "@/types"
import axios from "axios"
import InfiniteScroll from "react-infinite-scroll-component"
import useSWRInfinite from "swr/infinite"

export default function Test() {

  const queryParamsMessages = {
    conversationId: '3226e0df-9f3a-4c76-8e0f-121027c19f7a',
    limit: 5
  }

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
      <button className="text-orange-400 border block" onClick={async () => {
        await ConversationsService.getSidebarConversationsConversationsSidebarGet(
          1,
          0,
          10
        );

      }}>
        get sidebar conv
      </button>
      <button className="text-white" onClick={testAxios} >CLICKME</button>
      <button className="text-green-400" onClick={async () => {
        const res = await createMessage('3226e0df-9f3a-4c76-8e0f-121027c19f7a', 'user added message 4')


        const newMessage = {
          id: window.Date.now().toString(),
          content: "user added message 4",
          created_at: new window.Date().toString(),
          updated_at: new window.Date().toString(),
          sender_name: 'Test User',
          timestamp: new window.Date().toString(),
          is_clone: false,
          is_main: true,
          is_active: true,
          parent_id: '',
          clone_id: '',
          user_id: '',
          conversation_id: '3226e0df-9f3a-4c76-8e0f-121027c19f7a'
        }
        console.log("log", [newMessage, ...messages])

        mutate([newMessage, ...messages], false);
      }} >CREATE MESSAGE</button>
      {!isLoading &&

        <div
          className='overflow-auto transition-all duration-100'
          id='scrollable'
          style={{
            height: '400px',
            overflow: 'auto',
            display: 'flex',
            scrollBehavior: 'smooth',
            flexDirection: 'column-reverse',
          }}
        >
          <InfiniteScroll
            next={() => setSize(size + 1)}
            hasMore={!isLastPage}
            loader={<h1 className="text-red-400" >LOADING</h1>}
            endMessage={<p className="text-green-400" >Reached to the end</p>}
            dataLength={messages?.length ?? 0}
            inverse={true}
            scrollableTarget={"scrollable"}
            style={{ display: 'flex', flexDirection: 'column-reverse' }}
          >
            {messages?.map((message, index) => {
              return <h1 className="text-white border h-[100px]" key={index} >{"MESSAGE"} {message.content}</h1>
            })}

          </InfiniteScroll>
        </div>
      }
    </div>
  )
}
