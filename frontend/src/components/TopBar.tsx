'use client'

import React, { useEffect, useRef, useState } from 'react'

import Link from 'next/link'
import Image from 'next/image'

import SearchIcon from './SearchIcon'
import XIcon from './XIcon'
import { usePathname } from 'next/navigation'

interface TopBarProps {
  searchInput: string
  onSearchInput: (input: string) => void
  clearSearchInput: () => void
}

export default function TopBar({
  searchInput,
  onSearchInput,
  clearSearchInput,
}: TopBarProps): React.ReactElement {
  const pathname = usePathname()

  // search state
  const [isInputActive, setInputActive] = useState(false)
  const handleInputFocus = () => setInputActive(true)
  const handleInputBlur = () => {
    if (searchInput === '') setInputActive(false)
  }
  const inputRef = useRef<HTMLInputElement>(null)

  return (
    <div className='flex h-[72px] w-full sticky top-0 items-center justify-between border-b border-[#1d1e1e] px-[4%] bg-black z-50'>
      <div className='flex items-center gap-x-4'>
        {/* <h3 className='text-[22px] font-semibold leading-5 text-white cursor-pointer'>
          Cloner.ai
        </h3> */}
        <Link href="/" className='flex items-center cursor-pointer'>
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
          href='#'
          className={`transition duration-200 ml-4 ${pathname === '/'
              ? 'text-white font-semibold'
              : 'text-[#e5e5e5] hover:text-[#979797]'
            }`}
        >
          Home
        </Link>

        <Link
          href='mailto:email@example.com'
          className={`transition duration-200 ${pathname === '/create'
              ? 'text-white font-semibold'
              : 'text-[#e5e5e5]'
            }`}
        >
          Contact
        </Link>

        <Link
          href='#'
          className={`transition duration-200 ${pathname === '/create'
              ? 'text-white font-semibold'
              : 'text-[#e5e5e5]'
            }`}
        >
          <span>
            Create <sup className=''>Coming Soon</sup>
          </span>
        </Link>
      </div>
      {/* <div className='flex items-center text-white gap-x-2 text-sm cursor-pointer'>
          <div className='px-2 py-3 bg-black hover:bg-[#1d1e1e] rounded-lg flex items-center gap-x-1'>
            <StarIcon />
            Upgrade to Plus
          </div>
          <div className='px-2 py-3 bg-black hover:bg-[#1d1e1e] rounded-lg flex items-center gap-x-1'>
            <MailIcon />
            Contact
          </div>
          <div className='px-2 py-3 bg-black hover:bg-[#1d1e1e] rounded-lg flex items-center gap-x-1'>
            <ProfileIcon />
            Profile
          </div>
        </div> */}
      <div className='flex items-center gap-x-4 text-white'>
        {/* <button className='bg-gray-800 hover:bg-gray-700 rounded-lg p-2 grid place-items-center transition duration-200'>
          <SearchIcon />
        </button> */}
        <div
          className='relative group'
          onClick={() => {
            console.log('active')
            if (inputRef.current) {
              inputRef.current.focus()
            }
          }}
        >
          <button className='group absolute peer left-[10px] top-2 peer cursor-default'>
            <SearchIcon
              strokeClasses={` group-focus:stroke-[#5848BC] ${isInputActive ? 'stroke-[#5848BC]' : 'stroke-[#515151]'
                } transition duration-100 bg-red-400`}
            // strokeClasses='stroke-[#515151]'
            />
          </button>
          <input
            ref={inputRef}
            value={searchInput}
            onChange={(e) => onSearchInput(e.target.value)}
            onFocus={handleInputFocus}
            onBlur={handleInputBlur}
            className={`${isInputActive
                ? 'w-[300px] cursor-auto'
                : 'w-[44px] cursor-default'
              } focus:cursor-auto peer py-auto h-[40px]  transition-all  duration-500 rounded-lg border-none bg-[#1E1E1E] pr-0 pl-[44px] text-[15px] font-light leading-6 text-[#979797] focus:ring-1 focus:ring-transparent`}
            type='text'
            placeholder='Search'
            style={{ outline: 'none', resize: 'none' }}
          />
          <button
            className={`absolute right-[10px] top-3 ${searchInput === '' ? 'hidden' : 'flex'
              }`}
            onClick={clearSearchInput}
          >
            <XIcon />
          </button>
        </div>
        <button
          type='button'
          className='px-2 py-2 bg-purple-600 rounded-lg flex items-center gap-x-1 text-white'
          data-hs-overlay='#hs-slide-down-animation-modal'
        // data-hs-overlay="#hs-basic-modal"
        >
          {/* <PlusIcon /> */}
          Upgrade to Plus
        </button>
        <button className='cursor-pointer text-white h-[40px] w-[40px] bg-[#979797] rounded-full grid place-items-center hover:ring-1 hover:ring-[rgba(255,255,255,0.2)] '>
          J
        </button>
      </div>
    </div>
  )
}
