'use client'

import { cloneElement, useEffect, useState } from 'react'
//import { cookies } from 'next/headers'
// import Cookies from 'js-cookie';
import { redirect } from 'next/navigation'
import { Character, SidebarClone } from '@/types';
import cookiesToString from '@/utils/cookiesToString';
import CharactersSidebar from '@/components/ChatPage/Characters/Sidebar'
import ChatScreen from '@/components/ChatPage/Chat'
import { useQueryClonesById } from '@/hooks/useClones'
import Chat from '@/components/ChatPage/Chat';
import { useSession } from 'next-auth/react';
import { useSidebarClonesPagination } from '@/hooks/useSidebarClonesPagination';

export default function ConversationsPage({
  params,
}: {
  params: { cloneId: string, conversationId: string }
}) {

  //const { queryCloneById } = useClones()

  // Route Protection
  //const cookieStore = cookies()
  //const userCookie = cookieStore.get('clonrauth')
  //const userCookie = Cookies.get('clonrauth');

  // if (!userCookie) {
  //   redirect("/login")
  // }

  useEffect(() => {
    require('preline')
  }, [])

  const [searchParam, setSearchParam] = useState('')

  const sidebarClonesQueryParams = {
    limit: 10,
    name: searchParam,
  }

  const {
    paginatedData: cloneChats,
    isLoading,
    isLastPage,
    size,
    setSize,
    mutate
  } = useSidebarClonesPagination(sidebarClonesQueryParams)

  console.log("clone chats", cloneChats)


  // Render Page
  return (
    <>
      <CharactersSidebar
        currentCharacterId={params.cloneId}
        cloneChats={cloneChats}
        isLoading={isLoading}
        isLastPage={isLastPage}
        size={size}
        setSize={setSize}
        setSearchParam={setSearchParam}
        mutate={mutate}
      />
      <Chat
        characterId={params.cloneId}
        conversationId={params.conversationId}
        mutateSidebar={mutate}
      />
    </>
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