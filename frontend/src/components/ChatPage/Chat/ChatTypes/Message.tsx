import React, { useState, useEffect } from 'react'
import Image from 'next/image'
import { Message } from '@/types'
import { notFound } from 'next/navigation'

interface MessageProps {
  message: Message
  isLast: boolean
}

const Message: React.FC<MessageProps> = ({ message, isLast }) => {

  const [currentIndex, setCurrentIndex] = useState(0)
  const [messages, setMessages] = useState<Message[]>([message])

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

  function generateNewMessage() {

    const newMessage: Message = {
      id: '12345',
      img: '/new-image.png',
      alt: 'new-alt',
      name: 'new-name',
      content: 'New content',
      timeStamp: new Date(),
      senderType: 'bot',
    };

    setMessages((prevMessages) => [...prevMessages, newMessage]);
  }

  function handleRightArrow() {
    
    if (currentIndex === messages.length-1){
      generateNewMessage()
    }
    setCurrentIndex(prevState=>prevState+1)
  }
  

  return (
    <div className='relative flex flex-grow w-full items-stretch py-4'>
      <div className='flex flex-col shrink-0 w-[40px] justify-between items-center'>
        <Image
          key={0}
          src={message.img}
          alt={message.alt}
          width={40}
          height={40}
          className='rounded-full'
        />
        {
          (isLast && messages.length > 1 && currentIndex !== 0) && (
            <button
            className='mt-6 w-full flex justify-center'
            onClick={() => {
              setCurrentIndex(prevState=>prevState-1)
            }} >
              <svg width="24px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M15 6L9 12L15 18" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </button>
          )
        }
        {isLast && currentIndex === 0 && 
          <div className='h-[48px] w-8' ></div>
        }

      </div>
      <div className='ml-3 flex flex-col grow'>
        <div className='mb-[2px] flex items-center'>
          <span className='mr-2 text-[15px] font-semibold leading-5 text-white'>
            {messages[currentIndex].name}
          </span>
          <span className='text-xs font-light text-[#979797]'>
            {formatTime(messages[currentIndex].timeStamp)}
          </span>
        </div>
        <span className='text-xs font-light leading-[18px] text-white'>
          {messages[currentIndex].content}
        </span>
      </div>
      <div className='flex flex-col shrink-0 w-[40px] justify-end items-center'>
        {
          isLast && (
            <button
            className='mt-6 w-full flex justify-center'
            onClick={handleRightArrow} >
              <svg width="24px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 6L15 12L9 18" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </button>
          )
        }
      </div>
    </div>

  )
}

export default Message
