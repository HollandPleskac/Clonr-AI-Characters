import React from 'react'
import MagnifyingGlass from '@/svg/ChatPage/Chat/magnify.svg'
import Paperclip from '@/svg/ChatPage/Chat/paperclip.svg'
import ChatDropdown from './DropdownChat'
import Image from 'next/image'
import { Character, CharacterChat } from '@/types'
import Link from 'next/link'
import SmallNav from '../Characters/SmallSidebar'


type ChatTopBarProps = {
  isInputActive: boolean
  onSearchInput: (x:string) => void
  searchInput: string
  character: Character
  inputRef: React.RefObject<HTMLInputElement>
  handleInputFocus: () => void
  handleInputBlur: () => void
  characterId: string
  conversationId: string
  toggleRemoveMode: () => void
}

const ChatTopBar = ({
  isInputActive,
  onSearchInput,
  searchInput,
  character,
  inputRef,
  handleInputBlur,
  handleInputFocus,
  characterId,
  conversationId,
  toggleRemoveMode
}: ChatTopBarProps) => {
  if (!character) {
    return (
      <div> Loading character.. </div>
    )
  }

  return (
    <div className='flex h-[122px] w-full items-center justify-between border-b border-[#252525] px-10'>
      <div className='flex items-center'>
        <SmallNav characterId={characterId} />
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
            <p className='text-gray-400 text-sm line-clamp-1'>
              {character.short_description}
            </p>
          </div>
        ) : (
          <p>Loading character</p>
        )}


      </div>
        <div className='flex items-center gap-x-4'>
          <div className='relative group'>
            <button
              onClick={() => {
                if (inputRef.current) {
                  inputRef.current.focus()
                }
              }}
              className='group absolute peer left-[10px] top-2 peer cursor-default hover:cursor-pointer'
            >
              <MagnifyingGlass />

            </button>
            <input
              ref={inputRef}
              value={searchInput}
              onChange={(e) => onSearchInput(e.target.value)}
              onFocus={handleInputFocus}
              onBlur={handleInputBlur}
              className={` ${isInputActive
                ? 'w-[300px] cursor-auto bg-gray-700'
                : 'w-[44px] cursor-default bg-gray-800'
                }
              py-auto h-[40px] transition-all  duration-500 rounded-full border-none pr-0 pl-[44px] text-[15px] font-light leading-6 text-[#979797] focus:ring-1 focus:ring-transparent`}
              type='text'
              placeholder='Search'
              style={{ outline: 'none', resize: 'none' }}
            />
          </div>

          <ChatDropdown characterId={character.id} toggleRemoveMode={toggleRemoveMode} />
        </div>
     
    </div>
  )
}

export default ChatTopBar
