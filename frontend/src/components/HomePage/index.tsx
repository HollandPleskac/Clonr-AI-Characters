'use client'

import { useEffect, useState } from 'react'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'
import Carousel from './Carousel'
import TopBar from '@/components/TopBar'
import AlertBar from '@/components/AlertBar'
import CharacterGrid from './CharacterGrid'
import StatBar from '../Statistics/StatBar'
import ScaleFadeIn from '../Transitions/ScaleFadeIn'
import { useQueryClones } from '@/hooks/useClones'
import { ColorRing } from "react-loader-spinner"
import { CloneSortType } from '@/client/models/CloneSortType'
import { useQueryConversationsContinue } from '@/hooks/useConversations'
import { useClonesPagination } from '@/hooks/useClonesPagination'
import { useCarouselSlidesPerView } from '@/hooks/useCarouselSlidesPerView'
import AuthModal from '../Modal/AuthModal'
import { useClosePrelineModal } from '@/hooks/useClosePrelineModal'
import RequestCloneModal from '@/components/Modal/RequestCloneModal'
import CreatorProgramModal from '../Modal/CreatorProgramModal'
import { ReadonlyURLSearchParams, usePathname, useSearchParams, useRouter } from 'next/navigation'

export default function HomeScreen({ initialQ }: { initialQ: string }) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  const [searchInput, setSearchInput] = useState(initialQ)
  const [searchParam, setSearchParam] = useState(initialQ)
  const [showSearchGrid, setShowSearchGrid] = useState(false)
  const duration = 500

  useEffect(() => {
    require('preline')
  }, [])

  useClosePrelineModal()



  // fetch chars
  const topQueryParams = {
    sort: CloneSortType["TOP"],
    limit: 9
  }

  const trendingQueryParams = {
    sort: CloneSortType["HOT"],
    limit: 21
  }

  let continueQueryParams = {
    offset: 0,
    limit: 20
  }

  // chars data
  const { data: trendingChars, isLoading: isTrendingLoading } = useQueryClones(trendingQueryParams);
  const { data: topChars, isLoading: isTopLoading } = useQueryClones(topQueryParams);
  const { data: continueChars, isLoading: isContinueLoading } = useQueryConversationsContinue(continueQueryParams)
  const { slidesPerView, isLoadingSlidesPerView } = useCarouselSlidesPerView()

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

  function updateUrlParams(searchParams: ReadonlyURLSearchParams, updateKey: string, updateValue: string): string {
    const newParams = new URLSearchParams(searchParams.toString());
    if (updateValue) {
      newParams.set(updateKey, updateValue);
    } else {
      newParams.delete(updateKey);
    }
    return `?${newParams.toString()}`;
  }

  // search delay
  useEffect(() => {
    const timer = setTimeout(() => {
      if (router) {
        router.push(pathname + updateUrlParams(searchParams, "q", searchInput))
      }
      setSearchParam(searchInput)
    }, duration)
    return () => clearTimeout(timer)
  }, [searchInput])

  // character grid state
  const queryParamsSearch = {
    // name: searchParam,
    sort: CloneSortType["TOP"],
    similar: searchParam,
    limit: 30
  }

  const {
    paginatedData: searchedCharacters,
    isLastPage: isLastSearchedCharactersPage,
    isLoading: isLoadingSearchedCharacters,
    size,
    setSize
  } = useClonesPagination(queryParamsSearch)


  // top bar state
  const [isInputActive, setIsInputActive] = useState(searchInput !== "")

  return (
    <div className='pb-[75px]'>
      <AlertBar />

      <TopBar
        searchInput={searchInput}
        isInputActive={isInputActive}
        setIsInputActive={(x: boolean) => { setIsInputActive(x) }}
        onSearchInput={(x) => setSearchInput(x)}
        clearSearchInput={() => setSearchInput('')}
      />
      {showSearchGrid && (
        <ScaleFadeIn loaded={showSearchGrid} duration={duration}>
          <CharacterGrid
            characters={searchedCharacters}
            loading={isLoadingSearchedCharacters}
            fetchMoreData={() => setSize(size + 1)}
            hasMoreData={!isLastSearchedCharactersPage}
          />
        </ScaleFadeIn>
      )}

      {!showSearchGrid && (
        <ScaleFadeIn loaded={!searchInput} duration={duration}>
          {(isTrendingLoading || isContinueLoading || isTopLoading || isLoadingSlidesPerView) ? (
            <div className='grid place-items-center'
              style={{
                height: 'calc(100vh - 48px - 84px)'
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
          ) : (
            <>
              <Carousel
                characters={topChars}
                name='Top Characters'
                isBigCarousel={true}
                slidesPerView={slidesPerView!.big}
                zIndex={40}
              />
              {/* <StatBar /> */}
              <Carousel
                characters={trendingChars}
                name='Trending'
                isBigCarousel={false}
                slidesPerView={slidesPerView!.normal}
                zIndex={20}
              />
              {continueChars && continueChars.length > 0 && (
                <Carousel
                  characters={continueChars}
                  name='Continue Chatting'
                  isBigCarousel={false}
                  slidesPerView={slidesPerView!.normal}
                  zIndex={30}
                />
              )}
              {/* <Carousel
            characters={anime}
            name='Anime'
            isBigCarousel={false}
            zIndex={10}
          /> */}</>
          )}
        </ScaleFadeIn>
      )}
      <AuthModal />
      <RequestCloneModal />
      <CreatorProgramModal />
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
