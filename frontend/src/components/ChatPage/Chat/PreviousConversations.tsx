import React from 'react'
import ChevronRightPurple600 from '@/svg/ChatPage/Chat/chevron-right-purple-600.svg'
import ChevronRightPurple500 from '@/svg/ChatPage/Chat/chevron-right-purple-500.svg'

const PreviousConversations = () => {
  return (
    <div
      style={{
        height: 'calc(100vh - 122px)',
      }}
      className='p-8 flex flex-col items-center px-[4%] gap-y-4'
    >
      <button className='group rounded-lg flex justify-between items-center bg-black hover:bg-gray-800 transition duration-200 w-full rounded-lg p-4 '>
        <div className='flex flex-col items-start '>
          <h3 className='text-white text-xl font-semibold mb-2'>23 Days Ago</h3>
          <h4 className='text-gray-400 mb-1 text-[14px]'>
            You: <span className='italic'>hey whats up?</span>
          </h4>
          <h4 className='text-gray-400 text-[14px]'>
            Barack Obama:{' '}
            <span className='italic'>nothing much how about you?</span>
          </h4>
        </div>
        <div className=' text-purple-600 font-semibold flex items-center '>
          <p className=''>Long Term Memory</p>
          <div className='flex h-[24px] w-[24px] items-center justify-center ml-2'>
            <ChevronRightPurple600 />
          </div>
        </div>
      </button>
      <button className='group rounded-lg flex justify-between items-center bg-black hover:bg-gray-800 transition duration-200 w-full rounded-lg p-4 '>
        <div className='flex flex-col items-start '>
          <h3 className='text-white text-xl font-semibold mb-2'>23 Days Ago</h3>
          <h4 className='text-gray-400 mb-1 text-[14px]'>
            You: <span className='italic'>hey whats up?</span>
          </h4>
          <h4 className='text-gray-400 text-[14px]'>
            Barack Obama:{' '}
            <span className='italic'>nothing much how about you?</span>
          </h4>
        </div>
        <div className=' text-purple-500 font-semibold flex items-center '>
          <p className=''>Short Term Memory</p>
          <div className='flex h-[24px] w-[24px] items-center justify-center ml-2'>
            <ChevronRightPurple500 />
          </div>
        </div>
      </button>
      <button className='group rounded-lg flex justify-between items-center bg-black hover:bg-gray-800 transition duration-200 w-full rounded-lg p-4 '>
        <div className='flex flex-col items-start '>
          <h3 className='text-white text-xl font-semibold mb-2'>23 Days Ago</h3>
          <h4 className='text-gray-400 mb-1 text-[14px]'>
            You: <span className='italic'>hey whats up?</span>
          </h4>
          <h4 className='text-gray-400 text-[14px]'>
            Barack Obama:{' '}
            <span className='italic'>nothing much how about you?</span>
          </h4>
        </div>
        <div className=' text-purple-500 font-semibold flex items-center '>
          <p className=''>Short Term Memory</p>
          <div className='flex h-[24px] w-[24px] items-center justify-center ml-2'>
            <ChevronRightPurple500 />
          </div>
        </div>
      </button>
    </div>
  )
}

export default PreviousConversations
