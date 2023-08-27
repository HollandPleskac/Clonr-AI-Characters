import React from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { CharacterChat } from '@/types'
import { formatDate } from '@/utils/formatDate'

interface MyComponentProps {
  characterChat: CharacterChat
  currentCharacterId: string
}
const Character: React.FC<MyComponentProps> = ({
  characterChat,
  currentCharacterId,
}) => {
  return (
    <Link
      href={`/chat/${characterChat.characterId}/${characterChat.lastConversationId}`}
    >
      <div
        className={`${characterChat.characterId === currentCharacterId
            ? ' border-[#252525] bg-[#282348]'
            : 'border-[#252525] bg-[#121212]'
          } border-r-none cursor-pointer border-b px-0`}
      >
        <div className='flex items-center justify-between px-4 py-[22px]'>
          <div className='flex items-center'>
            <div className='h-[55px] w-[55px] relative'>
              <Image
                src={characterChat.characterAvatarUri}
                alt='Character Profile Picture'
                layout='fill'
                objectFit='cover'
                className='rounded-full'
              />
            </div>
            <div className='ml-3 flex flex-col'>
              <div className='mb-1 flex items-center'>
                <h3 className='mr-2 text-[16px] font-bold leading-[22px]'>
                  {characterChat.characterName}
                </h3>
                <h4 className='text-sm font-light leading-[18px] text-[#979797]'>
                  {/* {username} */}
                  {' • ' + formatDate(new Date(characterChat.lastUpdatedAt))}
                </h4>
              </div>
              <div className='text-smibold text-[14px] leading-[18px] line-clamp-1'>
                {characterChat.lastMessage}
              </div>
            </div>
          </div>
          <div className='grid w-6 place-items-center rounded-[10px] bg-[#3E347E] py-[2px] text-[12px] font-semibold leading-[16px]'>
            {3}
          </div>
        </div>
      </div>
    </Link>
  )
}

export default Character
