'use client'

import Image from 'next/image'
import { useEffect, useRef, KeyboardEvent } from 'react'

import { useState } from 'react'
import MessageComponent from './ChatTypes/Message'

import SmileIcon from '@/svg/ChatPage/Chat/smile-icon.svg'
import SendIcon from '@/svg/ChatPage/Chat/SendIcon'
import axios from 'axios'
import { ThreeDots } from 'react-loader-spinner'

import { Character, Message } from '@/types'
import InfiniteScroll from 'react-infinite-scroll-component'
import ChooseChatExperience from './ChooseChatExperience'
import PreviousConversations from './PreviousConversations'
import ChatTopBar from './ChatTopBar'
import useConversations from '@/hooks/useConversations';

interface ChatScreenProps {
  characterId: string
  conversationId: string
  character: Character
  initialMessages: Message[]
  initialConversationState: string
}

export default function ChatScreen({
  characterId,
  conversationId,
  character,
  initialMessages,
  initialConversationState,
}: ChatScreenProps) {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [isFetching, setIsFetching] = useState(false)
  const [convoID, setConvoID] = useState('')
  const [conversationState, setConversationState] = useState(
    initialConversationState
  )
  const [showChat, setShowChat] = useState(true)
  const [scrollToNewMessage, setScrollToNewMessage] = useState<boolean>(false)

  // search state
  const [isInputActive, setInputActive] = useState(false)
  const handleInputFocus = () => setInputActive(true)
  const handleInputBlur = () => setInputActive(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const divRef = useRef<HTMLDivElement | null>(null)

  // hooks
  const {createConversation, queryConversation, queryConversationMessages, createMessage, generateCloneMessage, queryCurrentRevisions} = useConversations();

  // OPTIONAL: FETCH initialMessages client side here
  // type: Message (see @/types)
  // want to sync this type up with backend
  // useEffect(() => {
  // setMessages(...)
  // also setInitialConversationState to 'undecided' or 'short' or 'long'
  // },[])

  useEffect(() => {
    // @ts-ignore
    import('preline')
  }, [])

  useEffect(() => {
    if (scrollToNewMessage && divRef.current) {
      divRef.current.scrollTop = divRef.current.scrollHeight
      setScrollToNewMessage(false)
    }
  }, [messages, scrollToNewMessage])

  const sendMessage = () => {
    console.log('sending message:', message)
    setScrollToNewMessage(true)

    const newMessage = {
      id: window.Date.now().toString(),
      img: '/dummy-char.png',
      alt: 'Character Profile Picture ' + (messages.length + 1),
      name: 'Holland',
      content: message,
      timeStamp: new window.Date(),
      senderType: 'user' as 'bot' | 'user',
    }

    let updatedMessages = [newMessage, ...messages]
    setMessages(updatedMessages)
    const message_copy = message
    setMessage('')
    fetchMessageFromServer(message_copy)
  }

  const fetchMessageFromServer = async (in_msg: String) => {
    setIsFetching(true)

    await new Promise((resolve) => setTimeout(resolve, 500))

    try {
      // TODO: edit - needs to be valid convoID str
      const convoID = "";
      console.log("this is the convoID: ", convoID)
      let serverMessage = await generateCloneMessage(convoID);
      console.log("this is the server message: ", serverMessage)

      // let url = `http://localhost:8000/v1/conversation/${convoID}/message`
      // let data = { content: in_msg, sender_name: 'User' }
      // let response = await axios.post(url, data)
      // url = `http://localhost:8000/v1/conversation/${convoID}/response`
      // response = await axios.get(url)
      // const serverMessage = response.data

      // update frontend
      if (serverMessage) {
        console.log('Server Message:', serverMessage.message)
      }

      const newServerMessage = {
        id: window.Date.now().toString(),
        img: '/dummy-char.png',
        alt: 'Character Profile Picture ' + (messages.length + 1),
        name: 'Barack Obama',
        content: serverMessage.content,
        timeStamp: new window.Date(),
        senderType: 'bot' as 'bot' | 'user',
      }

      setMessages((messages) => [...messages, newServerMessage])
    } catch (error) {
      console.error(error)
    }

    setIsFetching(false)
  }

  const handleConversationCreate = async () => {
    let r_convo = await axios.post('http://localhost:8000/v1/conversation')
    let convo_id = r_convo.data.id
    setConvoID(convo_id)
    let r_msg = await axios.get(
      `http://localhost:8000/v1/conversation/${convo_id}/message`
    )
    let msgs = r_msg.data
    console.log(msgs)
    msgs = msgs.map((x: any, index: number) => ({
      id: x.id,
      src: '/dummy-char.png',
      alt: `Character Profile Picture ${x.id}`,
      time: '09:22',
      message: x.content,
      name: x.sender_name,
    }))
    setMessages(msgs)
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60

    const paddedMinutes = String(minutes).padStart(2, '0')
    const paddedSeconds = String(remainingSeconds).padStart(2, '0')

    return `${paddedMinutes}:${paddedSeconds}`
  }

  const handleOnKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    //it triggers by pressing the enter key
    if (e.key === 'Enter') {
      sendMessage()
    }
  }

  const fetchMoreData = () => {
    // Simulate fetching 10 more messages from a server or other data source
    const newMessages: Message[] = Array.from({ length: 10 }, (_, index) => ({
      id: '134adlj23',
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: `New message ${messages.length + index}`,
      timeStamp: new window.Date(),
      senderType: 'bot',
    }))

    // Add the new messages to the end of the existing messages
    setMessages((prevMessages) => [...prevMessages, ...newMessages])
  }

  const handleSetConversationState = (newState: string) => {
    setConversationState(newState)
  }

  return (
    <div className='w-[100%] border-r-[2px] border-[#252525] bg-[#121212] lg:inline'>
      {conversationState === 'undecided' && (
        <ChooseChatExperience
          setConversationState={handleSetConversationState}
        />
      )}

      {conversationState !== 'undecided' && (
        <>
          <ChatTopBar
            character={character}
            isInputActive={isInputActive}
            handleInputFocus={handleInputFocus}
            handleInputBlur={handleInputBlur}
            inputRef={inputRef}
            toggleChatState={() => setShowChat((prevState) => !prevState)}
            showChat={showChat}
          />
          {!showChat && <PreviousConversations />}
          {showChat && (
            <>
              <div>
                <div
                  id='scrollableDiv'
                  style={{
                    height: 'calc(100vh - 122px - 92px)',
                    overflow: 'auto',
                    display: 'flex',
                    flexDirection: 'column-reverse',
                    scrollBehavior: 'smooth',
                  }}
                  className='px-6'
                  ref={divRef}
                >
                  <InfiniteScroll
                    dataLength={messages.length}
                    next={fetchMoreData}
                    style={{ display: 'flex', flexDirection: 'column-reverse' }} //To put endMessage and loader to the top.
                    inverse={true}
                    hasMore={true}
                    loader={<h4>Loading...</h4>}
                    scrollableTarget='scrollableDiv'
                    className='pt-4'
                  >
                    <div
                      className={`${
                        isFetching
                          ? 'text-white flex'
                          : 'text-transparent hidden'
                      } w-full py-4 h-[56px]`}
                    >
                      <ThreeDots
                        height='25'
                        width='25'
                        radius='4'
                        color='#979797'
                        ariaLabel='three-dots-loading'
                        wrapperStyle={{}}
                        visible={isFetching}
                      />
                    </div>
                    {messages.map((message, index) => (
                      <MessageComponent
                        message={message}
                        isLast={false}
                        key={index}
                      />
                    ))}
                  </InfiniteScroll>
                </div>
              </div>

              <div className='flex h-[92px] items-center border-t  border-[#252525] px-6'>
                <div className='relative w-full'>
                  <div className='absolute right-4 top-3'>
                    <SmileIcon />
                  </div>
                  <input
                    className='h-[48px] w-full rounded-[14px] border-none bg-[#1E1E1E] py-4 pl-4 pr-[50px] text-[15px] font-light leading-6 text-[#979797] transition-all duration-100 focus:ring-1 focus:ring-transparent'
                    type='text'
                    placeholder='Type a message'
                    value={message}
                    onChange={(event: any) => setMessage(event.target.value)}
                    style={{ outline: 'none', resize: 'none' }}
                    onKeyDown={handleOnKeyDown}
                  />
                </div>
                <div className='ml-[10px] transition-all duration-100 '>
                  <button
                    onClick={async () => {
                      !isFetching && sendMessage()
                    }}
                    disabled={isFetching}
                  >
                    <SendIcon
                      strokeClasses={
                        isFetching ? 'stroke-[#515151] fill-[#515151]' : ''
                      }
                    />
                  </button>
                </div>
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}

{
  /* <div className='flex w-full gap-x-6 mb-8'>
            <div className='w-1/2 flex flex-col bg-white border shadow-sm rounded-xl p-4 md:p-5 dark:bg-gray-800 dark:border-gray-700 dark:shadow-slate-700/[.7]'>
              <h3 className='text-lg font-bold text-gray-800 dark:text-white'>
                Short Term Memory
              </h3>
              <p className='mt-1 text-xs font-medium uppercase text-gray-500 dark:text-gray-500'>
                Fun conversations
              </p>
              <p className='mt-2 text-gray-800 dark:text-gray-400'>
                The short term memory bot offers a delightful twist for casual
                users, creating quick, fun conversations that are ideal for
                light-hearted chats and momentary enjoyment.
              </p>
              <a
                className='mt-3 inline-flex items-center gap-2 mt-5 text-sm font-medium text-purple-500 hover:text-purple-700'
                href='#'
              >
                Start Chat
                <svg
                  className='w-2.5 h-auto'
                  width='16'
                  height='16'
                  viewBox='0 0 16 16'
                  fill='none'
                  xmlns='http://www.w3.org/2000/svg'
                >
                  <path
                    d='M5 1L10.6869 7.16086C10.8637 7.35239 10.8637 7.64761 10.6869 7.83914L5 14'
                    stroke='currentColor'
                    stroke-width='2'
                    stroke-linecap='round'
                  />
                </svg>
              </a>
            </div>
            <div className='w-1/2 flex flex-col bg-white border shadow-sm rounded-xl p-4 md:p-5 dark:bg-gray-800 dark:border-gray-700 dark:shadow-slate-700/[.7]'>
              <h3 className='text-lg font-bold text-gray-800 dark:text-white'>
                Long Term Memory
              </h3>
              <p className='mt-1 text-xs font-medium uppercase text-gray-500 dark:text-gray-500'>
                Deep Relationship
              </p>
              <p className='mt-2 text-gray-800 dark:text-gray-400'>
                The long-term memory bot is designed for fostering deep
                relationships, remembering past interactions to create a more
                meaningful connection.
              </p>
              <a
                className='mt-3 inline-flex items-center gap-2 mt-5 text-sm font-medium text-purple-500 hover:text-purple-700'
                href='#'
              >
                Start Chat
                <svg
                  className='w-2.5 h-auto'
                  width='16'
                  height='16'
                  viewBox='0 0 16 16'
                  fill='none'
                  xmlns='http://www.w3.org/2000/svg'
                >
                  <path
                    d='M5 1L10.6869 7.16086C10.8637 7.35239 10.8637 7.64761 10.6869 7.83914L5 14'
                    stroke='currentColor'
                    stroke-width='2'
                    stroke-linecap='round'
                  />
                </svg>
              </a>
            </div>
          </div> */
}
