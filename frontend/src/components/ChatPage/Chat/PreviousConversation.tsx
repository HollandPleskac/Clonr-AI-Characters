import React from 'react'
import ChevronRightPurple600 from '@/svg/ChatPage/Chat/chevron-right-purple-600.svg'
import ChevronRightPurple500 from '@/svg/ChatPage/Chat/chevron-right-purple-500.svg'
import Link from 'next/link'
import { Conversation } from '@/types'

type PreviousConversationsProps = {
  conversation: Conversation
}

const PreviousConversations = ({
  conversation,
}: PreviousConversationsProps) => {
  return (
    <Link
      href={`/chat/${conversation.character.id}/${conversation.id}`}
      className='group rounded-lg flex justify-between items-center bg-[#121212] hover:bg-gray-800 transition duration-200 w-full rounded-lg p-4 '
    >
      <div className='flex flex-col items-start'>
        <h3 className='text-white text-xl font-semibold mb-2'>23 Days Ago</h3>
        <h4 className='text-gray-400 mb-1 text-[14px]'>
          You: <span className='italic'>{conversation.lastUserMessage}</span>
        </h4>
        <h4 className='text-gray-400 text-[14px]'>
          {conversation.character.name}:{' '}
          <span className='italic'>{conversation.lastBotMessage}</span>
        </h4>
      </div>
      <div
        className={`${
          conversation.memoryType === 'short'
            ? 'text-purple-500'
            : 'text-purple-600'
        } font-semibold flex items-center `}
      >
        <p className=''>
          {conversation.memoryType === 'short'
            ? 'Short Term Memory'
            : 'Long Term Memory'}
        </p>
        <div className='flex h-[24px] w-[24px] items-center justify-center ml-2'>
          {conversation.memoryType === 'short' ? (
            <ChevronRightPurple500 />
          ) : (
            <ChevronRightPurple600 />
          )}
        </div>
      </div>
    </Link>
  )
}

export default PreviousConversations
