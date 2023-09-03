'use client'

import { useEffect, useState } from 'react'
import CharactersSidebar from '@/components/ChatPage/Characters/Sidebar'
import Chat from '@/components/ChatPage/Chat';
import { useSidebarClonesPagination } from '@/hooks/useSidebarClonesPagination';
import Form from './Form';
import { useSession } from 'next-auth/react';
import { redirect } from 'react-router-dom';

export default function TestPage() {
  const { data: session, status } = useSession({ required: true })
  const loading = status === "loading"

  const [showChat, setShowChat] = useState(false)
  const [cloneId, setCloneId] = useState<string | null>(null)
  const [conversationId, setConversationId] = useState<string | null>(null)

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

  function handleShowChat(cloneId: string, convId: string) {
    setShowChat(true)
    setCloneId(cloneId)
    setConversationId(convId)
  }

  // manage form state here
  const [llmStart, setLlmStart] = useState("")
  const [characterName, setCharacterName] = useState("")
  const [username, setUsername] = useState("")
  const [shortDescription, setShortDescription] = useState("")
  const [longDescription, setLongDescription] = useState("")

  const [selectedFile, setSelectedFile] = useState(null);
  const [imageSrc, setImageSrc] = useState('');

  if (loading) {
    return (
      <div > </div>
    )
  }

  if (!loading && !session) {
    return redirect("/login")
  }

  return (
    <>
      {!showChat && (
        <div className='text-white' >
          <Form handleShowChat={handleShowChat}
            llmStart={llmStart}
            setLlmStart={setLlmStart}
            characterName={characterName}
            setCharacterName={setCharacterName}
            username={username}
            setUsername={setUsername}
            shortDescription={shortDescription}
            setShortDescription={setShortDescription}
            longDescription={longDescription}
            setLongDescription={setLongDescription}
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            imageSrc={imageSrc}
            setImageSrc={setImageSrc}
            session={session}
          />
        </div>
      )}
      {(showChat && conversationId && cloneId) && (
        <div
          className='bg-gray-900 w-full flex justify-center items-center overflow-hidden'
          style={{ height: 'calc(100vh)' }}
        >

          <div className='relative' >
            <button onClick={() => { setShowChat(false) }} className='absolute z-50 bg-blue-800 h-[80px] w-[300px] text-white grid place-items-center' >Go back to form</button>
            <CharactersSidebar
              currentCharacterId={cloneId}
              cloneChats={cloneChats}
              isLoading={isLoading}
              isLastPage={isLastPage}
              size={size}
              setSize={setSize}
              setSearchParam={setSearchParam}
              mutate={mutate}
            />
          </div>
          <Chat
            characterId={cloneId}
            conversationId={conversationId}
            mutateSidebar={mutate}
          />
        </div>
      )}
    </>
  )
}