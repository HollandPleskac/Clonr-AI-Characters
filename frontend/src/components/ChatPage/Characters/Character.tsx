import React from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { SidebarClone } from '@/types'
import { formatDate } from '@/utils/formatDate'
import { useRouter } from 'next/navigation'
import { ConversationsService } from '@/client'
import { ConversationUpdate } from '@/client'

interface MyComponentProps {
  sidebarClone: SidebarClone
  currentCharacterId: string | null
}
const Character: React.FC<MyComponentProps> = ({
  sidebarClone,
  currentCharacterId,
}) => {
  const router = useRouter()

  async function hideConversation(conversationId) {
    const payload: ConversationUpdate = {
      hidden_in_sidebar: true
    }
    await ConversationsService.patchConversationConversationsConversationIdPatch(conversationId, payload)
  }

  function isYesterday(date: Date): boolean {
    // Get the current date and reset time to the start of today (midnight)
    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);
  
    // Get the start of yesterday by subtracting 24 hours from the start of today
    const yesterdayStart = new Date(todayStart.getTime() - 24 * 60 * 60 * 1000);
  
    return date >= yesterdayStart && date < todayStart;
  }

  function isAnyDayBeforeYesterday(date: Date): boolean {
    const todayStart = new Date();
    todayStart.setHours(0, 0, 0, 0);
  
    const yesterdayStart = new Date(todayStart.getTime() - 24 * 60 * 60 * 1000);
  
    return date < yesterdayStart;
  } 

  function formatTime(date: Date): string {
    const now = new Date();

    // Check if the date is between 24 and 48 hours ago
    if (isYesterday(date)) {
      return "Yesterday";
    } else if (isAnyDayBeforeYesterday(date)) {
      const day = date.getDate().toString().padStart(2, '0');
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const year = date.getFullYear().toString().slice(2);

      return `${month}/${day}/${year}`;
    }

    let hours = date.getHours();
    let minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
  
    hours = hours % 12;
    hours = hours ? hours : 12;
    const paddedMinutes = String(minutes).padStart(2, '0');
  
    return `${hours}:${paddedMinutes} ${ampm}`;
  }

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
          ? 'bg-[#5748bc3d] bg-opacity-5'
          : 'bg-transparent border-b-[0.5px]'
          } hover:bg-[#5748bc38] hover:bg-opacity-5 w-[348px] border-b-none border-b-white border-opacity-20 cursor-pointer py-2 flex justify-between items-center`}
      >
        <div className='w-full' >
          <div className={`flex items-center justify-between pl-4 py-2 m-[1px]`}>
          <div className='flex items-center w-full'>
            <div className='h-[45px] min-w-[45px] min-h-[45px] relative'>
              <Image
                src={sidebarClone.avatar_uri}
                alt='Character Profile Picture'
                layout='fill'
                objectFit='cover'
                className='rounded-full'
              />
            </div>
            <div className='ml-3 flex flex-col -translate-y-[1px] w-full'>
              <div className='mb-1 flex items-center justify-between w-full'>
                <h3 className='mr-2 text-[16px] font-bold leading-[22px] text-left line-clamp-1'>
                  {sidebarClone.clone_name}
                </h3>
                <h4 className='text-sm font-light leading-[18px] text-[#979797]  text-right'>
                  {/* {username} */}
                  {/* {sidebarClone.clone_id !== currentCharacterId && ' • ' + formatDate(new Date(sidebarClone.updated_at))} */}
                  {' • ' + formatTime(new Date(sidebarClone.updated_at))}
                </h4>
              </div>
              <div className='text-semibold text-[14px] text-left leading-[18px] line-clamp-1 text-[#919494] pr-2'>
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
        <button
          type='button'
          className='focus-visible:outline-offset-[-4px] rounded-full p-1 hover:bg-[#361f1f] mr-1'
          onClick={hideConversation}
          >
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <g id="Edit / Hide"> <path id="Vector" d="M3.99989 4L19.9999 20M16.4999 16.7559C15.1473 17.4845 13.6185 17.9999 11.9999 17.9999C8.46924 17.9999 5.36624 15.5478 3.5868 13.7788C3.1171 13.3119 2.88229 13.0784 2.7328 12.6201C2.62619 12.2933 2.62616 11.7066 2.7328 11.3797C2.88233 10.9215 3.11763 10.6875 3.58827 10.2197C4.48515 9.32821 5.71801 8.26359 7.17219 7.42676M19.4999 14.6335C19.8329 14.3405 20.138 14.0523 20.4117 13.7803L20.4146 13.7772C20.8832 13.3114 21.1182 13.0779 21.2674 12.6206C21.374 12.2938 21.3738 11.7068 21.2672 11.38C21.1178 10.9219 20.8827 10.6877 20.4133 10.2211C18.6338 8.45208 15.5305 6 11.9999 6C11.6624 6 11.3288 6.02241 10.9999 6.06448M13.3228 13.5C12.9702 13.8112 12.5071 14 11.9999 14C10.8953 14 9.99989 13.1046 9.99989 12C9.99989 11.4605 10.2135 10.9711 10.5608 10.6113" stroke="#525252" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path> </g> </g></svg>
          </button>
      </div>
    </button>
  )
}

export default Character
