'use client'

import React, { useEffect, useState } from 'react'
import Image from 'next/image'
import SearchIcon from './SearchIcon'
import CharacterComponent from './Character'
import { Character, CharacterChat } from '@/types'
import Link from 'next/link'
import InfiniteScroll from 'react-infinite-scroll-component'
import { ColorRing } from 'react-loader-spinner'
import { useSidebarClonesPagination } from '@/hooks/useSidebarClonesPagination'
import XIcon from '@/components/XIcon'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'

interface CharactersProps {
    currentCharacterId: string | null
    cloneChats: any
    isLoading: boolean
    isLastPage: boolean | undefined
    size: number
    setSize: (x:number) => void
    setSearchParam: (x: string) => void
    mutate: () => void
}

export default function Characters({
    currentCharacterId,
    cloneChats,
    isLoading,
    isLastPage,
    size,
    setSize,
    setSearchParam,
    mutate
}: CharactersProps) {
    const duration = 500
    const sideBarBgColor = '#2A2D31'
    const { push } = useRouter()

    // search state
    const [searchInput, setSearchInput] = useState('')
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


 
    // Component
    return (
        <div
            className={`hidden lg:flex flex-col w-[350px] flex-grow border-r-[2px] border-[#252525] bg-[#000000] text-white`}
            style={{ height: 'calc(100vh)' }}
        >
            {/* Brand Logo */}
           
            <div className='flex items-center px-4 justify-between py-6'>
                {/* Should we put an onClick back to clones? */}
                <div className='flex items-center cursor-default'>
                    <div className='h-8 w-8 relative'>
                        <Image
                            src='/clonr-logo.png'
                            alt='logo'
                            layout='fill'
                            objectFit='cover'
                            onClick={() => push("/")}
                            className='hover:cursor-pointer'
                        />
                    </div>
                    <h3 className='ml-2 text-[30px] font-semibold leading-5 text-white font-fabada'>
                        chat
                    </h3>
                    {/* <p className='text-white font-thin ml-2 align-middle'>users</p> */}
                </div>
                <div className="div flex">
                    <Link href="/" className="w-10 h-10 translate-y-[2px] hover:bg-white hover:bg-opacity-20 p-2 rounded-full hover:cursor-pointer transition-all duration-200">

                        <svg fill="#ffffff" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" height={20}>
                            <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
                            <g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g>
                            <g id="SVGRepo_iconCarrier">
                                <path d="M21.554,8.168l-9-6A1,1,0,0,0,12,2h0a1,1,0,0,0-.554.168h0l-9,6a1,1,0,0,0-.278,1.387l0,0A1.05,1.05,0,0,0,3,10H4V21a1,1,0,0,0,1,1H19a.99.99,0,0,0,.389-.079,60.628,60.628,0,0,0,.318-.214A1,1,0,0,0,20,21V10h1a1,1,0,0,0,.555-1.832ZM10,20V13h4v7Zm6,0V12a1,1,0,0,0-1-1H9a1,1,0,0,0-1,1v8H6V8.2l6-4,6,4V20Z">
                                </path>
                            </g>
                        </svg>
                    </Link>
                    <Link href="/browse" className="w-10 h-10 hover:bg-white hover:bg-opacity-20 p-2 rounded-full hover:cursor-pointer transition-all duration-200">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier">
                                <path d="M12 12H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12ZM16 8L9.5 9.5L8 16L14.5 14.5L16 8Z" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                </path>
                            </g>
                        </svg>
                    </Link>
                </div>
            </div>

            {/* Search Bar  */}
            <div className={`flex px-4 min-w-[350px] max-w-[350px] items-center gap-x-2 pb-4`}>
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
            {/* {isLoading && (
                <div className='h-full grid place-items-center' >
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
            )} */}
            {!isLoading && (
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
                        dataLength={cloneChats?.length ?? 0}
                        next={() => setSize(size + 1)}
                        hasMore={!isLastPage}
                        loader={<h4>Loading...</h4>}
                        scrollableTarget='scrollableDiv'
                        className='flex flex-col'
                    >

                        {cloneChats!.map((sidebarClone, index) => (
                            <CharacterComponent
                                key={sidebarClone.id}
                                sidebarClone={sidebarClone}
                                currentCharacterId={currentCharacterId}
                            />
                        ))}
                    </InfiniteScroll>
                </div>
            )}
        </div>
    )
}
