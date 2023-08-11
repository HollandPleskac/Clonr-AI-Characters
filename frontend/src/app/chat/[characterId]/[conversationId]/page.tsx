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
      created_at: new Date(),
      updated_at: new Date(),
      creator_id: '0987',
      name: 'Barack Obama',
      short_description:
        'I am Barack Obama, 44th President of the United States. ',
      avatar_uri: '/dummy-char.png',
      num_messages: 234234,
      num_conversations: 3423,
      tags: ['president', 'politician'],
    }
  } else {
    return {
      id: '23456',
      created_at: new Date(),
      updated_at: new Date(),
      creator_id: '0987',
      name: 'Elon Musk',
      short_description: "You're wasting my time. I literally rule the world.",
      avatar_uri: '/dummy-char.png',
      num_messages: 2342343,
      num_conversations: 34233,
      tags: ['entrepreneur', 'businessman'],
    }
  }
}

async function getCharacterPastChats() {
  return [
    {
      character: {
        id: '12345',
        created_at: new Date(),
        updated_at: new Date(),
        creator_id: '0987',
        name: 'Barack Obama',
        short_description:
          'I am Barack Obama, 44th President of the United States. ',
        avatar_uri: '/dummy-char.png',
        num_messages: 234234,
        num_conversations: 3423,
        tags: ['president', 'politician'],
      },
      lastMessage: "Why can't I just eat my waffle?",
      lastConversationId: '123',
    },
    {
      character: {
        id: '23456',
        created_at: new Date(),
        updated_at: new Date(),
        creator_id: '0987',
        name: 'Elon Musk',
        short_description:
          "You're wasting my time. I literally rule the world.",
        avatar_uri: '/dummy-char.png',
        num_messages: 2342343,
        num_conversations: 34233,
        tags: ['entrepreneur', 'businessman'],
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
      id: '12353223iy4',
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char-first',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'bot' as 'bot' | 'user',
    },
    {
      id: 'adsklfhjjkj23',
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'user' as 'bot' | 'user',
    },
    {
      id: 'asdfhih34',
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'bot' as 'bot' | 'user',
    },
    {
      id: '325tieqwjaf',
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'user' as 'bot' | 'user',
    },
    {
      id: 'asghghdfhi34',
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'bot' as 'bot' | 'user',
    },
    {
      id: '325teqwkjjaf',
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'user' as 'bot' | 'user',
    },
    {
      id: 'asdfuhhi34',
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char',
      content: 'Hey how are you?',
      timeStamp: new Date(),
      senderType: 'bot' as 'bot' | 'user',
    },
    {
      id: '325iy98teqwjaf',
      img: '/dummy-char.png',
      alt: 'dummy-char',
      name: 'dummy-char-last',
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
