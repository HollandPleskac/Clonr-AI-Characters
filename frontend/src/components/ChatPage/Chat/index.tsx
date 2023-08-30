'use client'

import { useEffect, useRef, KeyboardEvent } from 'react'

import { useState } from 'react'
import MessageComponent from './ChatTypes/Message'

import SmileIcon from '@/svg/ChatPage/Chat/smile-icon.svg'
import SendIcon from '@/svg/ChatPage/Chat/SendIcon'
import { ColorRing, ThreeDots } from 'react-loader-spinner'

import { Character, Message } from '@/types'
import InfiniteScroll from 'react-infinite-scroll-component'
import ChooseChatExperience from './ChooseChatExperience'
import PreviousConversations from './PreviousConversations'
import ChatTopBar from './ChatTopBar'
import useConversations from '@/hooks/useConversations'
import { useMessagesPagination } from '@/hooks/useMessagesPagination'

interface ChatScreenProps {
  characterId: string
  conversationId: string
  character: Character
}


export default function ChatScreen({
  characterId,
  conversationId,
  character,
}: ChatScreenProps) {
  const { queryConversation, queryConversationMessages } = useConversations();

  const [message, setMessage] = useState('')

  const [isFetchingServerMessage, setIsFetchingServerMessage] = useState(false)

  const [showChat, setShowChat] = useState(true)
  const [scrollToNewMessage, setScrollToNewMessage] = useState<boolean>(false)

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

    // await new Promise((resolve) => setTimeout(resolve, 500))

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

    setIsFetchingServerMessage(false)
  }

  const handleConversationCreate = async () => {
    let conversationCreateData = {
      name: 'example',
      user_name: 'user',
      memory_strategy: 'short_term',
      information_strategy: 'internal',
      adaptation_strategy: 'static',
      clone_id: 'd433575f-d8ad-4f80-a90d-f21122b71bf0'
    }
    let convo_id = await createConversation(conversationCreateData);
    setConvoID(convo_id)

    let r_msg = await queryConversationMessages(convo_id);
    let msgs = r_msg.map((x: Message, index: number) => (
      x
    ))
    setMessages(msgs)
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
    if (e.key === 'Enter') {
      sendMessage()
    }
  }

  useEffect(() => {
    // @ts-ignore
    import('preline')
  }, [])

  return (
    <div className='w-[100%] border-r-[2px] border-[#252525] bg-[#121212] lg:inline'>
      {conversationId === 'convo' && (
        <ChooseChatExperience
          characterId={characterId}
          character={character}
          toggleChatState={() => setShowChat((prevState) => !prevState)}
          showChat={showChat}
        />
      )}

      {conversationId !== 'convo' && (
        <>
          <ChatTopBar
            isInputActive={isInputActive}
            searchInput={searchInput}
            onSearchInput={(x) => setSearchInput(x)}
            handleInputFocus={handleInputFocus}
            handleInputBlur={handleInputBlur}
            inputRef={inputRef}
            toggleChatState={() => setShowChat((prevState) => !prevState)}
            showChat={showChat}
            character={character}
            characterId={characterId}
            conversationId={conversationId}
          />
          {!showChat && <PreviousConversations characterId={characterId} />}
          {showChat && (
            <>
              {isLoadingMessages && (
                <div className='text-white grid place-items-center'
                  style={{
                    height: 'calc(100vh - 122px - 92px)',
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

              {!isLoadingMessages && (
                <div
                  id='scrollableMessagesDiv'
                  style={{
                    height: 'calc(100vh - 122px - 92px)',
                    overflow: 'auto',
                    display: 'flex',
                    flexDirection: 'column-reverse',
                    scrollBehavior: 'smooth',
                  }}
                  className='px-6'
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
                    <div
                      className={`${isFetchingServerMessage
                        ? 'text-white flex'
                        : 'text-transparent hidden'
                        } w-full py-4 h-[56px]`}
                    >
                      <ThreeDots
                        height='25'
                        width='25'
                        radius='4'
                        color='#979797'
                        ariaLabel='three-dots-loading'
                        wrapperStyle={{}}
                        visible={isFetchingServerMessage}
                      />
                    </div>
                    {messages?.map((message, index) => (
                      <MessageComponent
                        mutateMessages={mutateMessages}
                        conversationId={conversationId}
                        message={message}
                        character={character}
                        clone_avatar_uri={character.avatar_uri}
                        isLast={
                          message.is_clone && index === 0 ? true : false
                        }
                        key={message.id}
                      />

                    ))}
                  </InfiniteScroll>
                </div>
              )}

              <div className='flex h-[92px] items-center border-t  border-[#252525] px-6'>
                <div className='relative w-full'>
                  {/* <div className='absolute right-4 top-3'>
                    <SmileIcon />
                  </div> */}
                  <input
                    className='h-[48px] w-full rounded-[14px] border-none bg-[#1E1E1E] py-4 pl-4 pr-[50px] text-[15px] font-light leading-6 text-[#979797] transition-all duration-100 focus:ring-1 focus:ring-transparent'
                    type='text'
                    placeholder='Type a message'
                    value={message}
                    onChange={(event: any) => setMessage(event.target.value)}
                    style={{ outline: 'none', resize: 'none' }}
                    onKeyDown={handleOnKeyDown}
                  />
                </div>
                <div className='ml-[10px] transition-all duration-100 '>
                  <button
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
              </div>
            </>
          )}
        </>
      )}
    </div>
  )
}

{
  /* <div className='flex w-full gap-x-6 mb-8'>
            <div className='w-1/2 flex flex-col bg-white border shadow-sm rounded-xl p-4 md:p-5 dark:bg-gray-800 dark:border-gray-700 dark:shadow-slate-700/[.7]'>
              <h3 className='text-lg font-bold text-gray-800 dark:text-white'>
                Short Term Memory
              </h3>
              <p className='mt-1 text-xs font-medium uppercase text-gray-500 dark:text-gray-500'>
                Fun conversations
              </p>
              <p className='mt-2 text-gray-800 dark:text-gray-400'>
                The short term memory bot offers a delightful twist for casual
                users, creating quick, fun conversations that are ideal for
                light-hearted chats and momentary enjoyment.
              </p>
              <a
                className='mt-3 inline-flex items-center gap-2 mt-5 text-sm font-medium text-purple-500 hover:text-purple-700'
                href='#'
              >
                Start Chat
                <svg
                  className='w-2.5 h-auto'
                  width='16'
                  height='16'
                  viewBox='0 0 16 16'
                  fill='none'
                  xmlns='http://www.w3.org/2000/svg'
                >
                  <path
                    d='M5 1L10.6869 7.16086C10.8637 7.35239 10.8637 7.64761 10.6869 7.83914L5 14'
                    stroke='currentColor'
                    stroke-width='2'
                    stroke-linecap='round'
                  />
                </svg>
              </a>
            </div>
            <div className='w-1/2 flex flex-col bg-white border shadow-sm rounded-xl p-4 md:p-5 dark:bg-gray-800 dark:border-gray-700 dark:shadow-slate-700/[.7]'>
              <h3 className='text-lg font-bold text-gray-800 dark:text-white'>
                Long Term Memory
              </h3>
              <p className='mt-1 text-xs font-medium uppercase text-gray-500 dark:text-gray-500'>
                Deep Relationship
              </p>
              <p className='mt-2 text-gray-800 dark:text-gray-400'>
                The long-term memory bot is designed for fostering deep
                relationships, remembering past interactions to create a more
                meaningful connection.
              </p>
              <a
                className='mt-3 inline-flex items-center gap-2 mt-5 text-sm font-medium text-purple-500 hover:text-purple-700'
                href='#'
              >
                Start Chat
                <svg
                  className='w-2.5 h-auto'
                  width='16'
                  height='16'
                  viewBox='0 0 16 16'
                  fill='none'
                  xmlns='http://www.w3.org/2000/svg'
                >
                  <path
                    d='M5 1L10.6869 7.16086C10.8637 7.35239 10.8637 7.64761 10.6869 7.83914L5 14'
                    stroke='currentColor'
                    stroke-width='2'
                    stroke-linecap='round'
                  />
                </svg>
              </a>
            </div>
          </div> */
}
