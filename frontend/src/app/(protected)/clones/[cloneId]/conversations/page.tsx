'use client'

import { useEffect, useState } from 'react'
import CharactersSidebar from '@/components/ChatPage/Characters/Sidebar'
import Conversations from '@/components/ChatPage/Conversations';
import { useSidebarClonesPagination } from '@/hooks/useSidebarClonesPagination';

export default function ConversationsPage({
  params,
}: {
  params: { cloneId: string }
}) {
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
      <Conversations
        characterId={params.cloneId}
      />
    </>
  )
}