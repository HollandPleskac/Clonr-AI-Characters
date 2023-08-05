'use client'

import React, { useEffect, useRef, useState } from 'react'
// import { Navigation, Pagination, Scrollbar, A11y } from 'swiper/modules'
import SwiperBtnLeft from './SwiperBtnLeft'
import SwiperBtnRight from './SwiperBtnRight'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'
import { Swiper, SwiperSlide } from 'swiper/react'

import NetflixCard from './NetflixCard'
import { Character } from '@/types'
import { Navigation, Pagination, Scrollbar } from 'swiper'

interface CarouselProps {
  characters: Character[]
  name: String
  slidesPerView: number
  zIndex: number
}

export default function Carousel({
  characters,
  name,
  slidesPerView,
  zIndex,
}: CarouselProps) {
  // carousel state
  const [leftSwiperIndex, setLeftSwiperIndex] = useState(0)

  const [prevEl, setPrevEl] = useState<HTMLElement | null>(null)
  const [nextEl, setNextEl] = useState<HTMLElement | null>(null)

  // manipulate swiper css to remove overflow style

  return (
    <div className='pt-4 mb-4 text-white'>
      <div className='px-[4%] mb-4'>
        <h2 className='text-[#E5E5E5] text-2xl font-semibold mb-1'>{name}</h2>
      </div>
      <div className='group/swiper flex w-full h-full'>
        <SwiperBtnLeft setRef={(node) => setPrevEl(node)} />
        <Swiper
          modules={[Navigation, Pagination, Scrollbar]}
          navigation={{ prevEl, nextEl }}
          spaceBetween={4}
          slidesPerView={slidesPerView}
          slidesPerGroup={6}
          loop={true}
          speed={1100}
          onSlideChange={(swiper) => setLeftSwiperIndex(swiper.realIndex)}
          onSwiper={(swiper) => setLeftSwiperIndex(swiper.realIndex)}
          className={`w-full`}
          style={{
            zIndex: zIndex,
          }}
        >
          {characters.map((item, index) => {
            return (
              <SwiperSlide
                key={index}
                className='w-1/6 cursor-pointer z-0 hover:z-10'
              >
                {/* lets say we have 6 cards per view and 15 cards*/}
                {/* Left Index if index === leftSwiperIndex */}
                {/* Right Index if index === leftSwiperIndex + 6 -1   because indexes start at 0 */}
                {/* RightIndex if index === (traditionalRightIndex - listLen)  card Index carousel overflows to on last scroll 0->5 6->11 12 -> 1 17-16 == 1*/}
                <NetflixCard
                  item={item}
                  edgeCard={
                    index === leftSwiperIndex
                      ? 'left'
                      : index === leftSwiperIndex + slidesPerView - 1 ||
                        index ===
                          leftSwiperIndex +
                            slidesPerView -
                            1 -
                            characters.length
                      ? 'right'
                      : undefined
                  }
                />
              </SwiperSlide>
            )
          })}
        </Swiper>
        <SwiperBtnRight setRef={(node) => setNextEl(node)} />
      </div>
    </div>
  )
}
