'use client'

import React from 'react'
import HorizontalDotsBig from '@/svg/ChatPage/Chat/horizontal-dots-big.svg'
import Image from 'next/image'
import useConversations from '@/hooks/useConversations'
import { Character, Message } from '@/types'
import { useEffect, useState } from 'react'
//import { useHistory } from 'react-router-dom';

const {createConversation, queryConversation, queryConversationMessages, createMessage, generateCloneMessage, queryCurrentRevisions} = useConversations();


type ChooseChatExperienceProps = {
  characterId: string
  character: Character
  setConversationState: (newState: string) => void
  setConvoID: (newID: string) => void
}

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

const ChooseChatExperience = ({characterId, character, setConversationState, setConvoID}: ChooseChatExperienceProps) => {
  if (!character) {
    return <div>Loading character..</div>
  }
  const [conversationID, setConversationID] = useState('')
  //const history = useHistory();
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
            {character.num_conversations} Chats
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
            {character.name}
          </h2>
          <p className='mb-5 text-lg text-gray-400'>
            {character.short_description}{' '}
          </p>
          <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
            Long Description
          </h2>
          <p className='mb-5 text-gray-400 lime-clamp-3'>
            TODO: include long description in route
          </p>
          <button
            onClick={async () => {
              setConversationState('short term')
              const conversationId = await createCharacterConversation(characterId, 'short_term')
              setConversationID(conversationId)
              setConvoID(conversationId)
              const new_url = `http://localhost:3000/chat/${characterId}/${conversationId}`
              window.location.href = new_url
              //history.push(`/chat/${characterId}/${conversationId}`);
            }}
            className='flex items-center justify-between w-full py-2 px-4 inline-flex bg-purple-500 rounded-lg hover:bg-purple-600 text-white'
          >
            Start Short Term Memory Chat
          </button>
          <button
            onClick={async () => {
              setConversationState('long term')
              const conversationId = await createCharacterConversation(characterId, 'long_term')
              setConversationID(conversationId)
              setConvoID(conversationId)
              const new_url = `http://localhost:3000/chat/${characterId}/${conversationId}`
              window.location.href = new_url
              //history.push(`/chat/${characterId}/${conversationId}`);
            }}
            className='mt-2 flex items-center justify-between w-full py-2 px-4 inline-flex bg-purple-500 rounded-lg hover:bg-purple-600 text-white'
          >
            Start Long Term Memory Chat
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChooseChatExperience
