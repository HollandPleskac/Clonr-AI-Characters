import React from 'react'
import ChevronRightPurple600 from '@/svg/ChatPage/Chat/chevron-right-purple-600.svg'
import ChevronRightPurple500 from '@/svg/ChatPage/Chat/chevron-right-purple-500.svg'
import Link from 'next/link'
import { Conversation } from '@/types'
import { formatDate } from '@/utils/formatDate'

type PreviousConversationsProps = {
  conversation: Conversation
}

// TODO: edit
const PreviousConversations = ({
  conversation,
}: PreviousConversationsProps) => {
  console.log("In PreviousConversations, this is conversation: ", conversation)
  return (
    <Link
      href={`/chat/${conversation.clone_id}/${conversation.id}`}
      className='group rounded-lg flex justify-between items-center bg-[#121212] hover:bg-gray-800 transition duration-200 w-full rounded-lg p-4 '
    >
      <div className='flex flex-col items-start mr-[5%]'>
        <h3 className='text-white text-xl font-semibold mb-2'> {formatDate(new Date(conversation.updated_at)) + " ago"} </h3>
        <h4 className='text-gray-400 mb-1 text-[14px]'>
          You: <span className='italic'>{"TODO MAKE THIS LAST_USER_MESSAGE"}</span>
        </h4>
        <h4 className='text-gray-400 text-[14px]'>
          {conversation.clone_name}:{' '}
          <span className='italic'>{conversation.last_message}</span>
        </h4>
      </div>
      <div
        className={`${
          conversation.memory_strategy === 'zero'
            ? 'text-purple-500'
            : 'text-purple-600'
        } font-semibold flex items-center shrink-0`}
      >
        <p className=''>
          {conversation.memory_strategy === 'zero'
            ? 'Zero Memory'
            : 'Long Term Memory'}
        </p>
        <div className='flex h-[24px] w-[24px] items-center justify-center ml-2'>
          {conversation.memory_strategy === 'zero' ? (
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
