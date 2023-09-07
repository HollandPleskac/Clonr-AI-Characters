'use client'

import { useEffect, useRef, KeyboardEvent } from 'react'

import { useState } from 'react'
import MessageComponent from './ChatTypes/Message'

import SmileIcon from '@/svg/ChatPage/Chat/smile-icon.svg'
import SendIcon from '@/svg/ChatPage/Chat/SendIcon'
import { ColorRing, ThreeDots } from 'react-loader-spinner'

import InfiniteScroll from 'react-infinite-scroll-component'
import ChatTopBar from './ChatTopBar'
import useConversations from '@/hooks/useConversations'
import { useMessagesPagination } from '@/hooks/useMessagesPagination'
import { useQueryClonesById } from '@/hooks/useClones'
import { useRouter } from 'next/navigation'
import { useSession } from "next-auth/react"
import { Message } from '@/types'
import axios from 'axios'
import { useSidebarClonesPagination } from '@/hooks/useSidebarClonesPagination'
import { ConversationsService } from '@/client'
import { useRevisions } from '@/hooks/useRevisions'

interface ChatScreenProps {
  characterId: string
  conversationId: string
  mutateSidebar: () => void

}


export default function ChatScreen({
  characterId,
  conversationId,
  mutateSidebar
}: ChatScreenProps) {
  const [message, setMessage] = useState('')
  const [isFetchingServerMessage, setIsFetchingServerMessage] = useState(false)
  const [scrollToNewMessage, setScrollToNewMessage] = useState<boolean>(false)

  const router = useRouter();

  const [removeMode, setRemoveMode] = useState(false)

  const { data: character, error, isLoading: isLoadingCharacter } = useQueryClonesById({
    cloneId: characterId
  });

  // search state
  const [searchInput, setSearchInput] = useState('')
  const [isInputActive, setInputActive] = useState(false)
  const handleInputFocus = () => setInputActive(true)
  const handleInputBlur = () => setInputActive(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const divRef = useRef<HTMLDivElement | null>(null)

  // handle messages state
  const { createMessage, generateCloneMessage } = useConversations();

  const queryParamsMessages = {
    conversationId: conversationId,
    limit: 10
    // todo: include search query params
  }

  const {
    paginatedData: messages,
    isLastPage: isLastMessagesPage,
    isLoading: isLoadingMessages,
    size: messagesSize,
    setSize: setMessagesSize,
    mutate: mutateMessages
  } = useMessagesPagination(queryParamsMessages)

  useEffect(() => {
    if (scrollToNewMessage && divRef.current) {
      divRef.current.scrollTop = divRef.current.scrollHeight
      setScrollToNewMessage(false)
    }
  }, [messages, scrollToNewMessage])

  const sendMessage = async () => {
    setScrollToNewMessage(true)

    let sentMsg = await createMessage(conversationId, message);

    const newMessage = {
      id: window.Date.now().toString(),
      content: message,
      created_at: new window.Date().toString(),
      updated_at: new window.Date().toString(),
      sender_name: 'Test User',
      timestamp: new window.Date().toString(),
      is_clone: false,
      is_main: true,
      is_active: true,
      parent_id: '',
      clone_id: '',
      user_id: '',
      conversation_id: conversationId
    }

    let updatedMessages = [newMessage, ...messages]
    mutateMessages(updatedMessages);

    const message_copy = message
    setMessage('')
    await fetchMessageFromServer(message_copy)
  }

  const fetchMessageFromServer = async (in_msg: String) => {
    setIsFetchingServerMessage(true)

    await new Promise((resolve) => setTimeout(resolve, 1000))

    try {
      let serverMessage = await generateCloneMessage(conversationId);

      // update frontend
      if (serverMessage) {
        console.log('Server Message:', serverMessage.content)
      }

      const updatedMessagess = [serverMessage, ...messages]
      mutateMessages(updatedMessagess);

    } catch (error) {
      console.error(error)
    }

    mutateSidebar()
    mutateRevisions()
    setIsFetchingServerMessage(false)
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60

    const paddedMinutes = String(minutes).padStart(2, '0')
    const paddedSeconds = String(remainingSeconds).padStart(2, '0')

    return `${paddedMinutes}:${paddedSeconds}`
  }

  const handleOnKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    //it triggers by pressing the enter key
    if (e.key === 'Enter' && !isFetchingServerMessage) {
      sendMessage()
    }
  }

  // import preline and mutate sidebar if needed
  useEffect(() => {
    // @ts-ignore
    import('preline')
    mutateSidebar()
  }, [])

  const [removableMessages, setRemovableMessages] = useState<Message[]>([])

  function findAllDescendantMessages(messages: Message[], parentId, descendants: Message[] = []) {
    const child = messages.find(message => message.parent_id === parentId);

    // push Message of checkbox clicked
    const parent = messages.find(message => message.id === parentId);
    if (descendants.length === 0 && parent) {
      descendants.push(parent)
    }

    if (child) {
      descendants.push(child);
      findAllDescendantMessages(messages, child.id, descendants);
    }

    return descendants;
  }

  // if already checked instead, need to remove all checks of messages below
  // write function to remove descendents of list above the id clicked and stuff
  function handleRemoveMessage(id: string) {
    const descendants = findAllDescendantMessages(messages, id)
    if (id === removableMessages[0]?.id) {
      setRemovableMessages([])
    } else {
      setRemovableMessages(descendants)
    }
  }

  async function confirmRemoveMessages() {
    const response = await axios.delete(
      `http://localhost:8000/conversations/${conversationId}/messages/${removableMessages[0].id}`,
      {
        withCredentials: true
      }
    );
    setRemovableMessages([])
    mutateMessages()
    mutateSidebar()
    mutateRevisions()
    setRemoveMode(false)
    return response.data;
  }

  async function cancelRemoveMessages() {
    setRemovableMessages([])
    setRemoveMode(false)
  }

  // get revisions
  const { data:revisions, isLoading: isLoadingRevisions, mutate: mutateRevisions } = useRevisions({
    conversationId: conversationId
  });

  return (
    <div className='w-[100%] border-r-[2px] border-[#252525] bg-[#000000] lg:inline'>
      {isLoadingCharacter && (<div className='h-screen w-full grid place-items-center' >
        <ColorRing
          visible={true}
          height="80"
          width="80"
          ariaLabel="blocks-loading"
          wrapperStyle={{}}
          wrapperClass="blocks-wrapper"
          colors={['#9333ea', '#9333ea', '#9333ea', '#9333ea', '#9333ea']}
        />
      </div>)}
      {!isLoadingCharacter && (
        <>
          <ChatTopBar
            isInputActive={isInputActive}
            searchInput={searchInput}
            onSearchInput={(x) => setSearchInput(x)}
            handleInputFocus={handleInputFocus}
            handleInputBlur={handleInputBlur}
            inputRef={inputRef}
            character={character}
            characterId={characterId}
            conversationId={conversationId}
            toggleRemoveMode={() => {
              setRemoveMode(prevState => !prevState)
              console.log('changing remove')
            }}
          />
          {(isLoadingMessages || isLoadingRevisions) && (
            <div className='text-white grid place-items-center'
              style={{
                height: 'calc(100vh - 122px - 112px)',
              }}
            >
              <ColorRing
                visible={true}
                height="80"
                width="80"
                ariaLabel="blocks-loading"
                wrapperStyle={{}}
                wrapperClass="blocks-wrapper"
                colors={['#9333ea', '#9333ea', '#9333ea', '#9333ea', '#9333ea']}
              />
            </div>
          )}

          {!(isLoadingMessages || isLoadingRevisions) && (
            <div
              id='scrollableMessagesDiv'
              style={{
                height: 'calc(100vh - 122px - 112px)',
                overflow: 'auto',
                display: 'flex',
                flexDirection: 'column-reverse',
                scrollBehavior: 'smooth',
              }}
              className='px-[18px]'
              ref={divRef}
            >
              <InfiniteScroll
                dataLength={messages?.length ?? 0}
                next={() => setMessagesSize(messagesSize + 1)}
                hasMore={!isLastMessagesPage}
                style={{ display: 'flex', flexDirection: 'column-reverse' }} //To put endMessage and loader to the top.
                inverse={true}
                loader={<h4>Loading...</h4>}
                scrollableTarget='scrollableMessagesDiv'
                className='pt-4'
              >
                {messages?.map((message, index) => {
                  const isLast = message.is_clone && index === 0 ? true : false
                  return (
                    <MessageComponent
                      conversationId={conversationId}
                      message={message}
                      revisions={revisions}
                      mutateRevisions={mutateRevisions}
                      character={character}
                      clone_avatar_uri={character.avatar_uri}
                      isLast={isLast}
                      isRemoveMode={removeMode}
                      isRemoveMessage={removableMessages.some(removableMessage => removableMessage.id === message.id)}
                      handleRemoveMessage={handleRemoveMessage}
                      key={message.id}
                    />

                  )
                })}
              </InfiniteScroll>
            </div>
          )}

          <div className='relative flex flex-col'>
            <div className='flex flex-col h-[112px] justify-end border-t border-[#252525] px-6 mt-1'>
              {removeMode && (
                <div className='flex justify-between items-center w-full px-3' >
                  <p className='text-[#979797]' >Select the message to remove. All following messages will be removed.</p>
                  <div className='flex gap-x-2' >
                    <button
                      onClick={cancelRemoveMessages}
                      className='px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition duration-200' >Cancel</button>
                    <button
                      onClick={confirmRemoveMessages}
                      disabled={removableMessages.length === 0}
                      className={`px-4 py-2 ${removableMessages.length === 0 ? "bg-gray-400 text-white" : "bg-red-500 hover:bg-red-600 text-white"}  rounded-lg transition duration-200`} >Remove</button>
                  </div>
                </div>
              )}
              {
                !removeMode && (
                  <div className='flex w-full items-center' >
                    <div className='relative w-full'>
                      {/* <div className='absolute right-4 top-3'>
                            <SmileIcon />
                          </div> */}
                      <input
                        className='h-[48px] w-full rounded-[14px] border-none bg-[#1E1E1E] p-4 pl-4 pr-[50px] text-[15px] font-light leading-6 text-[#979797] transition-all duration-100 focus:ring-1 focus:ring-transparent'
                        type='text'
                        placeholder='Type a message'
                        value={message}
                        onChange={(event: any) => setMessage(event.target.value)}
                        style={{ outline: 'none', resize: 'none' }}
                        onKeyDown={handleOnKeyDown}
                      />
                    </div>

                    <button
                      className='ml-[10px] transition-all duration-100'
                      onClick={async () => {
                        !isFetchingServerMessage && sendMessage()
                      }}
                      disabled={isFetchingServerMessage}
                    >
                      <SendIcon
                        strokeClasses={
                          isFetchingServerMessage ? 'stroke-[#515151] fill-[#515151]' : ''
                        }
                      />
                    </button>
                  </div>
                )
              }
              <div className={` ${!isFetchingServerMessage && 'invisible'} mb-[10px] mt-[6px] flex items-center h-[22px] text-[#979797] gap-x-2 text-xs`} >
                <ThreeDots
                  height='22'
                  width='22'
                  radius='4'
                  color='#979797'
                  ariaLabel='three-dots-loading'
                  wrapperStyle={{}}
                  visible={isFetchingServerMessage}
                />
                {character.name} is typing...
              </div>
            </div>

          </div>
        </>
      )}

    </div>
  )
}