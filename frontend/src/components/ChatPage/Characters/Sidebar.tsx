'use client'

import React, { useEffect, useRef, useState } from 'react'
import Image from 'next/image'
import SearchIcon from './SearchIcon'
import CharacterComponent from './Character'
import { CharacterChat } from '@/types'
import { formatDate } from '@/utils/formatDate'
import Link from 'next/link'
import InfiniteScroll from 'react-infinite-scroll-component'


interface CharactersProps {
    initialCharacterChats: CharacterChat[]
    currentCharacterId: string
}

export default function Characters({
    initialCharacterChats,
    currentCharacterId,
}: CharactersProps) {
    const [characterChats, setCharacterChats] = useState<CharacterChat[]>(
        initialCharacterChats
    )

    console.log("in Characters, initialCharacterChats -> ", initialCharacterChats)

    useEffect(() => {
        setCharacterChats(initialCharacterChats)
    }, [initialCharacterChats])


    // search state
    const [isInputActive, setInputActive] = useState(false)
    const handleInputFocus = () => setInputActive(true)
    const handleInputBlur = () => setInputActive(false)

    const sidebarRef = useRef<HTMLDivElement | null>(null)

    const fetchMoreData = () => {
        // FETCH A LIST OF CHARACTER CHAT OBJECTS HERE

        // Add the new conversations to the end of the existing conversations
        // setCharacterChats((prevCharChats) => [
        //   ...prevCharChats,
        //   ...newCharChats,
        // ])
    }

    if (!characterChats) return <div> Loading CharacterChats.. </div>

    return (
        <div
            ref={sidebarRef}
            className={`hidden lg:flex flex-col w-[375px] flex-grow border-r-[2px] border-[#252525] bg-[#121212] text-white`}
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
                            currentCharacterId={currentCharacterId}
                        />
                    ))}
                </InfiniteScroll>
            </div>
        </div>
    )
}
