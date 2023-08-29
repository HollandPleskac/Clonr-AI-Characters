import React from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { SidebarClone } from '@/types'
import { formatDate } from '@/utils/formatDate'

interface MyComponentProps {
  sidebarClone: SidebarClone
  currentCharacterId: string
}
const Character: React.FC<MyComponentProps> = ({
  sidebarClone,
  currentCharacterId,
}) => {
  return (
    <Link
      href={`/chat/${sidebarClone.clone_id}/${sidebarClone.id}`}
    >
      <div
        className={`${sidebarClone.clone_id === currentCharacterId
            ? ' border-[#252525] bg-[#282348]'
            : 'border-[#252525] bg-[#121212]'
          } border-r-none cursor-pointer border-b px-0`}
      >
        <div className='flex items-center justify-between px-4 py-[22px]'>
          <div className='flex items-center'>
            <div className='h-[55px] w-[55px] min-w-[55px] min-h-[55px] relative'>
              <Image
                src={sidebarClone.avatar_uri}
                alt='Character Profile Picture'
                layout='fill'
                objectFit='cover'
                className='rounded-full'
              />
            </div>
            <div className='ml-3 flex flex-col'>
              <div className='mb-1 flex items-center'>
                <h3 className='mr-2 text-[16px] font-bold leading-[22px]'>
                  {sidebarClone.clone_name}
                </h3>
                <h4 className='text-sm font-light leading-[18px] text-[#979797]'>
                  {/* {username} */}
                  {sidebarClone.clone_id !== currentCharacterId && ' • ' + formatDate(new Date(sidebarClone.updated_at))}
                </h4>
              </div>
              <div className='text-smibold text-[14px] leading-[18px] line-clamp-1'>
                {sidebarClone.clone_id !== currentCharacterId ? sidebarClone.last_message : "Current conversation"}
              </div>
            </div>
          </div>
          {/* <div className='grid w-6 place-items-center rounded-[10px]bg-[#3E347E] py-[2px] text-[12px] font-semibold leading-[16px]'>
            {3}
          </div> */}
        </div>
      </div>
    </Link>
  )
}

export default Character
