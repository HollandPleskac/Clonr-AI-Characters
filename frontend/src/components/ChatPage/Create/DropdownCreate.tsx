'use client'

import React from 'react'
import HorizontalDotsBig from '@/svg/ChatPage/Chat/horizontal-dots-big.svg'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useSidebarClonesPagination } from '@/hooks/useSidebarClonesPagination'

type ChatDropdownProps = {
  characterId: string
  lastConversationId: string
}

const Dropdown = ({ characterId, lastConversationId }: ChatDropdownProps) => {
  
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
            href={`http://localhost:3000/clones/${characterId}/conversations/${lastConversationId}`}
            className='w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300'>
            <div className='w-4 h-4'>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M15 20L7 12L15 4" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path> </g></svg>
            </div>
            View current chat
          </Link>

          <Link
            href={`http://localhost:3000/clones/${characterId}/conversations`}
            className='w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300'>
            <div className='w-4 h-4'>
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M19 19.2674V7.84496C19 5.64147 17.4253 3.74489 15.2391 3.31522C13.1006 2.89493 10.8994 2.89493 8.76089 3.31522C6.57467 3.74489 5 5.64147 5 7.84496V19.2674C5 20.6038 6.46752 21.4355 7.63416 20.7604L10.8211 18.9159C11.5492 18.4945 12.4508 18.4945 13.1789 18.9159L16.3658 20.7604C17.5325 21.4355 19 20.6038 19 19.2674Z" stroke="#9ca3af" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"></path> </g></svg>
            </div>
            View previous conversations
          </Link>

          <button
            onClick={() => {}}
            className='w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300'>
            <div className='w-4 h-4' >
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M5 22V14M5 14V4M5 14L7.47067 13.5059C9.1212 13.1758 10.8321 13.3328 12.3949 13.958C14.0885 14.6354 15.9524 14.7619 17.722 14.3195L17.9364 14.2659C18.5615 14.1096 19 13.548 19 12.9037V5.53669C19 4.75613 18.2665 4.18339 17.5092 4.3727C15.878 4.78051 14.1597 4.66389 12.5986 4.03943L12.3949 3.95797C10.8321 3.33284 9.1212 3.17576 7.47067 3.50587L5 4M5 4V2" stroke="#9ca3af" strokeWidth="1.5" strokeLinecap="round"></path> </g></svg>
            </div>
            Report
          </button>
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

export default Dropdown
