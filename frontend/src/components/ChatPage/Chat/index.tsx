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

interface ChatScreenProps {
  characterId: string
  conversationId: string
}


export default function ChatScreen({
  characterId,
  conversationId,
}: ChatScreenProps) {
  const [message, setMessage] = useState('')
  const [isFetchingServerMessage, setIsFetchingServerMessage] = useState(false)

  const [scrollToNewMessage, setScrollToNewMessage] = useState<boolean>(false)

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

  // import preline and collapse sidebar if needed
  useEffect(() => {
    // @ts-ignore
    import('preline')
  }, [])

  return (
    <div className='w-[100%] border-r-[2px] border-[#252525] bg-[#121212] lg:inline'>
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
          />
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

    </div>
  )
}