'use client'
import React from 'react'
import MagnifyingGlass from '@/svg/ChatPage/Chat/magnify.svg'
import Paperclip from '@/svg/ChatPage/Chat/paperclip.svg'
import ChatDropdown from '../Chat/DropdownChat'
import Image from 'next/image'
import { Character, CharacterChat } from '@/types'
import Link from 'next/link'
import SmallNav from '../Characters/SmallSidebar'
import { useQueryClonesById } from '@/hooks/useClones'
import DropdownConversations from './DropdownConversations'


type ConversationsTopBarProps = {
  characterId: string
}

const ConversationsTopBar = ({
  characterId,
}: ConversationsTopBarProps) => {

  const queryParams = {
    cloneId: characterId
  }

  const { data: character, error, isLoading } = useQueryClonesById(queryParams);

  if (!character) {
    return (
      <div className='h-[122px]' > </div>
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
            {/* <p className='text-gray-400 text-sm line-clamp-1'>
              {character.short_description}
            </p> */}
          </div>
        ) : (
          <p>Loading character</p>
        )}


      </div>
      <DropdownConversations characterId={character.id} lastConversationId={"test"} />
    </div>
  )
}

export default ConversationsTopBar
