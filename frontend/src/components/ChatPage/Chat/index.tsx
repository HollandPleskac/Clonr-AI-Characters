'use client'

import Image from 'next/image'
import { MouseEventHandler, useEffect, useRef, KeyboardEvent } from 'react'

import { useState } from 'react'
import Date from './ChatTypes/Date'
import Message from './ChatTypes/Message'
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

const dummy_messages = [
  {
    id: 1,
    src: '/dummy-char.png',
    alt: 'Character Profile Picture 1',
    time: '09:22',
    message: 'hey, how are you? (first msg)',
    name: 'Holland',
  },
  {
    id: 2,
    src: '/dummy-char.png',
    alt: 'Character Profile Picture 2',
    time: '09:23',
    message: 'whats up?',
    name: 'Mika-chan',
  },
  {
    id: 3,
    src: '/dummy-char.png',
    alt: 'Character Profile Picture 3',
    time: '09:24',
    message: 'hello, how are you?',
    name: 'Holland',
  },
]

interface ChatScreenProps {
  characterId: string
  chatId: string
  characterName: string
}

export default function ChatScreen({
  characterId,
  chatId,
  characterName,
}: ChatScreenProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<any[]>([]) // FixMe (Jonny): workaround for type error in compiler
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
  const [seconds, setSeconds] = useState(0)

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

  useEffect(() => {
    let intervalId: NodeJS.Timer

    if (listening) {
      intervalId = setInterval(() => {
        setSeconds((seconds) => seconds + 1)
      }, 1000)
    }
    return () => clearInterval(intervalId)
  }, [listening])

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

  const handleResetTranscript: MouseEventHandler<HTMLButtonElement> = (
    event
  ) => {
    event.preventDefault()
    resetTranscript()
    setSeconds(0) // reset timer to 0 seconds
  }

  const sendVoiceMessage = () => {
    console.log(transcript)
    resetTranscript()
    setSeconds(0)
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
    setSeconds(0)
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

    // Use String.prototype.padStart() to pad the start of the string with 0's until it's 2 characters long
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
              Craig Ortega
            </h3>
            <p className='text-gray-400 text-sm'>
              I love buying new things but I hate spending money
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
          {/* <button className='bg-gray-800 hover:bg-gray-700 rounded-full p-2 grid place-items-center transition duration-200'>
            <HorizontalDotsBig />
          </button> */}
          <ChatDropdown />
        </div>
        {/* <button
          className='rounded-lg bg-[#5848BC] transition duration-100 hover:bg-[#4b3abd] text-white p-4 active:bg-purple-900'
          onClick={handleConversationCreate}
        >
          New Conversation
        </button> */}
      </div>
      {/* <div
        style={{ height: 'calc(100vh - 72px - 92px - 72px)' }}
        ref={containerRef}
        className='flex flex-col overflow-y-scroll bg-[#121212] px-6 pt-4'
      >
        <div className='flex gap-x-12 h-full pt-[60px]'>
          <div className='flex flex-col w-1/2'>
            <div className='ml-auto flex flex-col items-start '>
              <div className='relative w-[350px] aspect-[1/1] rounded-[14px] mb-4'>
                <Image
                  src={'/char.png'}
                  alt={'character.name'}
                  layout='fill'
                  objectFit='cover'
                  className='absolute rounded-[14px] cursor-pointer'
                />
                <div className='flex items-center gap-x-1 absolute top-2 right-2 bg-purple-500 rounded-[14px] text-white px-2 py-[0.5px]'>
                  2.5m
                </div>
              </div>
              <div className='flex flex-wrap text-white text-sm gap-2 w-[350px] justify-start'>
                {['Male', 'Bodyguard', 'Tough'].map((tag, index) => (
                  <div
                    key={index}
                    className={`bg-black px-4 py-2 cursor-pointer border-[rgba(255,255,255,0.2)] rounded-lg hover:ring-1 hover:ring-[rgba(255,255,255,0.2)] border-[1px]`}
                  >
                    {tag}
                  </div>
                ))}
              </div>
              <div className='flex'>
                <button>Copy URL</button>
                <button>Share</button>
                <button>Report</button>
              </div>
            </div>
          </div>
          <div className='flex flex-col w-1/2 text-white items-start'>
            <h1 className='font-bold text-5xl mb-2'>Marcus</h1>
            <a className='mr-2 mb-6 cursor-pointer text-lg text-[#9084e0] font-bold hover:text-white hover:underline transition-colors duration-200'>
              @charname
            </a>

            <h4 className='text-[#e5e5e5] font-semibold mb-1 text-[18px]'>
              Short Description
            </h4>
            <p className='text-[16px] text-[#b1b1b1] mb-4 w-1/2'>
              The new bodyguard your father has hired to protect you The new
              bodyguard your father has hired to protect you
            </p>
            <h4 className='text-[#e5e5e5] font-semibold mb-1 text-[18px]'>
              Long Description
            </h4>
            <p className='text-[16px] text-[#b1b1b1] mb-6 w-1/2'>
              The new bodyguard your father has hired to protect you The new
              bodyguard your father has hired to protect you The new bodyguard
              your father has hired to protect you The new bodyguard your father
              has hired to protect you The new bodyguard your father has hired
              to protect you The new bodyguard your father has hired to...
            </p>
            <div className='flex flex-col gap-y-2 text-white w-1/2 '>
              <button className='bg-purple-500 px-4 py-2 rounded-[10px] hover:bg-purple-600 transition duration-200'>
                Long Term Memory Chat
              </button>
              <button className='bg-orange-600 px-4 py-2 rounded-[10px] hover:bg-orange-700 transition duration-200'>
                Short Term Memory Chat
              </button>
            </div>
          </div>
        </div>
      </div> */}
      <div
        style={{ height: 'calc(100vh - 122px - 92px)' }}
        ref={containerRef}
        className='flex flex-col overflow-y-scroll bg-[#121212] px-6 pt-4'
      >
        <div className='mt-auto'></div>
        <Date date='May, 11 2023' />
        {messages.map((msg) => (
          <Message
            key={msg.id}
            src={msg.src}
            alt={msg.alt}
            time={msg.time}
            messages={[msg.message]}
            name={msg.name}
          />
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
      </div>

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
