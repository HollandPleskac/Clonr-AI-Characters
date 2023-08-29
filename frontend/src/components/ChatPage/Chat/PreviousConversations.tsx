import React, { useEffect } from 'react'
import PreviousConversation from './PreviousConversation'
import { Conversation } from '@/types'
import InfiniteScroll from 'react-infinite-scroll-component'
import { useConversationsPagination } from '@/hooks/useConversationsPagination'
import { stringify } from 'querystring'
import { ColorRing } from 'react-loader-spinner'

interface PreviousConversationsProps {
  characterId: string
}

const PreviousConversations = ({ characterId }: PreviousConversationsProps) => {

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
    <div>
      {
        isLoadingConversations && (
          <div className="grid place-items-center" >
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
  )
}

export default PreviousConversations
