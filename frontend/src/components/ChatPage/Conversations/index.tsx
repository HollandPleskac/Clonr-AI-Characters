import React, { useEffect } from 'react'
import PreviousConversation from './PreviousConversation'
import { Conversation } from '@/types'
import InfiniteScroll from 'react-infinite-scroll-component'
import { useConversationsPagination } from '@/hooks/useConversationsPagination'
import { stringify } from 'querystring'
import { ColorRing } from 'react-loader-spinner'
import ConversationsTopBar from './ConversationsTopbar'
import { useQueryClonesById } from '@/hooks/useClones'

interface ConversationsProps {
  characterId: string
}

const Conversations = ({ characterId }: ConversationsProps) => {

  const conversationsQueryParams = {
    cloneId: characterId,
    limit: 10
  }

  const {
    paginatedData: conversations,
    isLastPage: isLastConversationsPage,
    isLoading: isLoadingConversations,
    size: conversationsSize,
    setSize: setConversationsSize,
  } = useConversationsPagination(conversationsQueryParams)


  return (
    <div className='w-[100%] border-r-[2px] border-[#252525] bg-[#121212] lg:inline'>
      {/* Conversations Top bar */}
      <ConversationsTopBar
        characterId={characterId}
      />

      <div>
        {
          isLoadingConversations && (
            <div
            className="w-full grid place-items-center"
            style={{
              height: 'calc(100vh - 122px)',
            }} >
              <ColorRing
                visible={true}
                height="80"
                width="80"
                ariaLabel="blocks-loading"
                wrapperStyle={{}}
                wrapperClass="blocks-wrapper"
                colors={['#9333ea', '#9333ea', '#9333ea', '#9333ea', '#9333ea']}
              />
            </div>
          )
        }
        {!isLoadingConversations && (
          <div
            id='scrollableDiv'
            style={{
              height: 'calc(100vh - 122px)',
              overflow: 'auto',
              display: 'flex',
              flexDirection: 'column',
              scrollBehavior: 'smooth',
            }}
            className='px-6'
          >


            <InfiniteScroll
              dataLength={conversations?.length ?? 0}
              next={() => setConversationsSize(conversationsSize + 1)}
              style={{ display: 'flex', flexDirection: 'column' }} //To put endMessage and loader to the top.
              inverse={false}
              hasMore={!isLastConversationsPage}
              loader={<h4>Loading...</h4>}
              scrollableTarget='scrollableDiv'
              className='py-4 gap-y-4'
            >
              {conversations!.map((conversation, index) => (
                <PreviousConversation conversation={conversation} key={index} />
              ))}
            </InfiniteScroll>
          </div>
        )}

      </div>
    </div>
  )
}

export default Conversations
