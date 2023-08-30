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


interface SearchGridProps {
  characters: any[]
  loading: boolean
  fetchMoreData: () => void
  hasMoreData: boolean
  showPadding2?: boolean
}

export default function CharacterGrid({
  characters,
  loading,
  fetchMoreData,
  hasMoreData,
  showPadding2 = false,
}: SearchGridProps) {

  function calcEdgeCard(n: number): 'left' | 'right' | undefined {
    if (n % 6 === 0) {
      return 'left'
    } else if ((n - 5) % 6 === 0) {
      return 'right'
    } else {
      return undefined
    }
  }

  // if characters is undefined, spinner with loading
  // if characters is empty, no matches

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
      {!loading && characters.length > 0 && (
        <InfiniteScroll
          dataLength={characters?.length ?? 0}
          next={fetchMoreData}
          hasMore={hasMoreData}
          loader={<h4>Loading...</h4>}
          className={`grid grid-cols-6 gap-1 gap-y-10 ${showPadding2 ? 'pt-[50px]' : 'pt-[100px]'} pb-[100px] px-[4%]`}
        >
          {characters.map((item, index) => {
            const edgeCard = calcEdgeCard(index)
            return (
              <div className='w-full z-0 hover:z-10' key={item.id}>
                <NetflixCard item={item} edgeCard={edgeCard} />
              </div>
            )
          })}
        </InfiniteScroll>
      )}

    </div>
  )
}