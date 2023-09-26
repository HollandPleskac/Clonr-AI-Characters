'use client'

import React, { useEffect, useRef, useState } from 'react'
// import { Navigation, Pagination, Scrollbar, A11y } from 'swiper/modules'
import SwiperBtnLeft from './SwiperBtnLeft'
import SwiperBtnRight from './SwiperBtnRight'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'

import NetflixCard from './NetflixCard'
import InfiniteScroll from 'react-infinite-scroll-component'
import { CloneSearchResult } from '@/client/models/CloneSearchResult'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useCarouselSlidesPerView } from '@/hooks/useCarouselSlidesPerView'
import RequestCloneModal from '../Modal/RequestCloneModal'
import FreeMessageLimitModal from '../Modal/FreeMessageLimitModal'
import SuggestionBar from './SuggestionBar'

type CustomCloneSearchResult = CloneSearchResult & {
  conversation_id?: string;
};

interface SearchGridProps {
  characters: CustomCloneSearchResult[]
  loading: boolean
  fetchMoreData: () => void
  hasMoreData: boolean
  showPadding2?: boolean
  conversationId?: string
  onCharacterClick: (characterId: string, convoId?: string) => void;
  handleClearSearchInput?: () => void
}

export default function CharacterGrid({
  characters,
  loading,
  fetchMoreData,
  hasMoreData,
  showPadding2 = false,
  handleClearSearchInput
}: SearchGridProps) {

  const router = useRouter()
  const { data: session, status } = useSession();
  const { slidesPerView, isLoadingSlidesPerView } = useCarouselSlidesPerView()
  console.log("slides per view view", slidesPerView, isLoadingSlidesPerView)


  const handleCharacterClick = (item: CustomCloneSearchResult) => {
    if (session) {
      const characterId = item.id;
      const convoId = item?.conversation_id; // use if exists

      if (convoId) {
        router.push(`/clones/${characterId}/conversations/${convoId}`);
      } else {
        router.push(`/clones/${characterId}/create`);
      }
    }
  };


  function calcEdgeCard(n: number): 'left' | 'right' | undefined {
    if (n % slidesPerView!.normal === 0) {
      return 'left'
    } else if ((n - (slidesPerView!.normal - 1)) % slidesPerView!.normal === 0) {
      return 'right'
    } else {
      return undefined
    }
  }

  return (
    <div className=''>
      {(loading || isLoadingSlidesPerView) && (
        <div
          className='text-white grid place-items-center'
          style={{ minHeight: 'calc(100vh - 72px - 48px)' }}
        >
          <p className='' >&nbsp;</p>
        </div>
      )}
      {/* <div
        className='text-white grid place-items-center'
        style={{ minHeight: 'calc(100vh - 72px - 48px)' }}
      >
        <div className='flex flex-col items-center justify-center' >
          <h1 className='text-4xl mb-8'> <span className='font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-700 '>No results found</span></h1>

          <div className='w-[50%] flex items-center h-[150px]' >
            <p
              onClick={
                () => {
                  const modalElement = document.querySelector('#hs-slide-down-animation-modal-request');
                  if (window.HSOverlay && typeof window.HSOverlay.close === 'function' && modalElement) {
                    window.HSOverlay.open(modalElement);
                  }
                }
              }
              className='text-center text-lg cursor-pointer'
            >Couldn’t find what your looking for, submit a <span className='text-blue-400 hover:cursor-pointer'>request</span> to us </p>
            <div className='w-px bg-gray-400 h-full mx-4' >&nbsp;</div>
            <p
              onClick={
                () => {
                  const modalElement = document.querySelector('#hs-slide-down-animation-modal-creator-program');
                  if (window.HSOverlay && typeof window.HSOverlay.close === 'function' && modalElement) {
                    window.HSOverlay.open(modalElement);
                  }
                }
              }
              className='text-center text-lg cursor-pointer' >Don’t want to wait, <span className='text-blue-400 hover:cursor-pointer'>join</span> the creator partner program</p>

          </div>
        </div>
      </div> */}
      {((!loading && !isLoadingSlidesPerView) && characters.length === 0) && (
        <div
          className='text-white grid place-items-center'
          style={{ minHeight: 'calc(100vh - 72px - 48px)' }}
        >
          {/* <p>Your search did not return any matches.</p> */}
          <div className='flex flex-col items-center justify-center' >
            <h1 className='text-4xl mb-8'> <span className='font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-700 '>No results found</span></h1>

            <div className='w-[75%] flex items-center h-[150px]' >
              <div className="flex flex-col w-full items-left">
              <p className='text-left text-lg align-top cursor-pointer'>
              Couldn't find what you're looking for?</p>
              <button onClick={() => {
                    const modalElement = document.querySelector('#hs-slide-down-animation-modal-request');
                    if (window.HSOverlay && typeof window.HSOverlay.close === 'function' && modalElement) {
                      window.HSOverlay.open(modalElement);
                    }
                  }} className='text-white hover:cursor-pointer px-4 py-2 bg-[#7e34dfca] rounded-lg font-sans hover:bg-[#7e34df] mt-2'>Submit a request</button>
              </div>
              <div className='w-px bg-gray-400 h-full mx-4' >&nbsp;</div>
              <div className="flex flex-col w-full items-left">
                <p className='text-left text-lg align-top cursor-pointer block' >Don't want to wait?</p>
                <button onClick={() => {
                      const modalElement = document.querySelector('#hs-slide-down-animation-modal-creator-program');
                      if (window.HSOverlay && typeof window.HSOverlay.close === 'function' && modalElement) {
                        window.HSOverlay.open(modalElement);
                      }
                    }} className='text-white hover:cursor-pointer px-4 py-2 bg-[#7e34dfca] rounded-lg font-sans hover:bg-[#7e34df] mt-2'>Become a Creator</button>
              </div>
            </div>
          </div>
        </div>
      )}
      {((!loading && !isLoadingSlidesPerView) && characters.length > 0) && (
       <div className={`flex flex-col ${showPadding2 ? 'pt-[50px]' : 'pt-[48px]'}`} >
        <SuggestionBar handleClearSearchInput={handleClearSearchInput} tags={Array.from(characters.map((e, _) => e.tags[0]?.name))} />
         <InfiniteScroll
          dataLength={characters?.length ?? 0}
          next={fetchMoreData}
          hasMore={hasMoreData}
          loader={<h4>Loading...</h4>}
          className={`grid gap-1 gap-y-10 pb-[100px] px-[4%]`}
          style={{
            gridTemplateColumns: `repeat(${slidesPerView!.normal}, 1fr)`,
            overflow: 'visible'
          }}
        >
          {characters.map((item, index) => {
            const edgeCard = calcEdgeCard(index)
            return (
              <div className='w-full z-0 hover:z-10' key={item.id}>
                <NetflixCard item={item} edgeCard={edgeCard} onClick={() => {
                  handleCharacterClick(item);
                }} />
              </div>
            )
          })}
          </InfiniteScroll>
       </div>
      )}

    </div>
  )
}
