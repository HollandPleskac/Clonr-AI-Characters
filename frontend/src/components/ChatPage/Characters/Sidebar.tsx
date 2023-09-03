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
    currentCharacterId: string
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
            className={`hidden md:flex flex-col w-[300px] flex-grow border-r-[2px] border-[#252525] bg-[#000000] text-white`}
            style={{ height: 'calc(100vh)' }}
        >
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
            </div>

            {/* Search Bar  */}
            <div className={` flex w-[375px] min-w-[300px] max-w-[300px] items-center gap-x-2 pb-4`}>
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
                        className='py-auto h-[48px] pr-[42px] w-full border-none bg-[#16181A] pl-[50px] text-[15px] font-light leading-6 text-[#979797] transition duration-100 focus:ring-1 focus:ring-transparent'
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
            {isLoading && (
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
            )}
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
