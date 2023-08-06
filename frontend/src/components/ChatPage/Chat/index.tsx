'use client'

import Image from 'next/image'
import { MouseEventHandler, useEffect, useRef, KeyboardEvent } from 'react'

import { useState } from 'react'
import Date from './ChatTypes/Date'
import MessageComponent from './ChatTypes/Message'
import SpeechRecognition, {
  useSpeechRecognition,
} from 'react-speech-recognition'
import PlusIcon from '@/svg/ChatPage/Chat/PlusIcon'
import SmileIcon from '@/svg/ChatPage/Chat/smile-icon.svg'
import MicrophoneOffIcon from '@/svg/ChatPage/Chat/microphone-off.svg'
import MicrophoneActiveIcon from '@/svg/ChatPage/Chat/microphone-active.svg'
import SendIcon from '@/svg/ChatPage/Chat/SendIcon'
import axios from 'axios'
import { ThreeDots } from 'react-loader-spinner'
import TextareaAutosize from 'react-textarea-autosize'
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
}

export default function ChatScreen({
  characterId,
  conversationId,
  character,
  initialMessages,
}: ChatScreenProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<any[]>(initialMessages) // FixMe (Jonny): workaround for type error in compiler
  const [isFetching, setIsFetching] = useState(false)
  const [convoID, setConvoID] = useState('')

  // search state
  const [isInputActive, setInputActive] = useState(false)
  const handleInputFocus = () => setInputActive(true)
  const handleInputBlur = () => setInputActive(false)
  const inputRef = useRef<HTMLInputElement>(null)

  // speech recognition
  const [speechRecognitionSupported, setSpeechRecognitionSupported] = useState<
    boolean | null
  >(null)

  useEffect(() => {
    // @ts-ignore
    import('preline')
  }, [])

  // scrolling
  useEffect(() => {
    if (containerRef.current) {
      const { scrollHeight, clientHeight } = containerRef.current
      const maxScrollTop = scrollHeight - clientHeight
      containerRef.current.scrollTop = maxScrollTop > 0 ? maxScrollTop : 0
    }
  }, [messages])

  // speech recognition
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition()

  useEffect(() => {
    setSpeechRecognitionSupported(browserSupportsSpeechRecognition)
  }, [browserSupportsSpeechRecognition])

  const handleStartListening: MouseEventHandler<HTMLButtonElement> = (
    event
  ) => {
    event.preventDefault()
    SpeechRecognition.startListening()
  }

  // can be used to pause user voice input
  const handleStopListening: MouseEventHandler<HTMLButtonElement> = (event) => {
    event.preventDefault()
    console.log(transcript)
    setMessage(transcript)
    SpeechRecognition.stopListening()
  }

  const sendMessage = () => {
    console.log('sending message:', message)

    const newMessage = {
      id: window.Date.now(),
      src: '/dummy-char.png',
      alt: 'Character Profile Picture ' + (messages.length + 1),
      time: '09:25',
      message: message,
      name: 'Holland',
    }

    let updatedMessages = [...messages, newMessage]
    setMessages(updatedMessages)
    const message_copy = message
    setMessage('')
    resetTranscript()
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
        id: window.Date.now(),
        src: '/dummy-char.png',
        alt: 'Character Profile Picture ' + (messages.length + 1),
        time: '09:28',
        message: serverMessage.content,
        name: 'Barack Obama',
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
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: `New message ${messages.length + index}`,
      timeStamp: new window.Date(),
      senderType: 'bot', // or 'user' depending on your needs
    }))

    // Add the new messages to the end of the existing messages
    setMessages((prevMessages) => [...prevMessages, ...newMessages])
  }

  return (
    <div className='w-[100%] border-r-[2px] border-[#252525] bg-[#121212] lg:inline'>
      <div className='flex h-[122px] w-full items-center justify-between border-b border-[#252525] px-10'>
        <div className='flex items-center'>
          <Image
            key={0}
            src='/dummy-char.png' // Change to your image path
            alt={`Character Profile Picture ${0 + 1}`} // Change to your alt text
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
          {/* <button className='bg-gray-800 hover:bg-gray-700 rounded-full p-2 grid place-items-center transition duration-200'>
            <MagnifyingGlass />
          </button> */}
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
                // strokeClasses='stroke-[#515151]'
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

          <ChatDropdown />
        </div>
      </div>

      <div>
        <div
          id='scrollableDiv'
          style={{
            height: 'calc(100vh - 122px - 92px)',
            overflow: 'auto',
            display: 'flex',
            flexDirection: 'column-reverse',
          }}
          className='px-6'
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
            {messages.map((message, index) => (
              <MessageComponent message={message} key={index} />
            ))}
          </InfiniteScroll>
        </div>
      </div>

      {/* <div
        style={{ height: 'calc(100vh - 122px - 92px)' }}
        ref={containerRef}
        className='flex flex-col overflow-y-scroll bg-[#121212] px-6 pt-4'
      >
        <div className='mt-auto'></div>
        <Date date='May, 11 2023' />
        {messages.map((message, index) => (
          <MessageComponent message={message} key={index} />
        ))}
        <div
          className={`${
            isFetching ? 'text-white' : 'text-transparent'
          } w-full py-4 h-[56px]`}
        >
          <ThreeDots
            height='25'
            width='25'
            radius='4'
            color='#979797'
            ariaLabel='three-dots-loading'
            wrapperStyle={{}}
            wrapperClass=''
            visible={isFetching}
          />
        </div>
      </div> */}

      <div className='flex h-[92px] items-center border-t  border-[#252525] bg-[red-400] px-6'>
        <div className='mr-[10px] grid h-[32px] w-[32px] min-w-[32px] cursor-pointer place-items-center rounded-full bg-[#5848BC] transition duration-100 hover:bg-[#4b3abd]'>
          <PlusIcon strokeClasses='stroke-[#ffffff]' />
        </div>
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
        <div className='ml-[10px] transition-all duration-100'>
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
        <div className='ml-[10px] transition-all duration-100'>
          <button
            onClick={async (event) => {
              if (!isFetching) {
                !listening && handleStartListening(event)
                listening && handleStopListening(event)
              }
            }}
            disabled={isFetching}
          >
            {listening && <MicrophoneActiveIcon />}
            {!listening && <MicrophoneOffIcon />}
            {/* <VoiceIcon
              strokeClasses={
                isFetching ? 'stroke-[#515151] fill-[#515151]' : ''
              }
            /> */}
          </button>
        </div>
      </div>
    </div>
  )
}
