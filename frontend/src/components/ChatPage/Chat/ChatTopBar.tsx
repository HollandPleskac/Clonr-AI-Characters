import React from 'react'
import MagnifyingGlass from '@/svg/ChatPage/Chat/magnify.svg'
import Paperclip from '@/svg/ChatPage/Chat/paperclip.svg'
import ChatDropdown from './Dropdown'
import Image from 'next/image'
import { Character } from '@/types'
type ChatTopBarProps = {
  character: Character
  inputRef: React.RefObject<HTMLInputElement>
  isInputActive: boolean
  handleInputFocus: () => void
  handleInputBlur: () => void
  toggleChatState: () => void
}

const ChatTopBar = ({
  character,
  inputRef,
  isInputActive,
  handleInputBlur,
  handleInputFocus,
  toggleChatState,
}: ChatTopBarProps) => {
  return (
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

        <ChatDropdown toggleChatState={toggleChatState} />
      </div>
    </div>
  )
}

export default ChatTopBar
