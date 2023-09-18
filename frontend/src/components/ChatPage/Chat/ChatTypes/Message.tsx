'use client'

import React, { useState, useEffect } from 'react'
import Image from 'next/image'
import { Message } from '@/types'
import useConversations from '@/hooks/useConversations'
import { Character } from '@/types'
import Refresh from './Refresh'
import { ThreeDots } from 'react-loader-spinner'
import { useSession } from 'next-auth/react'
import { ConversationsService, MessageGenerate } from '@/client'
import { useRevisions } from '@/hooks/useRevisions'
import FreeMessageLimitModal from '@/components/Modal/FreeMessageLimitModal'
import { useUser } from '@/hooks/useUser';
import ReactMarkdown from 'react-markdown'

interface MessageProps {
  conversationId: string
  message: Message
  revisions: Message[]
  mutateRevisions: () => {}
  mutateSidebar: () => void
  character: Character
  clone_avatar_uri: string
  isLast: boolean
  isRemoveMode: boolean
  isRemoveMessage: boolean
  handleRemoveMessage: (id: string) => void
}

const Message: React.FC<MessageProps> = ({ conversationId, message, revisions, mutateRevisions, mutateSidebar, clone_avatar_uri, isLast, isRemoveMode, isRemoveMessage, handleRemoveMessage }) => {
  const { data: session } = useSession()

  const [isFetchingRegenMessage, setIsFetchingRegenMessage] = useState(false)
  const [pressedRefreshIcon, setPressedRefreshIcon] = useState(false)

  const currentIndex = revisions.findIndex(obj => obj.is_main === true);

  const { userObject, isUserLoading } = useUser()


  // function formatTime(date: Date): string {
  //   let hours = date.getHours()
  //   const minutes = date.getMinutes().toString().padStart(2, '0')
  //   const ampm = hours >= 12 ? 'PM' : 'AM'

  //   hours = hours % 12
  //   hours = hours ? hours : 12

  //   return `${hours.toString().padStart(2, '0')}:${minutes} ${ampm}`
  // }

  function isYesterday(date: Date): boolean {
    // Get the current date and reset time to the start of today (midnight)
    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);

    // Get the start of yesterday by subtracting 24 hours from the start of today
    const yesterdayStart = new Date(todayStart.getTime() - 24 * 60 * 60 * 1000);

    return date >= yesterdayStart && date < todayStart;
  }

  function isAnyDayBeforeYesterday(date: Date): boolean {
    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);

    const yesterdayStart = new Date(todayStart.getTime() - 24 * 60 * 60 * 1000);

    return date < yesterdayStart;
  }

  function formatTime(date: Date): string {
    const now = new Date();

    // Check if the date is between 24 and 48 hours ago
    if (isYesterday(date)) {
      return "Yesterday";
    } else if (isAnyDayBeforeYesterday(date)) {
      const day = date.getDate().toString().padStart(2, '0');
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const year = date.getFullYear().toString().slice(2);

      return `${month}/${day}/${year}`;
    }

    let hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';

    hours = hours % 12;
    hours = hours ? hours : 12;

    return `${hours.toString().padStart(2, '0')}:${minutes} ${ampm}`;
  }

  async function generateNewMessage() {

    setIsFetchingRegenMessage(true)
    // await new Promise((resolve) => setTimeout(resolve, 500))

    const requestBody: MessageGenerate = {
      is_revision: true
    }

    // fixme (holland): this should be conversationId not null
    const newMessage = await ConversationsService.generateCloneMessageConversationsConversationIdGeneratePost(
      conversationId, requestBody
    )
    mutateRevisions()
    // mutateSidebar()

    setIsFetchingRegenMessage(false)
  }

  async function handleLeftArrow() {
    if (currentIndex > 0) {
      await ConversationsService.setRevisionAsMainConversationsConversationIdMessagesMessageIdIsMainPost(
        revisions[currentIndex - 1].id, conversationId
      )
      mutateRevisions()
      // mutateSidebar()
    }
  }

  async function handleRightArrow() {
    if (currentIndex < revisions.length - 1) {
      await ConversationsService.setRevisionAsMainConversationsConversationIdMessagesMessageIdIsMainPost(
        revisions[currentIndex + 1].id, conversationId
      )
      mutateRevisions()
      // mutateSidebar()
    }
  }

  async function handleRefresh() {
    try {
      setPressedRefreshIcon(true)
      await generateNewMessage()
      setPressedRefreshIcon(false)
    } catch (e) {
      if (e.status === 402) {
        const modalElement = document.querySelector("#hs-slide-down-animation-modal-free-message-limit");
        if (window.HSOverlay && typeof window.HSOverlay.close === 'function' && modalElement) {
          window.HSOverlay.open(modalElement);
        }
      }
      setPressedRefreshIcon(false)
      setIsFetchingRegenMessage(false)
    }
  }

  const messageContent = (isLast && revisions.length !== 0) ? revisions[currentIndex].content : message.content
  const messageTimestamp = (isLast && revisions.length !== 0) ? revisions[currentIndex].timestamp : message.timestamp

  return (
    <div className={`relative flex items-stretch m-1 py-3 rounded-xl px-3 ${isRemoveMessage ? "bg-[#a53d098c]" : "bg-[#16181A]"}`}>
      {
        (isRemoveMode && message.sender_name === userObject?.name) && (
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
      {(isRemoveMode && message.sender_name !== userObject?.name) && (
        <div className={'w-[40px] h-[40px] min-w-[40px] min-h-[40px]'} ></div>
      )}
      <div className='flex flex-col shrink-0 w-[40px] justify-between items-center'>
        <div className='h-[40px] w-[40px] relative'>
          <Image
            src={message.sender_name == userObject?.name ? session?.image || '/user-profile.png' : clone_avatar_uri}
            alt={message.sender_name}
            layout='fill'
            objectFit='cover'
            className='rounded-full'
          />
        </div>

      </div>
      <div className='ml-3 flex flex-col'>
        <div className='mb-[2px] flex items-center'>
          <span className={`mr-2 text-[15px] font-semibold leading-5 ${message.is_clone ? "text-transparent bg-clip-text bg-gradient-to-r from-[#a974f3] to-[#ed74f3]" : "text-white"}`}>
            {message.sender_name}
          </span>
          <span className='text-xs font-light text-[#979797]'>
            {isFetchingRegenMessage ? formatTime(new Date()) : formatTime(new Date(messageTimestamp))}
          </span>
          {(isLast && revisions.length !== 0) && (
            <Refresh currentIndex={currentIndex}
              messagesLength={isLast ? revisions.length : 1}
              handleLeftArrow={handleLeftArrow}
              handleRightArrow={handleRightArrow}
              handleRefresh={handleRefresh}
              isFetchingRegenMessage={isFetchingRegenMessage}
              pressedRefreshIcon={pressedRefreshIcon}
            />
          )}
        </div>
        <span className='text-[14px] font-light leading-[18px] text-white'>
          {!isFetchingRegenMessage && <ReactMarkdown>{messageContent}</ReactMarkdown>}
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
      <FreeMessageLimitModal />
    </div>

  )
}

export default Message

