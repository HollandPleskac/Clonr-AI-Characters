import React from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { SidebarClone } from '@/types'
import { formatDate } from '@/utils/formatDate'
import { useRouter } from 'next/navigation'

interface MyComponentProps {
  sidebarClone: SidebarClone
  currentCharacterId: string
}
const Character: React.FC<MyComponentProps> = ({
  sidebarClone,
  currentCharacterId,
}) => {
  const router = useRouter()
  return (
    <button
      // href={`/clones/${sidebarClone.clone_id}/conversations/${sidebarClone.id}`}
      onClick={async () => {
        if (window.innerWidth<1024) {
          const sidebarElement = document.querySelector('#docs-sidebar');
          await (window as any).HSOverlay.close(sidebarElement)
        }
        router.push(`/clones/${sidebarClone.clone_id}/conversations/${sidebarClone.id}`)
      }}
    >
      <div
        className={`${sidebarClone.clone_id === currentCharacterId
          ? ' border-[#252525] bg-[#302e32]'
          : 'border-[#252525] bg-transparent hover:border-[#252525] hover:bg-[#1f1e21]'
          } border-r-none cursor-pointer mr-0 pr-0 my-0 py-0`}
      >
        <div className='flex items-center justify-between px-4 py-4'>
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
                  {/* {sidebarClone.clone_id !== currentCharacterId && ' • ' + formatDate(new Date(sidebarClone.updated_at))} */}
                  {' • ' + formatDate(new Date(sidebarClone.updated_at))}
                </h4>
              </div>
              <div className='text-smibold text-[14px] leading-[18px] line-clamp-1'>
                {/* {sidebarClone.clone_id !== currentCharacterId ? sidebarClone.last_message : "Current conversation"} */}
                {sidebarClone.last_message}
              </div>
            </div>
          </div>
          {/* <div className='grid w-6 place-items-center rounded-[10px]bg-[#3E347E] py-[2px] text-[12px] font-semibold leading-[16px]'>
            {3}
          </div> */}
        </div>
      </div>
    </button>
  )
}

export default Character
