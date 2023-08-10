import React from 'react'
import Image from 'next/image'
import { Message } from '@/types'

interface MessageProps {
  message: Message
  isLast: boolean
}

const Message: React.FC<MessageProps> = ({ message, isLast }) => {
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

  return (
    <div className='flex w-full items-start py-4'>
      <Image
        key={0}
        src={message.img}
        alt={message.alt}
        width={40}
        height={40}
        className='rounded-full'
      />
      <div className='ml-3 flex flex-col'>
        <div className='mb-[2px] flex items-center'>
          <span className='mr-2 text-[15px] font-semibold leading-5 text-white'>
            {message.name}
          </span>
          <span className='text-xs font-light text-[#979797]'>
            {formatTime(message.timeStamp)}
          </span>
        </div>
        <span className='text-xs font-light leading-[18px] text-white'>
          {message.content}
        </span>
      </div>
    </div>
  )
}

export default Message
