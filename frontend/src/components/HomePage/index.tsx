'use client'

import { useEffect, useState } from 'react'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'

import Carousel from './Carousel'
import TopBar from '@/components/TopBar'
import AlertBar from '@/components/AlertBar'
import { Character } from '@/types'
import SearchGrid from './SearchGrid'

interface HomeScreenProps {
  topCharacters: Character[]
  continueChatting: Character[]
  trending: Character[]
  anime: Character[]
}

export default function HomeScreen({
  topCharacters,
  continueChatting,
  trending,
  anime,
}: HomeScreenProps) {
  const [searchInput, setSearchInput] = useState('')
  const [searchedCharacters, setSearchedCharacters] = useState<Character[]>([])
  const [typingTimeout, setTypingTimeout] = useState<NodeJS.Timeout | null>(
    null
  )

  useEffect(() => {
    return () => {
      if (typingTimeout) clearTimeout(typingTimeout)
    }
  }, [typingTimeout])

  function onSearchInput(input: string) {
    setSearchInput(input)

    if (typingTimeout) clearTimeout(typingTimeout)

    setTypingTimeout(
      setTimeout(() => {
        console.log('User stopped typing')
        // api request to update searchedCharacters
      }, 1000)
    )
  }

  function clearSearchInput() {
    setSearchInput('')
  }

  return (
    <div className='pb-[75px]'>
      <AlertBar />
      <TopBar
        searchInput={searchInput}
        onSearchInput={onSearchInput}
        clearSearchInput={clearSearchInput}
      />
      {searchInput !== '' && <SearchGrid characters={searchedCharacters} />}
      {searchInput === '' && (
        <>
          <div className='h-[100px] w-full px-[4%] flex flex-col items-center cursor-pointer justify-center'>
            <h1 className='text-5xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-purple-500'>
              Welcome Back{' '}
            </h1>
          </div>
          <Carousel
            characters={topCharacters}
            name='Top Characters'
            slidesPerView={6}
            zIndex={40}
          />
          <Carousel
            characters={continueChatting}
            name='Continue Chatting'
            slidesPerView={6}
            zIndex={30}
          />
          <Carousel
            characters={trending}
            name='Trending'
            slidesPerView={6}
            zIndex={20}
          />
          <Carousel
            characters={anime}
            name='Anime'
            slidesPerView={6}
            zIndex={10}
          />
        </>
      )}
    </div>
  )
}

{
  /* <div className='h-[300px] bg-red-400asdf w-[75%] px-[4%] flex flex-col items-center cursor-pointer justify-center w-1/2'>
        <h1 className='text-5xl text-white font-bold mb-2'>
          The most advanced AI available{' '}
          <div className={styles.cubespinner}>
            <div className={styles.face1}>
              <span className='bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-purple-500'>
                Unfiltered, NSFW content
              </span>
            </div>
            <div className={styles.face2}>
              <span className='bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-purple-500'>
                Dynamic, living, breathing clones with long-term memory
              </span>
            </div>
            <div className={styles.face3}>
              <span className='bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-purple-500'>
                Dynamic clones that live and react to current events
              </span>
            </div>
          </div>
        </h1>
        <div className='flex mt-24 ml-16'>
          <button className='bg-purple-600 text-white font-semibold px-4 py-2 rounded-[14px] m-2 border-white hover:bg-purple-500'>
            Learn more
          </button>
          <button className='bg-purple-600 text-white font-semibold px-4 py-2 rounded-[14px] m-2 border-white'>
            Join now
          </button>
        </div>
      </div> */
}
