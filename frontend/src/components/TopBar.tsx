'use client'

import React, { useEffect, useRef, useState } from 'react'

import Link from 'next/link'
import Image from 'next/image'

import SearchIcon from './SearchIcon'
import XIcon from './XIcon'
import { usePathname } from 'next/navigation'
import AccountDropdown from './AccountDropdown'
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
  const inputRefLg = useRef<HTMLInputElement>(null)
  const inputRefSm = useRef<HTMLInputElement>(null)

  return (
    <>
      <header className='sticky top-0 flex flex-wrap lg:justify-start lg:flex-nowrap w-full bg-black text-sm py-[19.2px] border-b border-[#1d1e1e] px-[4%] z-[50]'>
        <nav
          className=' w-full mx-auto px-4 lg:flex lg:items-center lg:justify-between'
          aria-label='Global'
        >
          <div className='flex items-center justify-between'>
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
            <div className='flex lg:hidden gap-x-4'>
              <div
                className='relative group'
                onClick={() => {
                  console.log('active')
                  if (inputRefSm.current) {
                    inputRefSm.current.focus()
                  }
                }}
              >
                <button className='group absolute peer left-[10px] top-[5.5px] peer cursor-default'>
                  <SearchIcon
                    strokeClasses={` group-focus:stroke-[#5848BC] ${
                      isInputActive ? 'stroke-[#5848BC]' : 'stroke-[#515151]'
                    } transition duration-100`}
                  />
                </button>
                <input
                  ref={inputRefSm}
                  value={searchInput}
                  onChange={(e) => onSearchInput(e.target.value)}
                  onFocus={handleInputFocus}
                  onBlur={handleInputBlur}
                  className={`${
                    isInputActive
                      ? 'w-[200px] cursor-auto bg-[#1E1E1E]'
                      : 'w-[44px] cursor-default bg-black'
                  } focus:cursor-auto peer py-auto h-[35px]  transition-all  duration-500 rounded-full border-none  pr-0 pl-[44px] text-[15px] font-light leading-6 text-[#979797] focus:ring-1 focus:ring-transparent`}
                  type='text'
                  placeholder='Search'
                  style={{ outline: 'none', resize: 'none' }}
                />
                <button
                  className={`absolute right-[10px] top-[9.5px] ${
                    searchInput === '' ? 'hidden' : 'flex'
                  }`}
                  onClick={clearSearchInput}
                >
                  <XIcon />
                </button>
              </div>
              <button
                type='button'
                className='w-[35px] h-[35px] hs-collapse-toggle p-2 inline-flex justify-center items-center gap-2 rounded-md border font-medium bg-white text-gray-700 shadow-sm align-middle hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white focus:ring-purple-600 transition-all text-sm dark:bg-slate-900 dark:hover:bg-slate-800 dark:border-gray-700 dark:text-gray-400 dark:hover:text-white dark:focus:ring-offset-gray-800'
                data-hs-collapse='#navbar-collapse-with-animation'
                aria-controls='navbar-collapse-with-animation'
                aria-label='Toggle navigation'
              >
                <svg
                  className='hs-collapse-open:hidden w-4 h-4'
                  width='16'
                  height='16'
                  fill='currentColor'
                  viewBox='0 0 16 16'
                >
                  <path
                    fillRule='evenodd'
                    d='M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z'
                  />
                </svg>
                <svg
                  className='hs-collapse-open:block hidden w-4 h-4'
                  width='16'
                  height='16'
                  fill='currentColor'
                  viewBox='0 0 16 16'
                >
                  <path d='M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z' />
                </svg>
              </button>
            </div>
          </div>
          <div
            id='navbar-collapse-with-animation'
            className='hs-collapse hidden overflow-hidden transition-all duration-300 basis-full grow lg:block'
          >
            <div className='flex mt-5 lg:items-center lg:justify-between lg:mt-0 lg:pl-5'>
              <div className='flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-start'>
                <Link
                  href='/'
                  className={`transition duration-200 lg:ml-4 ${
                    pathname === '/'
                      ? 'text-white font-semibold'
                      : 'text-[#e5e5e5] hover:text-[#979797]'
                  } translate-y-[6px]`}
                >
                  Home
                </Link>

                <Link
                  href='/pricing'
                  className={`transition duration-200 ${
                    pathname === '/create'
                      ? 'text-white font-semibold'
                      : 'text-[#e5e5e5] hover:text-[#979797]'
                  } translate-y-[6px]`}
                >
                  Pricing
                </Link>

                <Link
                  href='#'
                  className={`transition duration-200 ${
                    pathname === '/create'
                      ? 'text-white font-semibold'
                      : 'text-[#e5e5e5]'
                  } translate-y-[6px]`}
                >
                  <span>
                    Create <sup className=''>Coming Soon</sup>
                  </span>
                </Link>
              </div>
              <div className='hidden lg:flex items-center gap-x-4 text-white'>
                <div
                  className='relative group'
                  onClick={() => {
                    console.log('active')
                    if (inputRefLg.current) {
                      inputRefLg.current.focus()
                    }
                  }}
                >
                  <button className='group absolute peer left-[10px] top-2 peer cursor-default'>
                    <SearchIcon
                      strokeClasses={` group-focus:stroke-[#5848BC] ${
                        isInputActive ? 'stroke-[#5848BC]' : 'stroke-[#515151]'
                      } transition duration-100`}
                    />
                  </button>
                  <input
                    ref={inputRefLg}
                    value={searchInput}
                    onChange={(e) => onSearchInput(e.target.value)}
                    onFocus={handleInputFocus}
                    onBlur={handleInputBlur}
                    className={`${
                      isInputActive
                        ? 'w-[300px] cursor-auto bg-[#1E1E1E]'
                        : 'w-[44px] cursor-default bg-black'
                    } focus:cursor-auto peer py-auto h-[40px]  transition-all  duration-500 rounded-full border-none  pr-0 pl-[44px] text-[15px] font-light leading-6 text-[#979797] focus:ring-1 focus:ring-transparent`}
                    type='text'
                    placeholder='Search'
                    style={{ outline: 'none', resize: 'none' }}
                  />
                  <button
                    className={`absolute right-[10px] top-3 ${
                      searchInput === '' ? 'hidden' : 'flex'
                    }`}
                    onClick={clearSearchInput}
                  >
                    <XIcon />
                  </button>
                </div>

                <AccountDropdown />
              </div>
            </div>
          </div>
        </nav>
      </header>
    </>
  )
}

{
  /* <button
          type='button'
          className='px-2 py-2 bg-purple-600 rounded-lg flex items-center gap-x-1 text-white'
          data-hs-overlay='#hs-slide-down-animation-modal'
        >
          Upgrade to Plus
        </button> */
}

{
  /*
   <button className='bg-gray-800 hover:bg-gray-700 rounded-lg p-2 grid place-items-center transition duration-200'>
          <SearchIcon />
        </button>
         */
}
