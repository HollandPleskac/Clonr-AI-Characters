import React from 'react'
import MagnifyingGlass from '@/svg/ChatPage/Chat/magnify.svg'
import Paperclip from '@/svg/ChatPage/Chat/paperclip.svg'
import ChatDropdown from './Dropdown'
import Image from 'next/image'
import { Character, CharacterChat } from '@/types'
import Link from 'next/link'
import SmallNav from '../Characters/SmallSidebar'


type ChatTopBarProps = {
  character: Character
  inputRef: React.RefObject<HTMLInputElement>
  isInputActive: boolean
  handleInputFocus: () => void
  handleInputBlur: () => void
  toggleChatState: () => void
  showChat: boolean
  characterId: string
  conversationId: string
}

const ChatTopBar = ({
  character,
  inputRef,
  handleInputBlur,
  handleInputFocus,
  toggleChatState,
  showChat,
  characterId,
  conversationId
}: ChatTopBarProps) => {
  return (
    <div className='flex h-[122px] w-full items-center justify-between border-b border-[#252525] px-10'>
      <div className='flex items-center'>
        <SmallNav characterId={characterId} conversationId={conversationId} character={character} />
        <div className='h-[55px] w-[55px] relative'>
          <Image
            src={character.avatar_uri}
            alt='Character Profile Picture'
            layout='fill'
            objectFit='cover'
            className='rounded-full'
          />
        </div>

        {character ? (
          <div className='flex flex-col ml-6 gap-y-3'>
            <h3 className='text-3xl font-bold leading-5 text-white'>
              {character.name}
            </h3>
            {/* <p className='text-gray-400 text-sm line-clamp-1'>
              {character.short_description}
            </p> */}
          </div>
        ) : (
          <p>Loading character</p>
        )}


      </div>
      {showChat && (
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
              <MagnifyingGlass />

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

          <ChatDropdown toggleChatState={toggleChatState} showChat={showChat} characterId={character.id} />
        </div>
      )}
      {!showChat && (
        <button
          onClick={toggleChatState}
          className='px-4 py-2 bg-gray-800 hover:bg-gray-700 text-[#D1D5DB] rounded-lg transition duration-200'
        >
          Back to Current Chat
        </button>
      )}
    </div>
  )
}

export default ChatTopBar
