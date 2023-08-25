
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { Character } from '@/types';
import cookiesToString from '@/utils/cookiesToString';
import CharactersSidebar from '@/components/ChatPage/Characters/Sidebar'
import ChatScreen from '@/components/ChatPage/Chat'

export default async function ChatPage({
  params,
}: {
  params: { characterId: string; conversationId: string }
}) {

  // Route Protection
  const cookieStore = cookies()
  const userCookie = cookieStore.get('fastapiusersauth')

  if (!userCookie) {
    redirect("/login")
  }

  // Get Character
  const character: Character = await getCharacterDetails(params.characterId)

  // Render Page
  return (
    <div
        className='bg-gray-900 w-full flex justify-center items-center overflow-hidden'
        style={{ height: 'calc(100vh)' }}
      >
        <CharactersSidebar
          currentCharacterId={params.characterId}
          conversationId={params.conversationId}
          character={character}
        />
        <ChatScreen
          characterId={params.characterId}
          conversationId={params.conversationId}
          character={character}
        />
      </div>
  )
}

// Return Character based on characterId
async function getCharacterDetails(
  characterId: string,
): Promise<Character> {
  const res = await fetch(`http://localhost:8000/clones/${characterId}`, {
    cache: 'force-cache',
    method: 'GET',
    headers: {
      'Cookie': cookiesToString(cookies().getAll())
    },
    credentials: 'include'
  });

  if (!res.ok) {
    throw new Error(`Something went wrong! Status: ${res.status}`);
  }

  return await res.json()
}
