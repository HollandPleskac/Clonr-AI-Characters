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
import { Character } from '@/types'
import Image from 'next/image'
import InfiniteScroll from 'react-infinite-scroll-component'
import { CloneSearchResult } from '@/client/models/CloneSearchResult'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import AuthModal from '../AuthModal'
import { useCarouselSlidesPerView } from '@/hooks/useCarouselSlidesPerView'

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
}

export default function CharacterGrid({
  characters,
  loading,
  fetchMoreData,
  hasMoreData,
  showPadding2 = false,
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

  if (!characters) {
    return (
      <div>
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <div className=''>
      {loading && (
        <div
          className='text-white grid place-items-center'
          style={{ minHeight: 'calc(100vh - 72px - 48px)' }}
        >
          <p></p>
        </div>
      )}
      {!loading && characters.length === 0 && (
        <div
          className='text-white grid place-items-center'
          style={{ minHeight: 'calc(100vh - 72px - 48px)' }}
        >
          <p>Your search did not return any matches.</p>
        </div>
      )}
      {(!loading && !isLoadingSlidesPerView) && characters.length > 0 && (
        <InfiniteScroll
          dataLength={characters?.length ?? 0}
          next={fetchMoreData}
          hasMore={hasMoreData}
          loader={<h4>Loading...</h4>}
          className={`grid gap-1 gap-y-10 ${showPadding2 ? 'pt-[50px]' : 'pt-[100px]'} pb-[100px] px-[4%]`}
          style={{
            gridTemplateColumns: `repeat(${slidesPerView!.normal}, 1fr)`,
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
      )}
    </div>
  )
}
