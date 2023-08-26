import Link from "next/link"

import Image from 'next/image'
import InfiniteScroll from "react-infinite-scroll-component"
import { Character, CharacterChat } from "@/types"
import { useEffect, useRef, useState } from "react"
import SearchIcon from "./SearchIcon"
import CharacterComponent from './Character'
import { ColorRing } from "react-loader-spinner"
import { useQueryConversationMessages } from '@/hooks/useConversations'


interface SmallNavProps {
  characterId: string
  conversationId: string,
  character: Character
}

export default function SmallNav({
  characterId,
  conversationId,
  character
}: SmallNavProps) {
  const [characterChats, setCharacterChats] = useState<any>([]);
  const [isFetching, setIsFetching] = useState(true)

  const {data, error, isLoading} = useQueryConversationMessages({conversationId})

  useEffect(() => {
    if (conversationId != 'undecided') {
      const characterChat = {
          character: character,
          lastMessage: data ? data[data.length - 1].content : '',
          lastConversationId: conversationId,
      }
      setCharacterChats(characterChat)
    }
    
}, [conversationId, character])

  // search state
  const [isInputActive, setInputActive] = useState(false)
  const handleInputFocus = () => setInputActive(true)
  const handleInputBlur = () => setInputActive(false)

  const fetchMoreData = () => {
    // FETCH A LIST OF CHARACTER CHAT OBJECTS HERE

    // Add the new conversations to the end of the existing conversations
    // setCharacterChats((prevCharChats) => [
    //   ...prevCharChats,
    //   ...newCharChats,
    // ])
  }

  if (isLoading || !character || !conversationId || !characterChats) {
    return <div> Loading characterSidebar.. </div>
}

  return (
    <>
      <button type="button" className="lg:hidden mr-6 text-gray-500 hover:text-gray-600" data-hs-overlay="#docs-sidebar" aria-controls="docs-sidebar" aria-label="Toggle navigation">
        <span className="sr-only">Toggle Navigation</span>
        <svg className="w-5 h-5" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
          <path fill-rule="evenodd" d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z" />
        </svg>
      </button>

      <div id="docs-sidebar" className="bg-[#121212] text-white lg:hidden hs-overlay hs-overlay-open:translate-x-0 -translate-x-full transition-all duration-300 transform hidden fixed top-0 left-0 bottom-0 z-[60] w-full min-[400px]:w-[375px] pt-7 pb-10 overflow-y-auto scrollbar-y lg:block lg:translate-x-0 lg:right-auto lg:bottom-0">
        {/* Brand Logo */}
        <div className='flex items-center px-4 justify-between py-6'>
          <div className='flex items-center cursor-pointer '>
            <Link href='/' className='flex items-center cursor-pointer'>
              <div className='h-8 w-8 relative'>
                <Image
                  src='/clonr-logo.png'
                  alt='logo'
                  layout='fill'
                  objectFit='cover'
                  className=''
                />
              </div>
              <h3 className='ml-2 text-[30px] font-semibold leading-5 text-white font-fabada'>
                clonr
              </h3>
              <p className='text-white font-thin ml-2 align-middle'>users</p>
            </Link>
          </div>
          <svg
            width='20'
            height='20'
            viewBox='0 0 16 16'
            fill='none'
            xmlns='http://www.w3.org/2000/svg'
            className="cursor-pointer"

          >
            <path
              d='M12.8537 12.1463C12.9002 12.1927 12.937 12.2479 12.9622 12.3086C12.9873 12.3693 13.0003 12.4343 13.0003 12.5C13.0003 12.5657 12.9873 12.6308 12.9622 12.6915C12.937 12.7521 12.9002 12.8073 12.8537 12.8538C12.8073 12.9002 12.7521 12.9371 12.6914 12.9622C12.6307 12.9873 12.5657 13.0003 12.5 13.0003C12.4343 13.0003 12.3692 12.9873 12.3085 12.9622C12.2478 12.9371 12.1927 12.9002 12.1462 12.8538L7.99997 8.70688L3.85372 12.8538C3.7599 12.9476 3.63265 13.0003 3.49997 13.0003C3.36729 13.0003 3.24004 12.9476 3.14622 12.8538C3.0524 12.7599 2.99969 12.6327 2.99969 12.5C2.99969 12.3673 3.0524 12.2401 3.14622 12.1463L7.2931 8L3.14622 3.85375C3.0524 3.75993 2.99969 3.63269 2.99969 3.5C2.99969 3.36732 3.0524 3.24007 3.14622 3.14625C3.24004 3.05243 3.36729 2.99973 3.49997 2.99973C3.63265 2.99973 3.7599 3.05243 3.85372 3.14625L7.99997 7.29313L12.1462 3.14625C12.24 3.05243 12.3673 2.99973 12.5 2.99973C12.6327 2.99973 12.7599 3.05243 12.8537 3.14625C12.9475 3.24007 13.0003 3.36732 13.0003 3.5C13.0003 3.63269 12.9475 3.75993 12.8537 3.85375L8.70685 8L12.8537 12.1463Z'
              fill='#515151'
            />
          </svg>
        </div>
        {/* Search Bar */}
        <div className={` flex w-[375px] min-w-[375px] max-w-[375px] items-center gap-x-2 pb-4`}>
          <div className='relative w-full'>
            <div className='absolute left-4 top-3'>
              <SearchIcon
                strokeClasses={`${isInputActive ? 'stroke-[#5848BC]' : 'stroke-[#515151]'
                  } transition duration-100`}
              />
            </div>
            <input
              onFocus={handleInputFocus}
              onBlur={handleInputBlur}
              className='py-auto h-[48px] w-full border-none bg-[#1E1E1E] pl-[50px] text-[15px] font-light leading-6 text-[#979797] transition duration-100 focus:ring-1 focus:ring-transparent'
              type='text'
              placeholder='Search'
              style={{ outline: 'none', resize: 'none' }}
            />
          </div>
        </div>
        {/* Characters */}
        {
          isFetching && (
            <div className="grid place-items-center" >
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
          )
        }
        {!isFetching && (
          <div
            className='overflow-auto transition-all duration-100'
            id='scrollableDiv'
            style={{
              height: 'calc(100vh - 144px)',
              overflow: 'auto',
              scrollBehavior: 'smooth',
            }}
          >
            <InfiniteScroll
              dataLength={characterChats.length}
              next={fetchMoreData}
              hasMore={true}
              loader={<h4>Loading...</h4>}
              scrollableTarget='scrollableDiv'
              className='flex flex-col'
            >

              {characterChats.map((charChat, index) => (
                <CharacterComponent
                  key={charChat.character.id}
                  characterChat={charChat}
                  currentCharacterId={characterId}
                />
              ))}
            </InfiniteScroll>
          </div>
        )}
      </div>
    </>
  )
}

