import Characters from '@/components/ChatPage/Characters'
import ChatScreen from '@/components/ChatPage/Chat'

export default async function ChatPage({
  params,
}: {
  params: { characterId: string; conversationId: string }
}) {
  return (
    <div>
      {/* <TopBar /> */}
      <div
        className='bg-gray-900 w-full flex justify-center items-center overflow-hidden'
        style={{ height: 'calc(100vh)' }}
      >
        <Characters />
        <ChatScreen
          characterId={params.characterId}
          characterName={'characterName'}
          chatId={params.conversationId}
        />
      </div>
    </div>
  )
}
