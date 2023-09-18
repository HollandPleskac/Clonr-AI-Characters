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
import { CloneSearchResult } from '@/client/models/CloneSearchResult'

import NetflixCard from './NetflixCard'
import { Navigation, Pagination, Scrollbar } from 'swiper/modules'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'

type CustomCloneSearchResult = CloneSearchResult & {
  conversation_id?: string;
};

interface CarouselProps {
  characters: CustomCloneSearchResult[]
  name: String
  isBigCarousel: boolean
  zIndex: number
  slidesPerView: number
  conversationId?: string
  onCharacterClick: (characterId: string, convoId?: string) => void;
}

export default function Carousel({
  characters,
  name,
  isBigCarousel = false,
  zIndex,
  slidesPerView
}: CarouselProps) {
  // carousel state
  const [leftSwiperIndex, setLeftSwiperIndex] = useState(0)

  const [prevEl, setPrevEl] = useState<HTMLElement | null>(null)
  const [nextEl, setNextEl] = useState<HTMLElement | null>(null)

  const router = useRouter()
  const { data: session, status } = useSession();

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

  return (
    <div className='pt-4 mb-4 text-white'>
      <div className='px-[4%] mb-4'>
        <h2 className='text-[#E5E5E5] text-xl font-semibold mb-1'>{name}</h2>
      </div>
      <div className='group/swiper flex w-full h-full'>
        <SwiperBtnLeft setRef={(node) => setPrevEl(node)} hideArrow={leftSwiperIndex === 0 && characters.length < slidesPerView * 2} />
        <Swiper
          modules={[Navigation, Pagination, Scrollbar]}
          navigation={{ prevEl, nextEl }}
          spaceBetween={4}
          slidesPerView={slidesPerView}
          slidesPerGroup={slidesPerView}
          loop={characters.length >= slidesPerView * 2 ? true : false}
          speed={1100}
          onSlideChange={(swiper) => setLeftSwiperIndex(swiper.realIndex)}
          onSwiper={(swiper) => setLeftSwiperIndex(swiper.realIndex)}
          className={`w-full`}
          style={{
            zIndex: zIndex,
            marginLeft: characters.length < slidesPerView ? '4%' : '',
            marginRight: characters.length < slidesPerView ? '4%' : ''
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
                {/* <h1 className='text-white'>{index}</h1>
                <h1 className='text-green-400'>{leftSwiperIndex}</h1> */}
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
                  onClick={() => {
                    handleCharacterClick(item);
                  }}
                />
              </SwiperSlide>
            )
          })}
        </Swiper>
        <SwiperBtnRight setRef={(node) => setNextEl(node)} hideArrow={characters.length <= slidesPerView || characters.length < slidesPerView * 2 && characters.length - leftSwiperIndex === slidesPerView} />
      </div>
    </div>
  )
}