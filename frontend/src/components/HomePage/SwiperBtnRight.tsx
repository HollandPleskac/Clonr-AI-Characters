'use client'

import React, { Ref } from 'react'
import ArrowRightWhite from '@/icons/HomePage/arrow-right-white.svg'

interface SwiperBtnRightProps {
  setRef: Ref<HTMLButtonElement>
}

const SwiperBtnRight: React.FC<SwiperBtnRightProps> = ({ setRef }) => {
  return (
    <button className={'group w-[4%]'} ref={setRef}>
      <div className='bg-bluef-400 h-full grid place-items-center '>
        <ArrowRightWhite className='opacity-0 transform scale-[2.75] group-hover:scale-[3.5] group-hover/swiper:opacity-100 transition duration-100 ease-in-out' />
      </div>
    </button>
  )
}

export default SwiperBtnRight
