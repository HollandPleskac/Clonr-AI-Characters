'use client'

import HomePage from '@/components/HomePage'
import Footer from '@/components/Footer'
import PreviousConversation from '@/components/ChatPage/Conversations/PreviousConversation'
import { Conversation } from '@/types';
import ConfirmDeleteModal from '@/components/Modal/ConfirmDeleteModal';
import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown'


export default function Home() {


const conversation1: Conversation = {
  name: "Chat with Alice",
  user_name: "Bob",
  memory_strategy: "short_term",
  information_strategy: "fact_based",
  adaptation_strategy: "user_focused",
  clone_id: "c12345",
  id: "a12345",
  created_at: "2023-09-15T10:00:00.000Z",
  updated_at: "2023-09-16T10:00:00.000Z",
  user_id: "u12345",
  is_active: true,
  num_messages_ever: 50,
  last_message: "See you tomorrow!",
  clone_name: "AliceClone"
};

const conversation2: Conversation = {
  name: "Chat with BobClone",
  user_name: "Alice",
  memory_strategy: "long_term",
  information_strategy: "opinion_based",
  adaptation_strategy: "context_aware",
  clone_id: "c54321",
  id: "a54321",
  created_at: "2023-09-10T10:00:00.000Z",
  updated_at: "2023-09-14T10:00:00.000Z",
  user_id: "u54321",
  is_active: false,
  num_messages_ever: 100,
  last_message: "Goodnight!",
  clone_name: "BobClone"
};


const convs = [conversation1, conversation2]

  const [selectedConvIdDelete, setSetectedConvIdDelete] = useState<string | null>(null)
  useEffect(() => {
    require('preline')
  }, [])


  return (
    <>
      <main className='w-full flex flex-col h-full'>
        <ConfirmDeleteModal conversationId={selectedConvIdDelete} />
        <div className='text-white bg-black w-full h-screen p-8' >
        <ReactMarkdown># Hello, *world*!</ReactMarkdown>
          <h1>test page</h1>
          <div className='flex flex-col gap-y-2' >
            {convs && convs.map((c, i) => {
              return <PreviousConversation conversation={c} handleSetSelectedConversationIdToDelete={(id: string) => {
                setSetectedConvIdDelete(id)
              }} key={i} />
            })}
          </div>
        </div>

      </main>
      <Footer />
    </>
  )
}
