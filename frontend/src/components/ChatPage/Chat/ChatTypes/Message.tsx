'use client'

import React, { useState, useEffect } from 'react'
import Image from 'next/image'
import { Message } from '@/types'
import useConversations from '@/hooks/useConversations'
import { Character } from '@/types'
import Refresh from './Refresh'
import { ThreeDots } from 'react-loader-spinner'
import { useSession } from 'next-auth/react'
import { ConversationsService } from '@/client'

interface MessageProps {
  mutateMessages: any
  conversationId: string
  message: Message
  character: Character
  clone_avatar_uri: string
  isLast: boolean
  isRemoveMode: boolean
  isRemoveMessage: boolean
  handleRemoveMessage: (id: string) => void
}

const Message: React.FC<MessageProps> = ({ mutateMessages, conversationId, message, clone_avatar_uri, isLast, isRemoveMode, isRemoveMessage, handleRemoveMessage }) => {
  const { data: session } = useSession()
  const [currentIndex, setCurrentIndex] = useState(0)
  const [messages, setMessages] = useState<Message[]>([message])
  const [isFetchingRegenMessage, setIsFetchingRegenMessage] = useState(false)
  const [pressedRefreshIcon, setPressedRefreshIcon] = useState(false)

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

    setIsFetchingRegenMessage(true)
    await new Promise((resolve) => setTimeout(resolve, 500))

    // const newMessage: Message = {
    //   id: message.id,
    //   content: "some new content",
    //   created_at: message.created_at,
    //   updated_at: message.updated_at,
    //   sender_name: message.sender_name,
    //   timestamp: message.timestamp,
    //   is_clone: true,
    //   is_main: true,
    //   is_active: true,
    //   parent_id: message.parent_id,
    //   clone_id: message.clone_id,
    //   user_id: message.user_id,
    //   conversation_id: message.conversation_id,
    // };

    // await new Promise((resolve) => setTimeout(resolve, 500))

    const newMessage = await generateCloneMessage(conversationId)

    setMessages([...messages, newMessage])
    setIsFetchingRegenMessage(false)

    // mutateMessages((prevMessages) => [...prevMessages, newMessage]);
  }

  function handleLeftArrow() {
    if (currentIndex > 0) {
      setCurrentIndex(prevState => prevState - 1)
    }
  }

  async function handleRightArrow() {
    console.log("current index", currentIndex, messages.length)
    if (currentIndex === messages.length - 1) {
      console.log("trigger")
      await generateNewMessage()
      setCurrentIndex(prevState => prevState + 1)
    } else {
      setCurrentIndex(prevState => prevState + 1)
    }
  }

  async function handleRefresh() {
    setPressedRefreshIcon(true)
    await generateNewMessage()
    console.log("len", messages.length - 1)
    setCurrentIndex(messages.length)
    setPressedRefreshIcon(false)
  }
      
  return (
    <div className="relative flex items-stretch m-1 py-3 rounded-xl px-3 bg-[#16181A]">
      {
        (isRemoveMode && message.sender_name === 'Test User') && (
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

      </div>
      <div className='ml-3 flex flex-col'>
        <div className='mb-[2px] flex items-center'>
          <span className={`mr-2 text-[15px] font-semibold leading-5 ${messages[currentIndex].is_clone ? "text-transparent bg-clip-text bg-gradient-to-r from-[#a974f3] to-[#ed74f3]" : "text-white"}`}>
            {messages[currentIndex].sender_name}
          </span>
          <span className='text-xs font-light text-[#979797]'>
            {formatTime(new Date(messages[currentIndex].timestamp))}
          </span>
          {isLast && (
            <Refresh currentIndex={currentIndex}
              messagesLength={messages.length}
              handleLeftArrow={handleLeftArrow}
              handleRightArrow={handleRightArrow}
              handleRefresh={handleRefresh}
              isFetchingRegenMessage={isFetchingRegenMessage}
              pressedRefreshIcon={pressedRefreshIcon}
            />
          )}
        </div>
        <span className='text-xs font-light leading-[18px] text-white'>
          {!isFetchingRegenMessage && messages[currentIndex].content}
          {isFetchingRegenMessage && (<ThreeDots
            height='18'
            width='22'
            radius='4'
            color='#979797'
            ariaLabel='three-dots-loading'
            wrapperStyle={{}}
            visible={isFetchingRegenMessage}
          />)}
        </span>

      </div>
    </div>

  )
}

export default Message

