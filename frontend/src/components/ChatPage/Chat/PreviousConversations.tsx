import React, { useEffect } from 'react'
import PreviousConversation from './PreviousConversation'
import { Conversation } from '@/types'
import InfiniteScroll from 'react-infinite-scroll-component'

const dummyConversation: Conversation = {
  id: '12345',

  character: {
    id: '12345',
    created_at: new Date(),
    updated_at: new Date(),
    creator_id: '0987',
    name: 'Barack Obama',
    short_description:
      'I am Barack Obama, 44th President of the United States. ',
    avatar_uri: '/dummy-char.png',
    num_messages: 234234,
    num_conversations: 3423,
    tags: ['president', 'politician'],
  },
  lastUserMessage: "Hey I've got 10 questions for you",
  lastBotMessage: "Why can't I just eat my waffle?",
  lastChatTime: new Date(),
  memoryType: 'long',
}

const PreviousConversations = () => {
  const [conversations, setConversations] = React.useState<Conversation[]>([])

  // FETCH first couple previous conversations client side
  // let infinite scroll take care of the rest if the user scrolls down
  useEffect(() => {
    setConversations([
      dummyConversation,
      dummyConversation,
      dummyConversation,
      dummyConversation,
      dummyConversation,
      dummyConversation,
    ])
  }, [])

  const fetchMoreData = () => {
    // Simulate fetching 10 more conversations from a server or other data source
    const newConversations: Conversation[] = Array.from(
      { length: 20 },
      (_, index) => dummyConversation
    )

    // Add the new conversations to the end of the existing conversations
    setConversations((prevConversations) => [
      ...prevConversations,
      ...newConversations,
    ])
  }

  return (
    <div>
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
          dataLength={conversations.length}
          next={fetchMoreData}
          style={{ display: 'flex', flexDirection: 'column' }} //To put endMessage and loader to the top.
          inverse={false}
          hasMore={true}
          loader={<h4>Loading...</h4>}
          scrollableTarget='scrollableDiv'
          className='pt-4 gap-y-4'
        >
          {conversations.map((message, index) => (
            <PreviousConversation conversation={conversations[0]} key={index} />
          ))}
        </InfiniteScroll>
      </div>
    </div>
  )
}

export default PreviousConversations