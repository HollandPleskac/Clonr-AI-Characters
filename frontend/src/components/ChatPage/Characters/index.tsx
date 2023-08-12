'use client'

import React, { useEffect, useRef, useState } from 'react'
import Image from 'next/image'
import SearchIcon from './SearchIcon'
import CharacterComponent from './Character'
import CharacterDropdown from './CharacterDropdown'
import { CharacterChat } from '@/types'
import { formatDate } from '@/utils/formatDate'
import Link from 'next/link'

interface CharactersProps {
  initialCharacterChats: CharacterChat[]
  currentCharacterId: string
}

export default function Characters({
  initialCharacterChats,
  currentCharacterId,
}: CharactersProps) {
  const [characterChats, setCharacterChats] = useState<CharacterChat[]>(
    initialCharacterChats
  )

  // OPTIONAL: FETCH initialCharacterChats client side here
  // type: CharacterChat (see @/types)
  // want to sync this type up with backend
  // useEffect(() => {
  // },[])

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
          {/* <div className='h-8 w-8 relative'>
            <Image
              src='/clonr-logo.png'
              alt='logo'
              layout='fill'
              objectFit='cover'
              className=''
            />
          </div> */}
          <Link href='/' className='flex items-center cursor-pointer'>
            <div className='h-8 w-8 relative'>
              <Image
                src='/clonr-logo.png'
                alt='logo'
                layout='fill'
                objectFit='cover'
                className=''
              />
            </div>
            <h3 className='ml-2 text-[30px] font-semibold leading-5 text-white font-fabada'>
              clonr
            </h3>
            <p className='text-white font-thin ml-2 align-middle'>users</p>
          </Link>
        </div>
        {/* <div className='cursor-pointer text-white h-[40px] w-[40px] bg-[#979797] rounded-full grid place-items-center hover:ring-1 hover:ring-[rgba(255,255,255,0.2)] '>
          J
        </div> */}
        {/* <div className='w-8 flex'>
          <HorizontalDots />
        </div> */}
        {/* <div className='z-50'>
          <CharacterDropdown />
        </div> */}
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
        {characterChats.map((charChat) => (
          <CharacterComponent
            key={charChat.character.id}
            characterChat={charChat}
            currentCharacterId={currentCharacterId}
          />
        ))}
      </div>
    </div>
  )
}
