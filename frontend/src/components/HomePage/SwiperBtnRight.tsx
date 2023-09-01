'use client'

import React, { Ref } from 'react'
import ArrowRightWhite from '@/svg/HomePage/arrow-right-white.svg'

interface SwiperBtnRightProps {
  setRef: Ref<HTMLButtonElement>
  hideArrow: boolean
}

const SwiperBtnRight: React.FC<SwiperBtnRightProps> = ({ setRef, hideArrow }) => {
  return (
    <button className={'group w-[4%] min-w-[4%]'} ref={setRef}>
      <div className='bg-bluef-400 h-full grid place-items-center '>
        {!hideArrow && (
          <ArrowRightWhite className='opacity-0 transform scale-[2.75] group-hover:scale-[3.5] group-hover/swiper:opacity-100 transition duration-100 ease-in-out' />
        )}
      </div>
    </button>
  )
}

export default SwiperBtnRight
