'use client'

import Characters from '@/components/ChatPage/Characters'
import ChatScreen from '@/components/ChatPage/Chat'
import { Character, CharacterChat } from '@/types'
import useClones from '@/hooks/useClones'
import useConversations from '@/hooks/useConversations'
import { useEffect, useState } from 'react'

const { queryCloneById } = useClones()

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

export default async function ChatPage({
  params,
}: {
  params: { characterId: string; conversationId: string }
}) {

  const [character, setCharacter] = useState<Character>(null);
  const [characterChats, setCharacterChats] = useState<CharacterChat[]>([]);
  const [initialMessages, setInitialMessages] = useState([]);
  const [initialConversationState, setInitialConversationState] = useState('undecided');
  //const [initial]

  useEffect(() => {
    const fetchData = async () => {
      try {
        const charDetails = await queryCloneById(params.characterId);
        setCharacter(charDetails);

        const chats = await getCharacterPastChats(
          params.characterId,
          params.conversationId
        );

        const characterChat = {
          character: charDetails,
          lastMessage: chats[chats.length - 1].content,
          lastConversationId: params.conversationId,
        }

        setCharacterChats([characterChat]);

        const messages = await getCharacterPastChats(
          params.characterId,
          params.conversationId
        );
        setInitialMessages(messages);
        
        const conversation = await queryConversation(params.conversationId);
        setInitialConversationState(conversation.memory_strategy);


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
          character={character}
          // need initial 20 msgs
          // need initial 10 characters

          initialMessages={initialMessages}
          conversationId={params.conversationId}
          initialConversationState={
            initialConversationState
            //'undecided'
            //'short_term'
            //'undecided'
            //'short term'
            //character && character.name === 'Barack Obama' ? 'undecided' : 'short term'
          }
        />
      </div>
    </div>
  )
}
