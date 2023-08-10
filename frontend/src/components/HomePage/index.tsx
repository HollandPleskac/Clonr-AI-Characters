'use client'

import { useEffect, useState } from 'react'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'

const axios = require('axios').default

import Carousel from './Carousel'
import TopBar from '@/components/TopBar'
import AlertBar from '@/components/AlertBar'
import { Character } from '@/types'
import SearchGrid from './SearchGrid'
import StatBar from '../Statistics/StatBar'
import ScaleFadeIn from '../Transitions/ScaleFadeIn'
import useClones from '@/hooks/useClones'
import AuthModal from '../AuthModal'
import StripeCheckoutButton from '@/components/Stripe/StripeCheckoutButton';

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
  const [doneSearching, setDoneSearching] = useState(false)
  const [showSearchGrid, setShowSearchGrid] = useState(false)
  const [trill, setTrill] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const duration = 500
  const { queryClones, fetchCloneById } = useClones();

  useEffect(() => {
    require('preline')
  }, [])

  const handleCloneSearch = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await queryClones(searchInput);
      setSearchedCharacters(data);
      setDoneSearching(searchInput !== '');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const debounceTimeout = setTimeout(handleCloneSearch, 500);
    return () => {
      clearTimeout(debounceTimeout)
    }
  }, [searchInput])

  useEffect(() => {
    if (searchInput === '') {
      setShowSearchGrid(false)
      console.log(searchInput)
    } else {
      if (!showSearchGrid) {
        const timer = setTimeout(() => {
          setShowSearchGrid(true)
        }, duration)
        return () => clearTimeout(timer)
      }
    }
  }, [searchInput])

  return (
    <div className='pb-[75px]'>
      <AlertBar />

      <TopBar
        searchInput={searchInput}
        onSearchInput={(x) => setSearchInput(x)}
        clearSearchInput={() => setSearchInput('')}
      />
      {showSearchGrid ? (
        <ScaleFadeIn loaded={showSearchGrid} duration={duration}>
          <SearchGrid characters={searchedCharacters} doneSearching={true} />
        </ScaleFadeIn>
      ) : (
        <ScaleFadeIn loaded={!searchInput} duration={duration}>
          <StripeCheckoutButton />
          <Carousel
            characters={topCharacters}
            name='Top Characters'
            isBigCarousel={true}
            zIndex={40}
          />
          {/* <StatBar /> */}
          <Carousel
            characters={continueChatting}
            name='Continue Chatting'
            isBigCarousel={false}
            zIndex={30}
          />
          <Carousel
            characters={trending}
            name='Trending'
            isBigCarousel={false}
            zIndex={20}
          />
          <Carousel
            characters={anime}
            name='Anime'
            isBigCarousel={false}
            zIndex={10}
          />
        </ScaleFadeIn>
      )}
      <AuthModal />
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
