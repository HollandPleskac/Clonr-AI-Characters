import React from 'react'
import ChevronRightPurple600 from '@/svg/ChatPage/Chat/chevron-right-purple-600.svg'
import ChevronRightPurple500 from '@/svg/ChatPage/Chat/chevron-right-purple-500.svg'
import Link from 'next/link'
import { Conversation } from '@/types'
import { formatDate } from '@/utils/formatDate'

type PreviousConversationsProps = {
  conversation: Conversation
  handleSetSelectedConversationIdToDelete: (id:string) => void
}

// TODO: edit
const PreviousConversations = ({
  conversation,
  handleSetSelectedConversationIdToDelete
}: PreviousConversationsProps) => {



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


    <div className='rounded-lg flex justify-between bg-[#121212] transition duration-200 w-full rounded-lg'>
      <Link className='py-4 pl-4 w-full rounded-l-lg hover:bg-gray-800' href={`/clones/${conversation.clone_id}/conversations/${conversation.id}`}>
        <div className='flex flex-col items-start mr-[5%] w-full'>
          <div className='flex items-center mb-2' >
            <h3 className='text-white text-xl font-semibold'> {formatTime(new Date(conversation.updated_at))} </h3>

            <div
              className={`font-semibold flex items-center shrink-0 ml-2 text-sm`}
            >
              <span className='text-gray-100' >28 msgs</span>
            </div>
          </div>
          <div
            className={`${conversation.memory_strategy === 'zero'
              ? 'text-purple-500'
              : 'text-purple-600'
              } font-semibold flex items-center shrink-0 mb-2 text-sm`}
          >
            <p className=''>
              {conversation.memory_strategy === 'zero'
                ? 'Zero Memory'
                : 'Long Term Memory'}

            </p>
          </div>
          <h4 className='text-gray-400 mb-1 text-[14px]'>
            You: <span className='italic'>{"TODO MAKE THIS LAST_USER_MESSAGE"}</span>
          </h4>
          <h4 className='text-gray-400 text-[14px]'>
            {conversation.clone_name}:{' '}
            <span className='italic'>{conversation.last_message}</span>
          </h4>
        </div>
      </Link>

      <button
        onClick={() => {
          handleSetSelectedConversationIdToDelete(conversation.id)
          const modalElement = document.querySelector('#hs-slide-down-animation-modal-confirm-delete');
          console.log("modal el", modalElement)
          if (window.HSOverlay && typeof window.HSOverlay.close === 'function' && modalElement) {
            window.HSOverlay.open(modalElement);
          }
        }}
        className='group cursor-pointer px-4 rounded-r-lg	' >
        <div
          className='grow p-4 rounded-full group-hover:bg-gray-600 transition duration-200 '
        >
          <div className='w-6 h-6'>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M18 6L17.1991 18.0129C17.129 19.065 17.0939 19.5911 16.8667 19.99C16.6666 20.3412 16.3648 20.6235 16.0011 20.7998C15.588 21 15.0607 21 14.0062 21H9.99377C8.93927 21 8.41202 21 7.99889 20.7998C7.63517 20.6235 7.33339 20.3412 7.13332 19.99C6.90607 19.5911 6.871 19.065 6.80086 18.0129L6 6M4 6H20M16 6L15.7294 5.18807C15.4671 4.40125 15.3359 4.00784 15.0927 3.71698C14.8779 3.46013 14.6021 3.26132 14.2905 3.13878C13.9376 3 13.523 3 12.6936 3H11.3064C10.477 3 10.0624 3 9.70951 3.13878C9.39792 3.26132 9.12208 3.46013 8.90729 3.71698C8.66405 4.00784 8.53292 4.40125 8.27064 5.18807L8 6M14 10V17M10 10V17" stroke="#9333ea" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>
          </div>
        </div>
      </button>
    </div>
  )
}

export default PreviousConversations
