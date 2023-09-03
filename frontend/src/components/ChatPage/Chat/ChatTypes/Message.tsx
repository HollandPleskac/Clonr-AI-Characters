'use client'

import React, { useState, useEffect } from 'react'
import Image from 'next/image'
import { Message } from '@/types'
import useConversations from '@/hooks/useConversations'
import { Character } from '@/types'
import { useSession } from 'next-auth/react'
import { ConversationsService } from '@/client'
import useSWR from 'swr'


interface MessageProps {
  mutateMessages: any
  conversationId: string
  message: Message
  character: Character
  clone_avatar_uri: string
  isLast: boolean
  isRemoveMode: boolean
  isRemoveMessage: boolean
  handleRemoveMessage: (id:string) => void
}

const Message: React.FC<MessageProps> = ({ mutateMessages, conversationId, message, clone_avatar_uri, isLast, isRemoveMode, isRemoveMessage, handleRemoveMessage }) => {
  const { data: session } = useSession()
  const [currentIndex, setCurrentIndex] = useState(0)
  const [messages, setMessages] = useState<Message[]>([message])


  async function getRevisions(conversationId: string) {
    const messages = await ConversationsService.getCurrentRevisionsConversationsConversationIdCurrentRevisionsGet(conversationId = conversationId)
    return messages
  }

  // This needs to turn off retries
  // const { data: revisions, isLoading, error } = useSWR(conversationId, getRevisions);
  const revisions = null;


  const textBoxColor = '#16181A'
  const textColor = '#ECEDEE'
  const rolePlayColor = '#0AB7DB'

  const { createMessage, generateCloneMessage } = useConversations();

  function formatTime(date: Date): string {
    let hours = date.getHours()
    const minutes = date.getMinutes().toString().padStart(2, '0') // Pads with 0 if needed to get 2 digits
    const ampm = hours >= 12 ? 'PM' : 'AM'

    // Convert 24-hour format to 12-hour format
    hours = hours % 12
    // If hours become 0 (midnight), set it to 12
    hours = hours ? hours : 12

    return `${hours.toString().padStart(2, '0')}:${minutes} ${ampm}`
  }

  async function generateNewMessage() {
    console.log("GENERATING NEW MESSAGE, this is message: ", message)
    
    //let newMessageContent = await generateCloneMessage(conversationId);
    
    //console.log("THIS IS newMessageContent: ", newMessageContent)
    
    const newMessage: Message = {
      id: message.id,
      content: message.content,
      created_at: message.created_at,
      updated_at: message.updated_at,
      sender_name: message.sender_name,
      timestamp: message.timestamp,
      is_clone: true,
      is_main: true,
      is_active: true,
      parent_id: message.parent_id,
      clone_id: message.clone_id,
      user_id: message.user_id,
      conversation_id: message.conversation_id,
    };
    
    // TODO: edit to remove prev msg and also add set new msg
    mutateMessages((prevMessages) => [...prevMessages, newMessage]);
  }
  
  function handleRightArrow() {
    
    if (currentIndex === messages.length - 1) {
      generateNewMessage()
    }
    setCurrentIndex(prevState => prevState + 1)
  }
      
  return (
    <div className="relative flex items-stretch m-1 py-3 rounded-xl px-3 bg-[#16181A]">
      {
        (isRemoveMode && message.sender_name === 'Test User' ) && (
          <div className='h-[40px] flex items-center justify-center w-[40px]' >
            <input
              id='remember'
              aria-describedby='remember'
              type='checkbox'
              className='self-center w-4 h-4 border focus:ring-transparent border-gray-300 rounded bg-gray-50  dark:bg-gray-700 dark:border-gray-600  checked:text-purple-500'
              required={false}
              checked={isRemoveMessage}
              onChange={() => {
                handleRemoveMessage(message.id)
              }}
              style={{ boxShadow: 'none' }}
            />
          </div>
        )}
        {(isRemoveMode && message.sender_name !== 'Test User') && (
          <div className='w-[40px] h-[40px]' ></div>
        )}
      <div className='flex flex-col shrink-0 w-[40px] justify-between items-center'>
        <div className='h-[40px] w-[40px] relative'>
          <Image
            src={message.sender_name == 'Test User' ? session?.image || '/user-profile.png' : clone_avatar_uri}
            alt={message.sender_name}
            layout='fill'
            objectFit='cover'
            className='rounded-full'
          />
        </div>
        {
          (isLast && messages.length > 1 && currentIndex !== 0) && (
            <button
              className='mt-6 w-full flex justify-center'
              onClick={() => {
                setCurrentIndex(prevState => prevState - 1)
              }} >
              <svg width="24px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M15 6L9 12L15 18" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          )
        }
        {isLast && currentIndex === 0 &&
          <div className='h-[48px] w-8' ></div>
        }

      </div>
      <div className='ml-3 flex flex-col'>
        <div className='mb-[2px] flex items-center'>
          <span className={`mr-2 text-[15px] font-semibold leading-5 ${messages[currentIndex].is_clone ? "text-transparent bg-clip-text bg-gradient-to-r from-[#a974f3] to-[#ed74f3]" : "text-white"}`}>
            {messages[currentIndex].sender_name}
          </span>
          <span className='text-xs font-light text-[#979797]'>
            {formatTime(new Date(messages[currentIndex].timestamp))}
          </span>
            {
              (isLast && (!revisions || revisions.length <= 1)) ?
                <button className='hover:bg-gray-700 ml-1 p-[4px] rounded-full active:bg-black'>
                  <svg width="12px" height="12px" viewBox="0 0 24.00 24.00" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="#ededed" transform="rotate(0)"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round" stroke="#edededCCCCCC" stroke-width="0.144"></g><g id="SVGRepo_iconCarrier"> <path d="M21 3V8M21 8H16M21 8L18 5.29168C16.4077 3.86656 14.3051 3 12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21C16.2832 21 19.8675 18.008 20.777 14" stroke="#ededed" stroke-width="2.304" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>
              </button> : ""}
          {(isLast && messages.length > 1 && revisions && revisions.length > 1) ?
            <div className="flex justify-between lg:block">
            <div className="text-xs flex items-center justify-center gap-1 self-center visible ml-2">
              <button className="dark:text-white disabled:text-gray-300 dark:disabled:text-gray-400">
                <svg stroke="currentColor" fill="none" stroke-width="1.5" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" className="h-3 w-3" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><polyline points="15 18 9 12 15 6"></polyline>
                </svg>
              </button>
              <span className="flex-grow flex-shrink-0 text-white">2 / 2</span>
              <button className="dark:text-white disabled:text-gray-300 dark:disabled:text-gray-400">
                <svg stroke="currentColor" fill="none" stroke-width="1.5" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" className="h-3 w-3" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><polyline points="9 18 15 12 9 6"></polyline>
              </svg>
              </button>
            </div>
            <div className="text-gray-400 flex self-end lg:self-center justify-center mt-2 gap-2 md:gap-3 lg:gap-1 lg:absolute lg:top-0 lg:translate-x-full lg:right-0 lg:mt-0 lg:pl-2 visible">
              <button className="p-1 rounded-md hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 disabled:dark:hover:text-gray-400"><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" className="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z">
              </path>
              </svg>
              </button>
                </div>
              </div>
            : ""}
        </div>
        <span className='font-light text-[1] font-sans leading-6 text-[#ECEDEE]'>
          {messages[currentIndex].content}
        </span>
      </div>
    </div>

  )
}

export default Message
