import { User } from '@/types'
import Link from 'next/link'
import React from 'react'
import { signOut, useSession } from "next-auth/react"
import Image from 'next/image'


export default function AccountDropdown() {
  const { data: session } = useSession({ required: false })

  return (
    <div className='hs-dropdown relative inline-flex justify-center items-center'>
      <button
        id='hs-dropdown-with-header'
        type='button'
        disabled={!session}
        className='hs-dropdown-toggle text-white h-[40px] w-[40px] bg-[#979797] rounded-full grid place-items-center hover:ring-1 hover:ring-[rgba(255,255,255,0.2)] '
      >
        {
          (session && session?.image) ? (
            <div className='h-[40px] w-[40px] relative'>
              <Image
                src={session?.image}
                alt={"alt"}
                layout='fill'
                objectFit='cover'
                className='rounded-full'
              />
            </div>
          ) : (
            session?.email?.charAt(0) || ''
          )
        }

      </button>

      {/* <div className='h-[40px] w-[40px] relative'>
          <Image
            src={session.image}
            alt={"alt"}
            layout='fill'
            objectFit='cover'
            className='rounded-full'
          />
        </div> */}

      <div
        className='hs-dropdown-menu transition-[opacity,margin] duration hs-dropdown-open:opacity-100 opacity-0 hidden min-w-[15rem]  shadow-md rounded-lg p-2 mt-2 bg-black border border-gray-700'
        aria-labelledby='hs-dropdown-with-header'
      >
        <div className='py-3 px-5 -m-2 rounded-t-lg bg-gray-700'>
          <p className='text-sm text-gray-400'>Signed in as</p>
          <p className='text-sm font-medium text-gray-300'>{session?.email || ''}</p>
        </div>
        <div className='mt-2 py-2 first:pt-0 last:pb-0'>
          <Link
            className='flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300'
            href='/account'
          >
            <div className='w-4 h-4' >
              <svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" fill="#9ca3af"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M0 0h48v48H0z" fill="none"></path> <g id="Shopicon"> <path d="M31.278,25.525C34.144,23.332,36,19.887,36,16c0-6.627-5.373-12-12-12c-6.627,0-12,5.373-12,12 c0,3.887,1.856,7.332,4.722,9.525C9.84,28.531,5,35.665,5,44h38C43,35.665,38.16,28.531,31.278,25.525z M16,16c0-4.411,3.589-8,8-8 s8,3.589,8,8c0,4.411-3.589,8-8,8S16,20.411,16,16z M24,28c6.977,0,12.856,5.107,14.525,12H9.475C11.144,33.107,17.023,28,24,28z"></path> </g> </g></svg>
            </div>
            Manage Account
          </Link>
          <button
            className='w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300'
            onClick={() => signOut()}
          >
            <div className='w-4 h-4' >
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M9.00195 7C9.01406 4.82497 9.11051 3.64706 9.87889 2.87868C10.7576 2 12.1718 2 15.0002 2L16.0002 2C18.8286 2 20.2429 2 21.1215 2.87868C22.0002 3.75736 22.0002 5.17157 22.0002 8L22.0002 16C22.0002 18.8284 22.0002 20.2426 21.1215 21.1213C20.2429 22 18.8286 22 16.0002 22H15.0002C12.1718 22 10.7576 22 9.87889 21.1213C9.11051 20.3529 9.01406 19.175 9.00195 17" stroke="#9ca3af" strokeWidth="1.5" strokeLinecap="round"></path> <path d="M15 12L2 12M2 12L5.5 9M2 12L5.5 15" stroke="#9ca3af" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"></path> </g></svg>
            </div>
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}