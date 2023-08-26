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
  console.log("In CharacterComponent, this is characterChat: ", characterChat)
  console.log("In CharacterComponent, this is currentCharacterId: ", currentCharacterId)
  return (
    <Link
      href={`/chat/${characterChat.character.id}/${characterChat.lastConversationId}`}
    >
      <div
        className={`${characterChat.character.id === currentCharacterId
            ? ' border-[#252525] bg-[#282348]'
            : 'border-[#252525] bg-[#121212]'
          } border-r-none cursor-pointer border-b px-0`}
      >
        <div className='flex items-center justify-between px-4 py-[22px]'>
          <div className='flex items-center'>
            {/* <Image
              key={0}
              src={characterChat.character.avatar_uri} 
              alt={`Character Profile Picture ${0 + 1}`}
              width={40}
              height={40}
              className='rounded-full'
            /> */}
            <div className='h-[55px] w-[55px] relative'>
              <Image
                src={characterChat.character.avatar_uri}
                alt='Character Profile Picture'
                layout='fill'
                objectFit='cover'
                className='rounded-full'
              />
            </div>
            <div className='ml-3 flex flex-col'>
              <div className='mb-1 flex items-center'>
                <h3 className='mr-2 text-[16px] font-bold leading-[22px]'>
                  {characterChat.character.name}
                </h3>
                <h4 className='text-sm font-light leading-[18px] text-[#979797]'>
                  {/* {username} */}
                  {' • ' + formatDate(new Date(characterChat.character.updated_at))}
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
