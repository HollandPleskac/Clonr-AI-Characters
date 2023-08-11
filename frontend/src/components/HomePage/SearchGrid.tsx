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

interface SearchGridProps {
  characters: Character[]
  doneSearching: boolean
}

export default function SearchGrid({
  characters,
  doneSearching,
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

  return (
    <div className=''>
      {doneSearching && characters.length === 0 && (
        <div
          className='text-white grid place-items-center'
          style={{ minHeight: 'calc(100vh - 72px - 48px)' }}
        >
          <p>Your search did not return any matches.</p>
        </div>
      )}
      {doneSearching && characters.length > 0 && (
        <div
          className='grid grid-cols-6 gap-1 gap-y-10 pt-[100px] pb-[100px] px-[4%]'
          style={{ minHeight: 'calc(100vh - 72px - 48px)' }}
        >
          {characters.map((item, index) => {
            const edgeCard = calcEdgeCard(index)
            return (
              <div className='w-full z-0 hover:z-10' key={index}>
                <NetflixCard item={item} edgeCard={edgeCard} />
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
