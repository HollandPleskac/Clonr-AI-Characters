'use client'

import React, { useEffect, useRef, useState } from 'react'

import Link from 'next/link'
import Image from 'next/image'

import SearchIcon from './SearchIcon'
import XIcon from './XIcon'
import { usePathname } from 'next/navigation'

export default function TopBarStatic(): React.ReactElement {
  const pathname = usePathname()

  return (
    <div className='flex h-[72px] w-full sticky top-0 items-center justify-between border-b border-[#1d1e1e] px-[4%] bg-black z-50'>
      <div className='flex items-center gap-x-4'>
        {/* <h3 className='text-[22px] font-semibold leading-5 text-white cursor-pointer'>
          Cloner.ai
        </h3> */}
        <Link href='/' className='flex items-center cursor-pointer'>
          <div className='h-8 w-8 relative'>
            <Image
              src='/clonr-logo.png'
              alt='logo'
              layout='fill'
              objectFit='cover'
              className=''
            />
          </div>
          <h3 className='ml-2 text-[30px] font-semibold leading-5 text-white font-fabada'>
            clonr
          </h3>
          <p className='text-white font-thin ml-2 align-middle'>users</p>
        </Link>
        <Link
          href='/'
          className={`transition duration-200 ml-4 ${
            pathname === '/'
              ? 'text-white font-semibold'
              : 'text-[#e5e5e5] hover:text-[#979797]'
          }`}
        >
          Home
        </Link>

        <Link
          href='mailto:email@example.com'
          className={`transition duration-200 ${
            pathname === '/create'
              ? 'text-white font-semibold'
              : 'text-[#e5e5e5]'
          }`}
        >
          Contact
        </Link>

        <Link
          href='#'
          className={`transition duration-200 ${
            pathname === '/create'
              ? 'text-white font-semibold'
              : 'text-[#e5e5e5]'
          }`}
        >
          <span>
            Create <sup className=''>Coming Soon</sup>
          </span>
        </Link>
      </div>

      <div className='flex items-center gap-x-4 text-white'>
        <button
          type='button'
          className='px-2 py-2 bg-purple-600 rounded-lg flex items-center gap-x-1 text-white'
          data-hs-overlay='#hs-slide-down-animation-modal'
        >
          Upgrade to Plus
        </button>
        <button className='cursor-pointer text-white h-[40px] w-[40px] bg-[#979797] rounded-full grid place-items-center hover:ring-1 hover:ring-[rgba(255,255,255,0.2)] '>
          J
        </button>
      </div>
    </div>
  )
}
