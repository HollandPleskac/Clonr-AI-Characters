'use client'

import React from 'react'
import HorizontalDotsBig from '@/svg/ChatPage/Chat/horizontal-dots-big.svg'
import { useState, useEffect } from 'react'
import Link from 'next/link'

type ChatDropdownProps = {
  characterId: string
}

const ChatDropdown = ({ characterId }: ChatDropdownProps) => {
  return (
    <div className='hs-dropdown relative inline-flex justify-center items-center'>
      <button
        id='hs-dropdown-with-title'
        type='button'
        className='hs-dropdown-toggle inline-flex justify-center items-center bg-gray-800 hover:bg-gray-700 rounded-full p-2 transition duration-200'
      >
        <HorizontalDotsBig />
      </button>

      <div
        className='z-[100] hs-dropdown-menu transition-[opacity,margin] duration hs-dropdown-open:opacity-100 opacity-0 hidden min-w-[15rem] bg-white shadow-md rounded-lg p-2 mt-2 divide-y divide-gray-200 dark:bg-black dark:border dark:border-gray-700 dark:divide-gray-700'
        aria-labelledby='hs-dropdown-with-title'
      >
        <div className='py-2 first:pt-0 last:pb-0'>
          {/* <span className='block py-2 px-3 text-xs font-medium uppercase text-gray-400 dark:text-gray-500'>
            Options
          </span> */}

          <Link
            href={`http://localhost:3000/clones/${characterId}/create`}
            className='w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300'>
            <div className='w-4 h-4'>
              <svg
                width='16'
                height='16'
                viewBox='0 0 24 24'
                fill='none'
                xmlns='http://www.w3.org/2000/svg'
              >
                <path
                  d='M18.364 8.05026L17.6569 7.34315C14.5327 4.21896 9.46734 4.21896 6.34315 7.34315C3.21895 10.4673 3.21895 15.5327 6.34315 18.6569C9.46734 21.7811 14.5327 21.7811 17.6569 18.6569C19.4737 16.84 20.234 14.3668 19.9377 12.0005M18.364 8.05026H14.1213M18.364 8.05026V3.80762'
                  stroke='currentColor'
                  strokeWidth='1.5'
                  strokeLinecap='round'
                  strokeLinejoin='round'
                />
              </svg>
            </div>
            Start new conversation
          </Link>

          <Link
            href={`http://localhost:3000/clones/${characterId}/conversations`}
            className='w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300'>
            <div className='w-4 h-4'>
              <svg
                width='16'
                height='16'
                viewBox='0 0 24 24'
                fill='none'
                xmlns='http://www.w3.org/2000/svg'
              >
                <path
                  d='M18.364 8.05026L17.6569 7.34315C14.5327 4.21896 9.46734 4.21896 6.34315 7.34315C3.21895 10.4673 3.21895 15.5327 6.34315 18.6569C9.46734 21.7811 14.5327 21.7811 17.6569 18.6569C19.4737 16.84 20.234 14.3668 19.9377 12.0005M18.364 8.05026H14.1213M18.364 8.05026V3.80762'
                  stroke='currentColor'
                  strokeWidth='1.5'
                  strokeLinecap='round'
                  strokeLinejoin='round'
                />
              </svg>
            </div>
            View previous conversations
          </Link>

          <button className='w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300'>
            <svg
              width='16'
              height='12'
              viewBox='0 -0.5 21 21'
              version='1.1'
              xmlns='http://www.w3.org/2000/svg'
              xmlnsXlink='http://www.w3.org/1999/xlink'
            >
              <title>report_flag [#1421]</title>
              <desc>Created with Sketch.</desc>
              <defs></defs>
              <g
                id='Page-1'
                stroke='none'
                stroke-width='1'
                fill='none'
                fill-rule='evenodd'
              >
                <g
                  id='Dribbble-Light-Preview'
                  transform='translate(-419.000000, -600.000000)'
                  fill='currentColor'
                >
                  <g id='icons' transform='translate(56.000000, 160.000000)'>
                    <path
                      d='M381.9,440 L369.3,440 C368.13975,440 367.2,440.895 367.2,442 L367.2,450 C367.2,451.105 368.13975,452 369.3,452 L381.9,452 C383.06025,452 384,451.105 384,450 L384,442 C384,440.895 383.06025,440 381.9,440 M365.1,441 L365.1,459 C365.1,459.552 364.6296,460 364.05,460 C363.4704,460 363,459.552 363,459 L363,441 C363,440.448 363.4704,440 364.05,440 C364.6296,440 365.1,440.448 365.1,441'
                      id='report_flag-[#1421]'
                    ></path>
                  </g>
                </g>
              </g>
            </svg>
            Remove Messages
          </button>

          {/* <button className='w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300'>
            <svg
              width='16'
              height='12'
              viewBox='0 -0.5 21 21'
              version='1.1'
              xmlns='http://www.w3.org/2000/svg'
              xmlnsXlink='http://www.w3.org/1999/xlink'
            >
              <title>report_flag [#1421]</title>
              <desc>Created with Sketch.</desc>
              <defs></defs>
              <g
                id='Page-1'
                stroke='none'
                stroke-width='1'
                fill='none'
                fill-rule='evenodd'
              >
                <g
                  id='Dribbble-Light-Preview'
                  transform='translate(-419.000000, -600.000000)'
                  fill='currentColor'
                >
                  <g id='icons' transform='translate(56.000000, 160.000000)'>
                    <path
                      d='M381.9,440 L369.3,440 C368.13975,440 367.2,440.895 367.2,442 L367.2,450 C367.2,451.105 368.13975,452 369.3,452 L381.9,452 C383.06025,452 384,451.105 384,450 L384,442 C384,440.895 383.06025,440 381.9,440 M365.1,441 L365.1,459 C365.1,459.552 364.6296,460 364.05,460 C363.4704,460 363,459.552 363,459 L363,441 C363,440.448 363.4704,440 364.05,440 C364.6296,440 365.1,440.448 365.1,441'
                      id='report_flag-[#1421]'
                    ></path>
                  </g>
                </g>
              </g>
            </svg>
            Report
          </button> */}
        </div>
        {/* <div className='py-2 first:pt-0 last:pb-0'>
          <span className='block py-2 px-3 text-xs font-medium uppercase text-gray-400 dark:text-gray-500'>
            Contacts
          </span>
          <a
            className='flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300'
            href='#'
          >
            <svg
              className='flex-none'
              width='16'
              height='16'
              viewBox='0 0 16 16'
              fill='currentColor'
            >
              <path d='M14 1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H4.414A2 2 0 0 0 3 11.586l-2 2V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12.793a.5.5 0 0 0 .854.353l2.853-2.853A1 1 0 0 1 4.414 12H14a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z' />
              <path d='M5 6a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm4 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm4 0a1 1 0 1 1-2 0 1 1 0 0 1 2 0z' />
            </svg>
            Contact support
          </a>
        </div> */}
      </div>
    </div>
  )
}

export default ChatDropdown
