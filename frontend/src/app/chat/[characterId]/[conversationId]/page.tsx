'use client'

import Characters from '@/components/ChatPage/Characters'
import ChatScreen from '@/components/ChatPage/Chat'
import { Character } from '@/types'
import useClones from '@/hooks/useClones'
import useConversations from '@/hooks/useConversations'
import { useEffect, useState } from 'react'

const { queryClones, queryCloneById } = useClones()

const {createConversation, queryConversation, queryConversationMessages, createMessage, generateCloneMessage, queryCurrentRevisions} = useConversations();


async function getCharacterDetails(
  characterId: string,
  conversationId: string
) {
  const charDetails = await queryCloneById(characterId)
  return charDetails
}

async function getCharacterPastChats(
  characterId: string,
  conversationId: string
) {
  const charDetails = await queryConversationMessages(conversationId)
  return charDetails
}

async function getInitialMessages(characterId: string, conversationId: string) {
  console.log('characterID', characterId)
  return [
    {
      id: '12353223iy4',
      img: '/dummy-char.png',
      alt: 'dummy-char',
      content: 'Test first message?',
      created_at: new Date(),
      updated_at: new Date(),
      sender_name: 'Test',
      timestamp: new Date(),
      is_clone: true,
      is_main: true,
      is_active: true,
      parent_id: '',
      clone_id: characterId,
      user_id: '41238967-9489-400d-9616-4bcacfb9140', // TODO: edit
      conversation_id: conversationId,
    },
  ]
}

export default async function ChatPage({
  params,
}: {
  params: { characterId: string; conversationId: string }
}) {

  const [character, setCharacter] = useState(null);
  const [characterChats, setCharacterChats] = useState([]);
  const [initialMessages, setInitialMessages] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const charDetails = await queryCloneById(params.characterId);
        setCharacter(charDetails);

        const chats = await getCharacterPastChats(
          params.characterId,
          params.conversationId
        );
        setCharacterChats(chats);

        const messages = await getCharacterPastChats(
          params.characterId,
          params.conversationId
        );
        setInitialMessages(messages);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [params.characterId, params.conversationId]); 


  // fetch previous 20 messages for chat screen
  // fetch 10 previous chats for character screen

  // pagination for fetching more chats on scroll up
  // pagination for fetching more characters on scroll down
  return (
    <div>
      {/* <TopBar /> */}
      <div
        className='bg-gray-900 w-full flex justify-center items-center overflow-hidden'
        style={{ height: 'calc(100vh)' }}
      >
        <Characters
          initialCharacterChats={characterChats}
          currentCharacterId={params.characterId}
        />
        <ChatScreen
          characterId={params.characterId}
          character={character ? character : null}
          // need initial 20 msgs
          // need initial 10 characters

          initialMessages={initialMessages}
          conversationId={params.conversationId}
          initialConversationState={
            'short term'
            //character && character.name === 'Barack Obama' ? 'undecided' : 'short term'
          }
        />
      </div>
    </div>
  )
}
