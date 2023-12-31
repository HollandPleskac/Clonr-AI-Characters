'use client'

import { useEffect } from 'react'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'
import Carousel from './Carousel'
import ScaleFadeIn from '../Transitions/ScaleFadeIn'
import { useQueryClones } from '@/hooks/useClones'
import { ColorRing } from "react-loader-spinner"
import { CloneSortType } from '@/client/models/CloneSortType'
import { useQueryConversationsContinue } from '@/hooks/useConversations'
import { useCarouselSlidesPerView } from '@/hooks/useCarouselSlidesPerView'
import AuthModal from '../Modal/AuthModal'
import { useClosePrelineModal } from '@/hooks/useClosePrelineModal'
import { useSearchContext } from '@/context/searchContext'

export default function HomeScreen() {
  const ctx = useSearchContext()

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

  return (
    <div className='pb-[75px]'>

      <ScaleFadeIn loaded={!(isTrendingLoading || isContinueLoading || isTopLoading)} duration={duration}>
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
          </>
        )}
      </ScaleFadeIn>
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
