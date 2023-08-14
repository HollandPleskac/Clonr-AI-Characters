import Characters from '@/components/ChatPage/Characters'
import ChatScreen from '@/components/ChatPage/Chat'
import { Character } from '@/types'

async function getCharacterDetails(
  characterId: string,
  conversationId: string
) {
  if (characterId === '12345') {
    return {
      id: '12345',
      created_at: 'string',
      updated_at: 'string',
      creator_id: 'string',
      name: 'Barack Obama',
      short_description: 'short description',
      avatar_uri: '/dummy-char.png',
      num_messages: 2134,
      num_conversations: 234,
      tags: [
        {
          id: '123',
          created_at: new Date(),
          updated_at: new Date(),
          color_code: '#853838',
          name: 'Politician'
        }
      ]
    }
  } else {
    return {
      id: '54321',
      created_at: 'string',
      updated_at: 'string',
      creator_id: 'string',
      name: 'Elon Musk',
      short_description: 'CEO',
      avatar_uri: '/dummy-char.png',
      num_messages: 2134,
      num_conversations: 234,
      tags: [
        {
          id: '123',
          created_at: new Date(),
          updated_at: new Date(),
          color_code: '#853838',
          name: 'CEO'
        }
      ]
    }
  }
}

async function getCharacterPastChats() {
  return [
    {
      character: {
        id: '12345',
        created_at: 'string',
        updated_at: 'string',
        creator_id: 'string',
        name: 'Barack Obama',
        short_description: 'short description',
        avatar_uri: '/dummy-char.png',
        num_messages: 2134,
        num_conversations: 234,
        tags: [
          {
            id: '123',
            created_at: new Date(),
            updated_at: new Date(),
            color_code: '#853838',
            name: 'Politician'
          }
        ]
      },
      lastMessage: "Why can't I just eat my waffle?",
      lastConversationId: '123',
    },
    {
      character: {
        id: '54321',
        created_at: 'string',
        updated_at: 'string',
        creator_id: 'string',
        name: 'Elon Musk',
        short_description: 'CEO',
        avatar_uri: '/dummy-char.png',
        num_messages: 2134,
        num_conversations: 234,
        tags: [
          {
            id: '123',
            created_at: new Date(),
            updated_at: new Date(),
            color_code: '#853838',
            name: 'CEO'
          }
        ]
      },
      lastMessage: 'Next I’m buying Coca-Cola to put the cocaine back in',
      lastConversationId: '1234',
    },
  ]
}

async function getInitialMessages(characterId: string, conversationId: string) {
  console.log('characterID', characterId)
  return [
    {
      id: '12345323',
      content: 'string',
      created_at: 'string',
      updated_at: 'string',
      sender_name: 'string',
      timestamp: 'string',
      is_clone: true,
      is_main: true,
      is_active: true,
      parent_id: '123',
      clone_id: '123',
      user_id: '13432',
      conversation_id: '3243',
    },
    {
      id: '123asdf45',
      content: 'string',
      created_at: 'string',
      updated_at: 'string',
      sender_name: 'string',
      timestamp: 'string',
      is_clone: true,
      is_main: true,
      is_active: true,
      parent_id: '123',
      clone_id: '123',
      user_id: '13432',
      conversation_id: '3243',
    },
    {
      id: '1243r345',
      content: 'string',
      created_at: 'string',
      updated_at: 'string',
      sender_name: 'string',
      timestamp: 'string',
      is_clone: true,
      is_main: true,
      is_active: true,
      parent_id: '123',
      clone_id: '123',
      user_id: '13432',
      conversation_id: '3243',
    },
    {
      id: '1234asdf5',
      content: 'string',
      created_at: 'string',
      updated_at: 'string',
      sender_name: 'string',
      timestamp: 'string',
      is_clone: true,
      is_main: true,
      is_active: true,
      parent_id: '123',
      clone_id: '123',
      user_id: '13432',
      conversation_id: '3243',
    },
    {
      id: '1234adf5',
      content: 'string',
      created_at: 'string',
      updated_at: 'string',
      sender_name: 'string',
      timestamp: 'string',
      is_clone: true,
      is_main: true,
      is_active: true,
      parent_id: '123',
      clone_id: '123',
      user_id: '13432',
      conversation_id: '3243',
    },
    {
      id: '12fdas345',
      content: 'string',
      created_at: 'string',
      updated_at: 'string',
      sender_name: 'string',
      timestamp: 'string',
      is_clone: true,
      is_main: true,
      is_active: true,
      parent_id: '123',
      clone_id: '123',
      user_id: '13432',
      conversation_id: '3243',
    },
    {
      id: 'adsfdasfdsa',
      content: 'string',
      created_at: 'string',
      updated_at: 'string',
      sender_name: 'string',
      timestamp: 'string',
      is_clone: true,
      is_main: true,
      is_active: true,
      parent_id: '123',
      clone_id: '123',
      user_id: '13432',
      conversation_id: '3243',
    },
    {
      id: '12asf345',
      content: 'string',
      created_at: 'string',
      updated_at: 'string',
      sender_name: 'string',
      timestamp: 'string',
      is_clone: true,
      is_main: true,
      is_active: true,
      parent_id: '123',
      clone_id: '123',
      user_id: '13432',
      conversation_id: '3243',
    },
  ]
}

export default async function ChatPage({
  params,
}: {
  params: { characterId: string; conversationId: string }
}) {
  // get character for chat screen
  const character = await getCharacterDetails(
    params.characterId,
    params.conversationId
  )
  const characterChats = await getCharacterPastChats()
  const initialMessages = await getInitialMessages(
    params.characterId,
    params.conversationId
  )

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
            character.name === 'Barack Obama' ? 'undecided' : 'short term'
          }
        />
      </div>
    </div>
  )
}
