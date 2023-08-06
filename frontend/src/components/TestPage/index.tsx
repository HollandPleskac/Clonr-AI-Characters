'use client'

import React, { useState } from 'react'
import InfiniteScroll from 'react-infinite-scroll-component'

const TestPage = () => {
  const [messages, setMessages] = useState([
    'msg1',
    'msg2',
    'msg3',
    'msg3',
    'msg1',
    'msg2',
    'msg3',
    'msg3',
    'msg1',
    'msg2',
    'msg3',
    'msg3',
    'msg1',
    'msg2',
    'msg3',
    'msg3',
    'msg1',
    'msg2',
    'msg3',
    'msg3',
    'msg1',
    'msg2',
    'msg3',
    'msg3',
    'msg1',
    'msg2',
    'msg3',
    'msg3',
    'msg1',
    'msg2',
    'msg3',
    'msg3',
    'msg1',
    'msg2',
    'msg3',
    'msg3',
    'msg1',
    'msg2',
    'msg3',
    'msg3',
    'msg1',
    'msg2',
    'msg3',
    'msg3',
  ])

  const fetchMoreData = () => {
    // Simulate fetching 10 more messages from a server or other data source
    const newMessages: string[] = Array.from(
      { length: 20 },
      (_, index) => `New message ${messages.length + index}`
    )

    // Add the new messages to the end of the existing messages
    setMessages((prevMessages) => [...prevMessages, ...newMessages])
  }

  return (
    <div className='text-white bg-orange-400 h-screen'>
      <div
        id='scrollableDiv'
        style={{
          height: 500,
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column-reverse',
        }}
      >
        <InfiniteScroll
          dataLength={messages.length}
          next={fetchMoreData}
          style={{ display: 'flex', flexDirection: 'column-reverse' }} //To put endMessage and loader to the top.
          inverse={true}
          hasMore={true}
          loader={<h4>Loading...</h4>}
          scrollableTarget='scrollableDiv'
        >
          {messages.map((i, index) => (
            <div className='bg-red-200 border-2 border-white' key={index}>
              div - #{index}
            </div>
          ))}
        </InfiniteScroll>
      </div>
    </div>
  )
}

export default TestPage
