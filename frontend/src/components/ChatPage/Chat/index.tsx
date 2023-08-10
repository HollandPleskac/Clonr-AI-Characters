'use client'

import Image from 'next/image'
import { useEffect, useRef, KeyboardEvent } from 'react'

import { useState } from 'react'
import MessageComponent from './ChatTypes/Message'

import SmileIcon from '@/svg/ChatPage/Chat/smile-icon.svg'
import SendIcon from '@/svg/ChatPage/Chat/SendIcon'
import axios from 'axios'
import { ThreeDots } from 'react-loader-spinner'
import MagnifyingGlass from '@/svg/ChatPage/Chat/magnify.svg'
import Paperclip from '@/svg/ChatPage/Chat/paperclip.svg'
import ChatDropdown from './ChatDropdown'
import { Character, Message } from '@/types'
import InfiniteScroll from 'react-infinite-scroll-component'

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
  const [showPreviousMessages, setShowPreviousMessages] = useState(false)
  const [scrollToNewMessage, setScrollToNewMessage] = useState<boolean>(false)

  // search state
  const [isInputActive, setInputActive] = useState(false)
  const handleInputFocus = () => setInputActive(true)
  const handleInputBlur = () => setInputActive(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const divRef = useRef<HTMLDivElement | null>(null)

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
      let url = `http://localhost:8000/v1/conversation/${convoID}/message`
      let data = { content: in_msg, sender_name: 'User' }
      let response = await axios.post(url, data)
      url = `http://localhost:8000/v1/conversation/${convoID}/response`
      response = await axios.get(url)
      const serverMessage = response.data

      // update frontend
      if (response) {
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

  return (
    <div className='w-[100%] border-r-[2px] border-[#252525] bg-[#121212] lg:inline'>
      {conversationState === 'undecided' && (
        <div
          className='h-full px-8 flex flex-col gap-x-8 justify-center items-start pt-8'
          style={{ height: 'calc(100vh)' }}
        >
          {/* <h1 className='text-2xl font-bold md:text-4xl text-white mb-8'>
            How do you want to chat?
          </h1> */}
          <div className='flex gap-x-8 justify-center'>
            <div className='w-[280px] flex flex-col'>
              <div className='h-[280px] w-[280px] relative'>
                <Image
                  src='/barack2.jpeg'
                  alt='logo'
                  layout='fill'
                  objectFit='cover'
                  className='rounded-lg mb-5'
                />
              </div>
              <h2 className='text-xl text-left my-4 font-semibold text-gray-500'>
                22.3k Chats
              </h2>
              <div className='flex flex-wrap gap-2'>
                <button className='px-2 py-1 text-sm text-gray-600 border-2 border-gray-700 rounded-lg rounder-gray-800 hover:border-gray-700 hover:text-gray-600'>
                  President
                </button>
                <button className='px-2 py-1 text-sm text-gray-600 border-2 border-gray-700 rounded-lg rounder-gray-800 hover:border-gray-700 hover:text-gray-600'>
                  Male
                </button>
                <button className='px-2 py-1 text-sm text-gray-600 border-2 border-gray-700 rounded-lg rounder-gray-800 hover:border-gray-700 hover:text-gray-600'>
                  Politician
                </button>
              </div>
            </div>
            <div className='w-1/3 flex flex-col justify-start'>
              <h2 className='text-lg sm:text-4xl font-semibold mb-4 text-white'>
                Barack Obama
              </h2>
              <p className='mb-5 text-lg text-gray-400'>
                I am Barack Obama, 44th President of the United States.{' '}
              </p>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                Long Description
              </h2>
              <p className='mb-5 text-gray-400 lime-clamp-3'>
                I am Barack Obama, 44th President of the United States. I am
                Barack Obama, 44th President of the United States. I am Barack
                Obama, 44th Presid...
              </p>
              <button
                onClick={() => {
                  setConversationState('short_term')
                }}
                className='flex items-center justify-between w-full py-2 px-4 inline-flex bg-purple-500 rounded-lg hover:bg-purple-600 text-white'
              >
                Start Short Term Memory Chat
                <div>i</div>
              </button>
              <button
                onClick={() => {
                  setConversationState('long term')
                }}
                className='mt-2 flex items-center justify-between w-full py-2 px-4 inline-flex bg-purple-500 rounded-lg hover:bg-purple-600 text-white'
              >
                Start Long Term Memory Chat
                <div>i</div>
              </button>
            </div>
            
          </div>

          {/* <h1 className='text-2xl font-bold md:text-4xl text-white mb-8'>
            Character Information
          </h1> */}
        </div>
      )}

      {conversationState !== 'undecided' && (
        <>
          <div className='flex h-[122px] w-full items-center justify-between border-b border-[#252525] px-10'>
            <div className='flex items-center'>
              <Image
                key={0}
                src='/dummy-char.png'
                alt={`Character Profile Picture ${0 + 1}`}
                width={55}
                height={55}
                className='rounded-full'
              />
              <div className='flex flex-col ml-6 gap-y-3'>
                <h3 className='text-3xl font-bold leading-5 text-white'>
                  {character.name}
                </h3>
                <p className='text-gray-400 text-sm line-clamp-1'>
                  {character.short_description}
                </p>
              </div>
            </div>
            <div className='flex items-center gap-x-4'>
              <div className='relative group'>
                <button
                  onClick={() => {
                    if (inputRef.current) {
                      inputRef.current.focus()
                    }
                  }}
                  className='group absolute peer left-[10px] top-2 peer cursor-default'
                >
                  <MagnifyingGlass
                    strokeClasses={` group-focus:stroke-[#5848BC] ${
                      isInputActive ? 'stroke-[#5848BC]' : 'stroke-[#515151]'
                    } transition duration-100 bg-red-400`}
                  />
                </button>
                <input
                  ref={inputRef}
                  onFocus={handleInputFocus}
                  onBlur={handleInputBlur}
                  className={`cursor-default peer-focus:cursor-auto focus:cursor-auto peer py-auto h-[40px] w-[44px] peer-focus:w-[300px] focus:w-[300px] transition-all  duration-500 rounded-full border-none bg-gray-800 peer-focus:bg-gray-700 focus:bg-gray-700 pr-0 pl-[44px] text-[15px] font-light leading-6 text-[#979797] focus:ring-1 focus:ring-transparent`}
                  type='text'
                  placeholder='Search'
                  style={{ outline: 'none', resize: 'none' }}
                />
              </div>
              <button className='bg-gray-800 hover:bg-gray-700 rounded-full p-2 grid place-items-center transition duration-200'>
                <Paperclip />
              </button>

              <ChatDropdown
                togglePreviousConversations={() => {
                  setShowPreviousMessages((prevState) => !prevState)
                }}
              />
            </div>
          </div>
          {showPreviousMessages && (
            <div
              style={{
                height: 'calc(100vh - 122px)',
              }}
              className='p-8'
            >
              <button className='rounded-lg flex justify-between items-center bg-black hover:bg-gray-800 transition duration-200 w-[80%] rounded-lg p-4 '>
                <div className='flex flex-col items-start '>
                  <h3 className='text-white text-xl font-semibold mb-2'>
                    23 Days Ago
                  </h3>
                  <h4 className='text-gray-400 mb-1 text-[14px]'>
                    You: <span className='italic'>hey whats up?</span>
                  </h4>
                  <h4 className='text-gray-400 text-[14px]'>
                    Barack Obama:{' '}
                    <span className='italic'>nothing much how about you?</span>
                  </h4>
                </div>
                <div className='text-purple-600 font-semibold'>
                  Long Term Memory
                </div>
              </button>
            </div>
          )}

          {!showPreviousMessages && (
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
                        wrapperclassName=''
                        visible={isFetching}
                      />
                    </div>
                    {messages.map((message, index) => (
                      <MessageComponent message={message} key={index} />
                    ))}
                  </InfiniteScroll>
                </div>
              </div>

              <div className='flex h-[92px] items-center border-t  border-[#252525] bg-[red-400] px-6'>
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
