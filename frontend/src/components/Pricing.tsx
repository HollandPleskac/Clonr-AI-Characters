import React from 'react'

const Pricing = () => {
  return (
    <div className='mt-0 flex justify-center gap-6 lg:items-center'>
      <div className='w-[287px] flex flex-col  border-2 border-transparent text-center shadow-xl rounded-xl p-8'>
        {/* <p className='mb-3'>
          <span className='inline-flex items-center gap-1.5 py-1.5 px-3 rounded-md text-xs uppercase font-semibold bg-blue-100 text-blue-800 dark:bg-blue-600 dark:text-white'>
            Most popular
          </span>
        </p> */}
        <h4 className='font-medium text-lg text-gray-800 dark:text-gray-200'>
          Get Clonr Plus
        </h4>
        <span className='mt-5 font-bold text-5xl text-gray-800 dark:text-gray-200'>
          <span className='font-bold text-2xl mr-1'>$</span>
          19
          <span className='ml-2 text-lg font-normal text-gray-500'>/ mon</span>
        </span>
        <p className='mt-2 text-sm text-gray-500'>
          All the basics for starting a new business
        </p>

        <ul className='mt-7 space-y-2.5 text-sm'>
          <li className='flex space-x-2'>
            <svg
              className='flex-shrink-0 h-5 w-5 text-blue-600'
              width='16'
              height='16'
              viewBox='0 0 16 16'
              fill='none'
              xmlns='http://www.w3.org/2000/svg'
            >
              <path
                d='M11.5219 4.0949C11.7604 3.81436 12.181 3.78025 12.4617 4.01871C12.7422 4.25717 12.7763 4.6779 12.5378 4.95844L6.87116 11.6251C6.62896 11.91 6.1998 11.94 5.9203 11.6916L2.9203 9.02494C2.64511 8.78033 2.62032 8.35894 2.86493 8.08375C3.10955 7.80856 3.53092 7.78378 3.80611 8.02839L6.29667 10.2423L11.5219 4.0949Z'
                fill='currentColor'
              />
            </svg>
            <span className='text-gray-800 dark:text-gray-400'>2 users</span>
          </li>

          <li className='flex space-x-2'>
            <svg
              className='flex-shrink-0 h-5 w-5 text-blue-600'
              width='16'
              height='16'
              viewBox='0 0 16 16'
              fill='none'
              xmlns='http://www.w3.org/2000/svg'
            >
              <path
                d='M11.5219 4.0949C11.7604 3.81436 12.181 3.78025 12.4617 4.01871C12.7422 4.25717 12.7763 4.6779 12.5378 4.95844L6.87116 11.6251C6.62896 11.91 6.1998 11.94 5.9203 11.6916L2.9203 9.02494C2.64511 8.78033 2.62032 8.35894 2.86493 8.08375C3.10955 7.80856 3.53092 7.78378 3.80611 8.02839L6.29667 10.2423L11.5219 4.0949Z'
                fill='currentColor'
              />
            </svg>
            <span className='text-gray-800 dark:text-gray-400'>
              Plan features
            </span>
          </li>

          <li className='flex space-x-2'>
            <svg
              className='flex-shrink-0 h-5 w-5 text-blue-600'
              width='16'
              height='16'
              viewBox='0 0 16 16'
              fill='none'
              xmlns='http://www.w3.org/2000/svg'
            >
              <path
                d='M11.5219 4.0949C11.7604 3.81436 12.181 3.78025 12.4617 4.01871C12.7422 4.25717 12.7763 4.6779 12.5378 4.95844L6.87116 11.6251C6.62896 11.91 6.1998 11.94 5.9203 11.6916L2.9203 9.02494C2.64511 8.78033 2.62032 8.35894 2.86493 8.08375C3.10955 7.80856 3.53092 7.78378 3.80611 8.02839L6.29667 10.2423L11.5219 4.0949Z'
                fill='currentColor'
              />
            </svg>
            <span className='text-gray-800 dark:text-gray-400'>
              Product support
            </span>
          </li>
        </ul>

        <a
          className='mt-5 inline-flex justify-center items-center gap-x-3 text-center bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 focus:ring-offset-white transition py-3 px-4 dark:focus:ring-offset-gray-800'
          href='https://github.com/htmlstreamofficial/preline/tree/main/examples/html'
        >
          Subscribe
        </a>
      </div>
    </div>
  )
}

export default Pricing
