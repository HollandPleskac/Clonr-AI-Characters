'use client'

import React, { Ref } from 'react'
import ArrowLeftWhite from '@/svg/HomePage/arrow-left-white.svg'

interface SwiperBtnLeftProps {
  setRef: Ref<HTMLButtonElement>
}

const SwiperBtnLeft: React.FC<SwiperBtnLeftProps> = ({ setRef }) => {
  return (
    <button className={'group w-[4%]'} ref={setRef}>
      <div className='bg-bluef-400 h-full grid place-items-center '>
        <ArrowLeftWhite className='opacity-0 transform scale-[2.75] group-hover:scale-[3.5] group-hover/swiper:opacity-100 transition duration-100 ease-in-out' />
      </div>
    </button>
  )
}

export default SwiperBtnLeft
