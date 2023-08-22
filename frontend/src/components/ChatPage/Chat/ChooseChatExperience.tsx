'use client'

import React from 'react'
import HorizontalDotsBig from '@/svg/ChatPage/Chat/horizontal-dots-big.svg'
import Image from 'next/image'
import useConversations from '@/hooks/useConversations'
import { Character, CharacterChat, Message } from '@/types'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
//import { useHistory } from 'react-router-dom';
import Paperclip from '@/svg/ChatPage/Chat/paperclip.svg'
import ChatPopover from './ChatPopover'
import MagnifyingGlass from '@/svg/ChatPage/Chat/magnify.svg'
import SmallNav from '../Characters/SmallSidebar'
import { initScriptLoader } from 'next/script'
import TagsComponent from '@/components/HomePage/Tags'
const { createConversation, queryConversation, queryConversationMessages, createMessage, generateCloneMessage, queryCurrentRevisions } = useConversations();

type ChooseChatExperienceProps = {
  characterId: string
  character: Character
  setConversationState: (newState: string) => void
  setConvoID: (newID: string) => void
  initialCharacterChats: CharacterChat[],
  currentCharacterId: string
}

const tags = [
  {
    id: '1',
    created_at: new Date(),
    updated_at: new Date(),
    color_code: '48FF83',
    name: "Anime"
  }, {
    id: '2',
    created_at: new Date(),
    updated_at: new Date(),
    color_code: 'FF0392',
    name: "Warrior"
  },
  , {
    id: '2',
    created_at: new Date(),
    updated_at: new Date(),
    color_code: 'DD04FF',
    name: "Female"
  }
]

async function createCharacterConversation(
  characterId: string,
  memoryStrategy: string,
) {
  const conversationCreateData = {
    name: 'Test Conversation',
    user_name: 'Test User',
    memory_strategy: memoryStrategy,
    information_strategy: 'internal',
    adaptation_strategy: null,
    clone_id: characterId,
  }
  const conversationId = await createConversation(conversationCreateData)
  return conversationId
}

const ChooseChatExperience = ({ characterId, character, setConversationState, setConvoID, initialCharacterChats, currentCharacterId }: ChooseChatExperienceProps) => {
  if (!character) {
    return <div>Loading character..</div>
  }
  const [conversationID, setConversationID] = useState('')
  //const history = useHistory();
  const router = useRouter();
  return (
    <div
      className='h-full flex flex-col gap-x-8'
      style={{ height: 'calc(100vh)' }}
    >
      <div className='flex h-[122px] w-full items-center justify-between border-b border-[#252525] px-10'>
        <div className='flex items-center'>
          <SmallNav initialCharacterChats={initialCharacterChats} currentCharacterId={currentCharacterId} />
          {/* <Image
            key={0}
            src={character.avatar_uri}
            alt={`Character Profile Picture ${0 + 1}`}
            width={55}
            height={55}
            className='rounded-full'
          /> */}

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
        <div className='flex items-center gap-x-4'>
          <button
            onClick={() => {
            }}
            className='bg-gray-800 hover:bg-gray-700 rounded-full p-2 grid place-items-center transition duration-200 cursor-not-allowed'
          >
            <MagnifyingGlass />

          </button>
          <button className='bg-gray-800 hover:bg-gray-700 rounded-full p-2 grid place-items-center transition duration-200 cursor-not-allowed'>
            <Paperclip />
          </button>

          <button
            className='hs-dropdown-toggle inline-flex justify-center items-center bg-gray-800 hover:bg-gray-700 rounded-full p-2 transition duration-200 cursor-not-allowed'
          >
            <HorizontalDotsBig />
          </button>
        </div>
      </div>


      {/* <div className='flex flex-col px-[4%] justify-center my-auto ' >
        <h1 className='text-2xl font-bold md:text-4xl text-white mb-8'>
          How do you want to chat?
        </h1>

        <div className='flex gap-x-8 ' >
          <div className="flex flex-col bg-white border shadow-sm rounded-xl p-4 md:p-5 dark:bg-gray-800 dark:border-gray-700 dark:shadow-slate-700/[.7]">
            <h3 className="text-lg font-bold text-gray-800 dark:text-white">
              Short Term Memory Chat
            </h3>
            <p className="mt-1 text-xs font-medium uppercase text-gray-500 dark:text-gray-500">
              Casual Interactions
            </p>
            <p className="mt-2 text-gray-800 dark:text-gray-400">
              Perfect for lighthearted chats and spontaneous fun. Doesn't retain information, ensuring fresh interactions every time.
            </p>
            <a className="mt-3 inline-flex items-center gap-2 mt-5 text-sm font-medium text-blue-500 hover:text-blue-700" href="#">
                Start Chat
                <svg className="w-2.5 h-auto" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 1L10.6869 7.16086C10.8637 7.35239 10.8637 7.64761 10.6869 7.83914L5 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                </svg>
              </a>
          </div>

          <div className="flex flex-col bg-white border shadow-sm rounded-xl p-4 md:p-5 dark:bg-gray-800 dark:border-gray-700 dark:shadow-slate-700/[.7]">
            <h3 className="text-lg font-bold text-gray-800 dark:text-white">
              Long Term Memory Chat
            </h3>
            <p className="mt-1 text-xs font-medium uppercase text-gray-500 dark:text-gray-500">
              Deep Conversations
            </p>
            <p className="mt-2 text-gray-800 dark:text-gray-400">
              Best suited for in-depth discussions and building relationships. Retains conversation history for meaningful engagements.
            </p>
            <a className="mt-3 inline-flex items-center gap-2 mt-5 text-sm font-medium text-blue-500 hover:text-blue-700" href="#">
                Start Chat
                <svg className="w-2.5 h-auto" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 1L10.6869 7.16086C10.8637 7.35239 10.8637 7.64761 10.6869 7.83914L5 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                </svg>
              </a>
          </div>


        </div>
      </div> */}



      <div className='overflow-auto pb-[40px] md:pb-0 flex flex-col md:flex-row gap-x-[48px] items-center md:items-start md:justify-center my-auto mt-[80px] md:mt-auto'>
        <div className='w-[50%] md:w-[240px] flex flex-col mb-8 md:mb-0'>
          <div className='h-[240px] w-full md:w-[240px] relative'>
            <Image
              src={character.avatar_uri}
              alt='logo'
              layout='fill'
              objectFit='cover'
              className='rounded-lg mb-5'
            />
          </div>

          <h2 className='text-lg text-center text-left my-4 font-light text-gray-500'>
            {character.num_conversations} Chats
          </h2>

          <button
            onClick={async () => {
              setConversationState('short term')
              const conversationId = await createCharacterConversation(characterId, 'short_term')
              // setConversationID(conversationId)
              // setConvoID(conversationId)
              const new_url = `http://localhost:3000/chat/${characterId}/${conversationId}`
              router.push(new_url)
            }}
            className='flex items-center justify-between w-full py-2 px-4 inline-flex bg-purple-500 rounded-lg hover:bg-purple-600 text-white'
          >
            Short Term Memory Chat
            <ChatPopover />
          </button>
          <button
            onClick={async () => {
              setConversationState('long term')
              const conversationId = await createCharacterConversation(characterId, 'long_term')
              const new_url = `http://localhost:3000/chat/${characterId}/${conversationId}`
              router.push(new_url)
            }}
            className='mt-2 flex items-center justify-between w-full py-2 px-4 inline-flex bg-purple-500 rounded-lg hover:bg-purple-600 text-white'
          >
            Long Term Memory Chat
            <ChatPopover />
          </button>
        </div>
        <div className='w-[50%] md:w-1/3 flex flex-col justify-start'>
          <h2 className='text-lg sm:text-4xl font-semibold mb-4 text-white'>
            {character.name}
          </h2>
          <TagsComponent tags={tags} />
          <p className='mb-4 mt-4 text-lg text-gray-400'>
            {character.short_description}{' '}
          </p>

          <h2 className='text-lg mb-2 sm:text-xl font-semibold text-white flex justify-start gap-x-2  items-center'>
            Long Description
            <svg className='cursor-pointer' fill="#fff" width="22px" height="22px" viewBox="0 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg" stroke="#fff">
              <g id="SVGRepo_bgCarrier" stroke-width="0" />
              <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round" />
              <g id="SVGRepo_iconCarrier"> <title>popout</title> <path d="M15.694 13.541l2.666 2.665 5.016-5.017 2.59 2.59 0.004-7.734-7.785-0.046 2.526 2.525-5.017 5.017zM25.926 16.945l-1.92-1.947 0.035 9.007-16.015 0.009 0.016-15.973 8.958-0.040-2-2h-7c-1.104 0-2 0.896-2 2v16c0 1.104 0.896 2 2 2h16c1.104 0 2-0.896 2-2l-0.074-7.056z" /> </g>
            </svg>
          </h2>
          <p className='text-gray-400 line-clamp-3' >
            {character.long_description}{' '}
          </p>
          <h2 className='text-lg mb-2 mt-4 sm:text-xl font-semibold text-white flex justify-start gap-x-2  items-center'>
            Greeting Message
            <svg className='cursor-pointer' fill="#fff" width="22px" height="22px" viewBox="0 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg" stroke="#fff">
              <g id="SVGRepo_bgCarrier" stroke-width="0" />
              <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round" />
              <g id="SVGRepo_iconCarrier"> <title>popout</title> <path d="M15.694 13.541l2.666 2.665 5.016-5.017 2.59 2.59 0.004-7.734-7.785-0.046 2.526 2.525-5.017 5.017zM25.926 16.945l-1.92-1.947 0.035 9.007-16.015 0.009 0.016-15.973 8.958-0.040-2-2h-7c-1.104 0-2 0.896-2 2v16c0 1.104 0.896 2 2 2h16c1.104 0 2-0.896 2-2l-0.074-7.056z" /> </g>
            </svg>
          </h2>
          <p className='text-gray-400 line-clamp-3' >
            {character.long_description}{' '}
          </p>

        </div>
      </div>
    </div>
  )
}

export default ChooseChatExperience



// Alternative Cards

{/* <div className="flex flex-col bg-white border shadow-sm rounded-xl dark:bg-gray-800 dark:border-gray-700 dark:shadow-slate-700/[.7]">
            <div className="p-4 md:p-5">
              <h3 className="text-lg font-bold text-gray-800 dark:text-white">
              Short Term Memory Chat
              </h3>
              <p className="mt-2 text-gray-800 dark:text-gray-400">
              Perfect for lighthearted chats and spontaneous fun. Doesn't retain information, ensuring fresh interactions every time.
              </p>
              <a className="mt-3 inline-flex items-center gap-2 mt-5 text-sm font-medium text-blue-500 hover:text-blue-700" href="#">
                Start Chat
                <svg className="w-2.5 h-auto" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 1L10.6869 7.16086C10.8637 7.35239 10.8637 7.64761 10.6869 7.83914L5 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                </svg>
              </a>
            </div>
          </div>

          <div className="flex flex-col bg-white border shadow-sm rounded-xl dark:bg-gray-800 dark:border-gray-700 dark:shadow-slate-700/[.7]">
            <div className="p-4 md:p-5">
              <h3 className="text-lg font-bold text-gray-800 dark:text-white">
                Long Term Memory Chat
              </h3>
              <p className="mt-2 text-gray-800 dark:text-gray-400">
                Best suited for in-depth discussions and building relationships. Retains conversation history for meaningful engagements.
              </p>
              <a className="mt-3 inline-flex items-center gap-2 mt-5 text-sm font-medium text-blue-500 hover:text-blue-700" href="#">
                Start Chat
                <svg className="w-2.5 h-auto" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 1L10.6869 7.16086C10.8637 7.35239 10.8637 7.64761 10.6869 7.83914L5 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                </svg>
              </a>
            </div>
          </div> */}