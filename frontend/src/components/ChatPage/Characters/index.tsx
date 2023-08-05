'use client'

import React, { useEffect, useRef, useState } from 'react'
import Image from 'next/image'
import SearchIcon from './SearchIcon'
import Character from './Character'
import CharacterDropdown from './CharacterDropdown'

interface MessageData {
  name: string
  username: string
  messagePreview: string
  newMessages: number
  timeLastSeen: string
}

const messages: MessageData[] = [
  {
    name: 'Mika-chan',
    username: '@mikachan',
    messagePreview: 'Doing well, thank...',
    newMessages: 3,
    timeLastSeen: '6h',
  },
  {
    name: 'Mika-chan2',
    username: '@mikachan2',
    messagePreview: 'Doing well, thank...',
    newMessages: 14,
    timeLastSeen: '22 May',
  },
]

export default function Characters() {
  // active character state
  const [activeUsername, setActiveUsername] = useState<string>(
    messages[0].username
  )

  const handleUpdateUsername = (username: string) => {
    setActiveUsername(username)
  }

  // search state
  const [isInputActive, setInputActive] = useState(false)
  const handleInputFocus = () => setInputActive(true)
  const handleInputBlur = () => setInputActive(false)

  const sidebarRef = useRef<HTMLDivElement | null>(null)

  return (
    <div
      ref={sidebarRef}
      className={`flex flex-col w-[375px] flex-grow border-r-[2px] border-[#252525] bg-[#121212] text-white`}
      style={{ height: 'calc(100vh)' }}
    >
      <div className='flex items-center px-4 justify-between py-6'>
        <div className='flex items-center cursor-pointer '>
          <div className='h-8 w-8 relative'>
            <Image
              src='/clonr-logo.png'
              alt='logo'
              layout='fill'
              objectFit='cover'
              className=''
            />
          </div>
        </div>
        <div className='cursor-pointer text-white h-[40px] w-[40px] bg-[#979797] rounded-full grid place-items-center hover:ring-1 hover:ring-[rgba(255,255,255,0.2)] '>
          J
        </div>
        {/* <div className='w-8 flex'>
          <HorizontalDots />
        </div> */}
        <div className='z-50'>
          <CharacterDropdown />
        </div>
      </div>
      <div
        className={` flex w-[375px] min-w-[375px] max-w-[375px] items-center gap-x-2 pb-4`}
      >
        <div className='relative w-full'>
          <div className='absolute left-4 top-3'>
            <SearchIcon
              strokeClasses={`${
                isInputActive ? 'stroke-[#5848BC]' : 'stroke-[#515151]'
              } transition duration-100`}
              // strokeClasses='stroke-[#515151]'
            />
          </div>
          <input
            onFocus={handleInputFocus}
            onBlur={handleInputBlur}
            className='py-auto h-[48px] w-full border-none bg-[#1E1E1E] pl-[50px] text-[15px] font-light leading-6 text-[#979797] transition duration-100 focus:ring-1 focus:ring-transparent'
            type='text'
            placeholder='Search'
            style={{ outline: 'none', resize: 'none' }}
          />
        </div>
      </div>

      <div className='sticky top-[154px] overflow-auto transition-all duration-100 h-full'>
        {messages.map((message) => (
          <Character
            key={message.username}
            isActive={message.username === activeUsername}
            name={message.name}
            username={message.username}
            messagePreview={message.messagePreview}
            newMessages={message.newMessages}
            timeLastSeen={message.timeLastSeen}
            onClick={handleUpdateUsername}
          />
        ))}
      </div>
    </div>
  )
}