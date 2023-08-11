'use client'

import React from 'react'
import HorizontalDotsBig from '@/svg/ChatPage/Chat/horizontal-dots-big.svg'
import Image from 'next/image'
type ChooseChatExperienceProps = {
  setConversationState: (newState: string) => void
}

const ChooseChatExperience = ({setConversationState}: ChooseChatExperienceProps) => {
  return (
    <div
      className='h-full px-8 flex flex-col gap-x-8 justify-center items-start pt-8'
      style={{ height: 'calc(100vh)' }}
    >
      {/* <h1 className='text-2xl font-bold md:text-4xl text-white mb-8'>
            How do you want to chat?
          </h1> */}
      <div className='flex gap-x-8 justify-center'>
        <div className='w-[280px] flex flex-col'>
          <div className='h-[280px] w-[280px] relative'>
            <Image
              src='/barack2.jpeg'
              alt='logo'
              layout='fill'
              objectFit='cover'
              className='rounded-lg mb-5'
            />
          </div>
          <h2 className='text-xl text-left my-4 font-semibold text-gray-500'>
            22.3k Chats
          </h2>
          <div className='flex flex-wrap gap-2'>
            <button className='px-2 py-1 text-sm text-gray-600 border-2 border-gray-700 rounded-lg rounder-gray-800 hover:border-gray-700 hover:text-gray-600'>
              President
            </button>
            <button className='px-2 py-1 text-sm text-gray-600 border-2 border-gray-700 rounded-lg rounder-gray-800 hover:border-gray-700 hover:text-gray-600'>
              Male
            </button>
            <button className='px-2 py-1 text-sm text-gray-600 border-2 border-gray-700 rounded-lg rounder-gray-800 hover:border-gray-700 hover:text-gray-600'>
              Politician
            </button>
          </div>
        </div>
        <div className='w-1/3 flex flex-col justify-start'>
          <h2 className='text-lg sm:text-4xl font-semibold mb-4 text-white'>
            Barack Obama
          </h2>
          <p className='mb-5 text-lg text-gray-400'>
            I am Barack Obama, 44th President of the United States.{' '}
          </p>
          <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
            Long Description
          </h2>
          <p className='mb-5 text-gray-400 lime-clamp-3'>
            I am Barack Obama, 44th President of the United States. I am Barack
            Obama, 44th President of the United States. I am Barack Obama, 44th
            Presid...
          </p>
          <button
            onClick={() => {
              setConversationState('short_term')
            }}
            className='flex items-center justify-between w-full py-2 px-4 inline-flex bg-purple-500 rounded-lg hover:bg-purple-600 text-white'
          >
            Start Short Term Memory Chat
            <div>i</div>
          </button>
          <button
            onClick={() => {
              setConversationState('long term')
            }}
            className='mt-2 flex items-center justify-between w-full py-2 px-4 inline-flex bg-purple-500 rounded-lg hover:bg-purple-600 text-white'
          >
            Start Long Term Memory Chat
            <div>i</div>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChooseChatExperience