'use client'

import { useEffect, useState } from 'react'
//import { cookies } from 'next/headers'
// import Cookies from 'js-cookie';
import { redirect } from 'next/navigation'
import { Character } from '@/types';
import cookiesToString from '@/utils/cookiesToString';
import CharactersSidebar from '@/components/ChatPage/Characters/Sidebar'
import ChatScreen from '@/components/ChatPage/Chat'
import { useQueryClonesById } from '@/hooks/useClones'
import Conversations from '@/components/ChatPage/Conversations';
import { useSidebarClonesPagination } from '@/hooks/useSidebarClonesPagination';
import Link from 'next/link';
import { ColorRing } from 'react-loader-spinner';
import SmallNav from '@/components/ChatPage/Characters/SmallSidebar'


interface SizeProps {
  height: number,
  width: number,
}

function WavingRobot({ height, width }: SizeProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={width}
      height={height}
      viewBox="0 0 500 250"
    >
      <path
        fill="#7503E4"
        fillOpacity="0.14"
        stroke="#4D48F1"
        strokeWidth="4"
        d="M-62.93-4.065v-13.202h0c0-25.219 11.954-45.663 26.699-45.663h72.462c14.745 0 26.699 20.444 26.699 45.663v34.534h0c0 25.219-11.954 45.663-26.699 45.663h-72.462 0c-14.745 0-26.699-20.444-26.699-45.663z"
        transform="matrix(1 0 0 .5847 338.377 152.338)"
      ></path>
      <path
        fill="#9a4af6"
        fillOpacity="0"
        stroke="#4D48F1"
        strokeWidth="4"
        d="M-6.19 5.158L0-5.158 6.19 5.158"
        transform="translate(314.65 145.805)"
      ></path>
      <path
        fill="#9a4af6"
        fillOpacity="0"
        stroke="#4D48F1"
        strokeWidth="3"
        d="M0 9.029V-9.03"
        transform="translate(338.377 105.345)"
      ></path>
      <path
        fill="#9a4af6"
        fillOpacity="0"
        stroke="#4D48F1"
        strokeWidth="4"
        d="M-6.19 5.158L0-5.158 6.19 5.158"
        transform="translate(361.354 145.18)"
      ></path>
      <path
        fill="#9a4af6"
        fillOpacity="0"
        stroke="#4894F1"
        strokeWidth="0"
        d="M0-19.257c10.63 0 19.257 8.627 19.257 19.257S10.63 19.257 0 19.257-19.257 10.63-19.257 0-10.63-19.257 0-19.257z"
        transform="translate(333.906 145.805)"
      ></path>
      <path
        fill="#9a4af6"
        fillOpacity="0"
        stroke="#4D48F1"
        strokeWidth="4"
        d="M11.098 18.443l-22.196-36.886"
        transform="translate(257.191 155.465)"
      ></path>
      <path
        fill="#6D17DC"
        stroke="#4894F1"
        strokeWidth="0"
        d="M0-34.388c18.982 0 34.388 15.406 34.388 34.388S18.982 34.388 0 34.388-34.388 18.982-34.388 0-18.982-34.388 0-34.388z"
        transform="translate(338.377 99.75) scale(.19276)"
      ></path>
      <path
        fill="#9a4af6"
        fillOpacity="0"
        stroke="#4894F1"
        strokeWidth="0"
        d="M0-21.664c11.959 0 21.664 9.705 21.664 21.664 0 11.959-9.705 21.664-21.664 21.664-11.959 0-21.664-9.705-21.664-21.664 0-11.959 9.705-21.664 21.664-21.664z"
        transform="matrix(.25822 0 0 .25822 338.377 99.75)"
      ></path>
      <path
        fill="#FFF"
        fillOpacity="0"
        stroke="#4D48F1"
        strokeWidth="4"
        d="M-4.47-10.198l8.94 20.396"
        transform="translate(411.938 183.043)"
      ></path>
    </svg>
  );
}

export default function DefaultClonesPage({
  params,
}: {
  params: { cloneId: string }
}) {
  useEffect(() => {
    require('preline')
  }, [])

  const [searchParam, setSearchParam] = useState('')

  const sidebarClonesQueryParams = {
    limit: 10,
    name: searchParam,
  }

  const {
    paginatedData: cloneChats,
    isLoading,
    isLastPage,
    size,
    setSize,
    mutate
  } = useSidebarClonesPagination(sidebarClonesQueryParams)


  const newWelcome = (
    <>
      <h1 className='text-4xl'> <span className='font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-700 '>Welcome to Clonr Chat</span></h1>
      <p className='leading-8 text-lg'>To begin chatting, please select a Clone from either the <Link href="/" className='text-blue-400 hover:cursor-pointer'>Home</Link>{" "}page or the <Link href="/browse" className='text-blue-400 hover:cursor-pointer'>Browse</Link>{" "}page. These pages can be reached by clicking the icons located at the top of the sidebar 👈.
      <br/><br/>
      All of the clones you are chatting with will appear on the left sidebar, and, any conversations with them will appear here.
      <br /><br/>
      We're stoked to see you 🙌, and happy chatting 🎉</p>
    </>
  )

  const oldWelcome = (
    <>
      <h1 className='text-4xl'> <span className='font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-700 '>Welcome Back </span></h1>
      <p className='hidden lg:inline-block leading-8 text-lg'>To pick up where you left off, or to create a new conversation 🌱, please select a clone from the left 👈.
      <br /><br/>
      Looking to try something new? Head back to either the <Link href="/browse" className='text-blue-400 hover:cursor-pointer'>Home</Link>{" "}page or the <Link href="/browse" className='text-blue-400 hover:cursor-pointer'>Browse</Link>{" "}page (by clicking the icons located above the sidebar).
      <br/><br/>
      We're stoked to see you back 🙌, and happy chatting 🎉</p>

      <p className='lg:hidden leading-8 text-lg'>To pick up where you left off, or to create a new conversation 🌱, please select a clone from the expandable sidebar on the left 👈.
      <br /><br/>
      Looking to try something new? Head back to either the <Link href="/browse" className='text-blue-400 hover:cursor-pointer'>Home</Link>{" "}page or the <Link href="/browse" className='text-blue-400 hover:cursor-pointer'>Browse</Link>{" "}page (by clicking the icons located above the sidebar).
      <br/><br/>
      We're stoked to see you back 🙌, and happy chatting 🎉</p>
    </>
  )

  // Render Page
  return (
    <div
      className='bg-gray-900 w-full flex justify-center items-center overflow-hidden'
      style={{ height: 'calc(100vh)' }}>
      <CharactersSidebar
        currentCharacterId={params.cloneId}
        cloneChats={cloneChats}
        isLoading={isLoading}
        isLastPage={isLastPage}
        size={size}
        setSize={setSize}
        setSearchParam={setSearchParam}
        mutate={mutate}
      />
      <div className='w-[100%] border-r-[2px] border-[#252525] bg-[#121212] lg:inline'>
        {/* <div
          className="flex flex-col items-center h-screen">
          <div className='text-left w-[100vh]'>
            <WavingRobot height={600} width={600} />
          </div>          
        </div> */}
        <div className='h-screen w-full place-items-center grid' >
          {/* <div className='grid'> */}
            {/* <div className=''>
              <WavingRobot height={300} width={300} />                    
            </div> */}
            <div className='absolute top-6 left-6' >
              <SmallNav characterId={params.cloneId} />
            </div>
            <div className='text-white text-left w-1/2'>
              {
                (!isLoading && cloneChats && cloneChats.length > 0) && oldWelcome
              }
              {
                (!isLoading && (!cloneChats || cloneChats.length === 0)) && newWelcome
              }
            </div>
        </div>
      </div>
    </div>
  )
}