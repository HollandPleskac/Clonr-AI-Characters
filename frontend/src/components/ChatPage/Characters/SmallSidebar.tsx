import Link from "next/link"

import Image from 'next/image'
import InfiniteScroll from "react-infinite-scroll-component"
import { useEffect, useState } from "react"
import SearchIcon from "./SearchIcon"
import CharacterComponent from './Character'
import { ColorRing } from "react-loader-spinner"
import { useSidebarClonesPagination } from "@/hooks/useSidebarClonesPagination"
import XIcon from "@/components/XIcon"
import { useRouter } from "next/navigation"

interface SmallNavProps {
  characterId: string
}

export default function SmallNav({
  characterId,
}: SmallNavProps) {
  const router = useRouter()
  const duration = 500

  // search state
  const [searchInput, setSearchInput] = useState('')
  const [searchParam, setSearchParam] = useState('')
  const [isInputActive, setInputActive] = useState(false)
  const handleInputFocus = () => setInputActive(true)
  const handleInputBlur = () => setInputActive(false)

  // search delay
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchParam(searchInput)
    }, duration)
    return () => clearTimeout(timer)
  }, [searchInput])

  const sidebarClonesQueryParams = {
    limit: 10,
    name: searchParam,
  }

  const {
    paginatedData: cloneChats,
    isLoading,
    isLastPage,
    size,
    setSize
  } = useSidebarClonesPagination(sidebarClonesQueryParams)

  async function pushToUrl(url:string) {
    if (window.innerWidth < 1024) {
      const sidebarElement = document.querySelector('#docs-sidebar');
      await (window as any).HSOverlay.close(sidebarElement)
    }
    router.push(url)
  }

  return (
    <>
      <button type="button" className="lg:hidden mr-6 text-gray-500 hover:text-gray-600" data-hs-overlay="#docs-sidebar" aria-controls="docs-sidebar" aria-label="Toggle navigation">
        <span className="sr-only">Toggle Navigation</span>
        <svg className="w-5 h-5" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
          <path fillRule="evenodd" d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z" />
        </svg>
      </button>

      <div id="docs-sidebar" className="bg-[#121212] text-white lg:hidden hs-overlay hs-overlay-open:translate-x-0 -translate-x-full transition-all duration-300 transform hidden fixed top-0 left-0 bottom-0 z-[60] w-full min-[400px]:w-[350px] pt-7 pb-10 overflow-y-autoasdf scrollbar-yadsf lg:block lg:translate-x-0 lg:right-auto lg:bottom-0">
        {/* Brand Logo */}
        <div className='flex items-center px-4 justify-between py-6'>
          {/* Should we put an onClick back to clones? */}
          <button className='flex items-center' onClick={() => pushToUrl("/")}>
            <div className='h-8 w-8 relative'>
              <Image
                src='/clonr-logo.png'
                alt='logo'
                layout='fill'
                objectFit='cover'
                
                className='hover:cursor-pointer'
              />
            </div>
            <h3 className='ml-2 text-[30px] font-semibold leading-5 text-white font-fabada'>
              chat
            </h3>
            {/* <p className='text-white font-thin ml-2 align-middle'>users</p> */}
          </button>
          <div className="div flex">
            <button onClick={() => pushToUrl("/")}
              className="w-10 h-10 hover:bg-white hover:bg-opacity-20 p-2 rounded-full hover:cursor-pointer transition-all duration-200"
            >

              <svg fill="#ffffff" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
                <g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g>
                <g id="SVGRepo_iconCarrier">
                  <path d="M21.554,8.168l-9-6A1,1,0,0,0,12,2h0a1,1,0,0,0-.554.168h0l-9,6a1,1,0,0,0-.278,1.387l0,0A1.05,1.05,0,0,0,3,10H4V21a1,1,0,0,0,1,1H19a.99.99,0,0,0,.389-.079,60.628,60.628,0,0,0,.318-.214A1,1,0,0,0,20,21V10h1a1,1,0,0,0,.555-1.832ZM10,20V13h4v7Zm6,0V12a1,1,0,0,0-1-1H9a1,1,0,0,0-1,1v8H6V8.2l6-4,6,4V20Z">
                  </path>
                </g>
              </svg>
            </button>
            <button onClick={() => pushToUrl("/browse")} className="w-10 h-10 hover:bg-white hover:bg-opacity-20 p-2 rounded-full hover:cursor-pointer transition-all duration-200">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier">
                  <path d="M12 12H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12ZM16 8L9.5 9.5L8 16L14.5 14.5L16 8Z" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  </path>
                </g>
              </svg>
            </button>
            <button
              type='button'
              data-hs-overlay="#docs-sidebar"
              aria-controls="docs-sidebar"
              aria-label="Toggle navigation"
              className="pl-2"
            >

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
            </button>
          </div>
        </div>
        {/* Search Bar */}
        <div className={` flex px-4 w-[350px] min-w-[350px] max-w-[350px] items-center gap-x-2 pb-4`}>
          <div className='relative w-full'>
            <div className='absolute left-4 top-3'>
              <SearchIcon
                strokeClasses={`${isInputActive ? 'stroke-[#5848BC]' : 'stroke-[#515151]'
                  } transition duration-100`}
              />
            </div>
            <input
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onFocus={handleInputFocus}
              onBlur={handleInputBlur}
              className='py-auto h-[48px] pr-[42px] w-full border-none bg-[#ffffff] bg-opacity-10 rounded-xl pl-[50px] text-[15px] font-light leading-6 text-[#979797] transition duration-100 focus:ring-1 focus:ring-transparent'
              type='text'
              placeholder='Search'
              style={{ outline: 'none', resize: 'none' }}
            />
            <button
              className={`absolute right-4 top-[16px] ${searchInput === '' ? 'hidden' : 'flex'
                }`}
              onMouseDown={(e) => e.preventDefault()} // prevent blur on input
              onClick={() => { setSearchInput('') }}
            >
              <XIcon />
            </button>
          </div>
        </div>
        {/* Characters */}
        {
          isLoading && (
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
        {!isLoading && (
          <div
            className='overflow-auto transition-all duration-100'
            id='scrollableDivSidebar'
            style={{
              height: 'calc(100vh - 172px - 40px)',
              overflow: 'auto',
              scrollBehavior: 'smooth',
            }}
          >
            <InfiniteScroll
              dataLength={cloneChats?.length ?? 0}
              next={() => setSize(size + 1)}
              hasMore={!isLastPage}
              loader={<h4>Loading...</h4>}
              scrollableTarget='scrollableDivSidebar'
              className='flex flex-col'
            >

              {cloneChats!.map((sidebarClone, index) => (
                <CharacterComponent
                  key={sidebarClone.id}
                  sidebarClone={sidebarClone}
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

