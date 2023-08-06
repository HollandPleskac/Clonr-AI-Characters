import Characters from '@/components/ChatPage/Characters'
import ChatScreen from '@/components/ChatPage/Chat'
import { Character } from '@/types'

async function getCharacterDetails() {
  return {
    id: 'string',
    created_at: new Date(),
    updated_at: new Date(),
    creator_id: 'string',
    name: 'string',
    short_description: 'string',
    avatar_uri: 'string',
    num_messages: 234234,
    num_conversations: 3423,
    tags: ['tag1', 'tag2'],
  }
}

async function getInitialCharacterChats() {
  return [
    {
      character: {
        id: 'string',
        created_at: new Date(),
        updated_at: new Date(),
        creator_id: 'string',
        name: 'string',
        short_description: 'string',
        avatar_uri: 'string',
        num_messages: 234234,
        num_conversations: 3423,
        tags: ['tag1', 'tag2'],
      },
      lastMessage: 'string',
    },
    {
      character: {
        id: 'string',
        created_at: new Date(),
        updated_at: new Date(),
        creator_id: 'string',
        name: 'string',
        short_description: 'string',
        avatar_uri: 'string',
        num_messages: 234234,
        num_conversations: 3423,
        tags: ['tag1', 'tag2'],
      },
      lastMessage: 'string',
    },
  ]
}

async function getInitialMessages() {
  return [
    {
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'bot' as 'bot' | 'user',
    },
    {
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'user' as 'bot' | 'user',
    },
    {
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'bot' as 'bot' | 'user',
    },
    {
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'user' as 'bot' | 'user',
    },
    {
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'bot' as 'bot' | 'user',
    },
    {
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'user' as 'bot' | 'user',
    },
    {
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'bot' as 'bot' | 'user',
    },
    {
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'user' as 'bot' | 'user',
    },
  ]
}

export default async function ChatPage({
  params,
}: {
  params: { characterId: string; conversationId: string }
}) {
  // get character for chat screen
  const initialCharacter = await getCharacterDetails()
  const initialCharacterChats = await getInitialCharacterChats()
  const initialMessages = await getInitialMessages()

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
        <Characters initialCharacterChats={initialCharacterChats} />
        <ChatScreen
          characterId={params.characterId}
          initialCharacter={initialCharacter}
          // need initial 20 msgs
          // need initial 10 characters

          initialMessages={initialMessages}
          conversationId={params.conversationId}
        />
      </div>
    </div>
  )
}
