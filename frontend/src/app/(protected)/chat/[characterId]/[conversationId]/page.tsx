'use client'

import { useEffect, useState } from 'react'
//import { cookies } from 'next/headers'
import Cookies from 'js-cookie';
import { redirect } from 'next/navigation'
import { Character } from '@/types';
import cookiesToString from '@/utils/cookiesToString';
import CharactersSidebar from '@/components/ChatPage/Characters/Sidebar'
import ChatScreen from '@/components/ChatPage/Chat'
import { useQueryClonesById } from '@/hooks/useClones'
import router from 'next/router';
import { useSession } from 'next-auth/react';

export default function ChatPage({
  params,
}: {
  params: { characterId: string; conversationId: string }
}) {

  useEffect(() => {
    require('preline')
  }, [])

  

  return (
    <div
      className='bg-gray-900 w-full flex justify-center items-center overflow-hidden'
      style={{ height: 'calc(100vh)' }}
    >
      <CharactersSidebar
        currentCharacterId={params.characterId}
      />
      <ChatScreen
        characterId={params.characterId}
        conversationId={params.conversationId}
      />
    </div>
  )
}

// // // Return Character based on characterId
// async function getCharacterDetails(
//   characterId: string,
// ): Promise<Character> {
//   const res = await fetch(`http://localhost:8000/clones/${characterId}`, {
//     cache: 'no-store', // force-cache
//     method: 'GET',
//     headers: {
//       'Cookie': cookiesToString(Cookies.getAll())
//     },
//     credentials: 'include'
//   });

//   if (!res.ok) {
//     throw new Error(`Something went wrong! Status: ${res.status}`);
//   }

//   return await res.json()
// }