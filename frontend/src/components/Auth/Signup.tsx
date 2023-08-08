'use client'
import Link from 'next/link'
import React from 'react'

const SignupModal = () => {
  return (
    <main className='w-full max-w-md mx-auto p-6'>
      <div className='mt-7 border border-gray-200 rounded-xl shadow-sm dark:bg-gray-800 dark:border-gray-700'>
        <div className='p-4 sm:p-7'>
          <div className='text-start'>
            <h1 className='mb-2 block text-2xl font-bold text-gray-800 dark:text-white'>
              Sign up
            </h1>
          </div>

          <div className='mt-5 flex flex-col gap-y-4 '>
            <div className='flex items-start'>
              <div className='flex items-center h-5'>
                <input
                  id='remember'
                  aria-describedby='remember'
                  type='checkbox'
                  className='w-4 h-4 border focus:ring-transparent border-gray-300 rounded bg-gray-50  dark:bg-gray-700 dark:border-gray-600  checked:text-purple-500'
                  required={false}
                  style={{ boxShadow: 'none' }}
                />
              </div>
              <div className='ml-3 text-sm'>
                <label
                  htmlFor='terms'
                  className='font-light text-gray-500 dark:text-gray-300'
                >
                  I accept the{' '}
                  <a
                    className='font-medium text-purple-600 hover:underline dark:text-purple-500'
                    href='#'
                  >
                    Terms and Conditions
                  </a>
                </label>
              </div>
            </div>
            <button
              type='button'
              className='w-full py-3 px-4 inline-flex justify-center items-center gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-600 transition-all text-sm bg-gray-800 hover:bg-slate-800 dark:border-gray-700 text-gray-400 hover:text-white focus:ring-offset-gray-800'
            >
              <svg
                className='w-5 h-auto'
                width='46'
                height='47'
                viewBox='0 0 46 47'
                fill='none'
              >
                <path
                  d='M46 24.0287C46 22.09 45.8533 20.68 45.5013 19.2112H23.4694V27.9356H36.4069C36.1429 30.1094 34.7347 33.37 31.5957 35.5731L31.5663 35.8669L38.5191 41.2719L38.9885 41.3306C43.4477 37.2181 46 31.1669 46 24.0287Z'
                  fill='#4285F4'
                />
                <path
                  d='M23.4694 47C29.8061 47 35.1161 44.9144 39.0179 41.3012L31.625 35.5437C29.6301 36.9244 26.9898 37.8937 23.4987 37.8937C17.2793 37.8937 12.0281 33.7812 10.1505 28.1412L9.88649 28.1706L2.61097 33.7812L2.52296 34.0456C6.36608 41.7125 14.287 47 23.4694 47Z'
                  fill='#34A853'
                />
                <path
                  d='M10.1212 28.1413C9.62245 26.6725 9.32908 25.1156 9.32908 23.5C9.32908 21.8844 9.62245 20.3275 10.0918 18.8588V18.5356L2.75765 12.8369L2.52296 12.9544C0.909439 16.1269 0 19.7106 0 23.5C0 27.2894 0.909439 30.8731 2.49362 34.0456L10.1212 28.1413Z'
                  fill='#FBBC05'
                />
                <path
                  d='M23.4694 9.07688C27.8699 9.07688 30.8622 10.9863 32.5344 12.5725L39.1645 6.11C35.0867 2.32063 29.8061 0 23.4694 0C14.287 0 6.36607 5.2875 2.49362 12.9544L10.0918 18.8588C11.9987 13.1894 17.25 9.07688 23.4694 9.07688Z'
                  fill='#EB4335'
                />
              </svg>
              Sign up with Google
            </button>

            <button
              type='button'
              className='w-full py-3 px-4 inline-flex justify-center items-center gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-600 transition-all text-sm bg-gray-800 hover:bg-slate-800 dark:border-gray-700 text-gray-400 hover:text-white focus:ring-offset-gray-800'
            >
              <svg
                xmlns='http://www.w3.org/2000/svg'
                width='24'
                height='24'
                viewBox='0 0 24 24'
                fill='#555555'
                className='w-5 h-auto'
              >
                <path d='M16.46 5.79l.3.01a5.6 5.6 0 0 1 4.38 2.38c-.1.07-2.62 1.53-2.59 4.57.04 3.63 3.19 4.84 3.22 4.86-.02.08-.5 1.72-1.66 3.41-1 1.46-2.04 2.92-3.67 2.95-1.6.03-2.13-.96-3.96-.96-1.84 0-2.42.93-3.94.99-1.57.06-2.78-1.58-3.78-3.04-2.07-2.98-3.64-8.42-1.53-12.1a5.87 5.87 0 0 1 4.97-3c1.55-.03 3.01 1.04 3.96 1.04.95 0 2.73-1.29 4.6-1.1zM16.78 0a5.3 5.3 0 0 1-1.25 3.83 4.46 4.46 0 0 1-3.56 1.7 5.03 5.03 0 0 1 1.27-3.71A5.38 5.38 0 0 1 16.78 0z' />
              </svg>
              Sign up with Apple
            </button>

            <button
              type='button'
              className='w-full py-3 px-4 inline-flex justify-center items-center gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-600 transition-all text-sm bg-gray-800 hover:bg-slate-800 dark:border-gray-700 text-gray-400 hover:text-white focus:ring-offset-gray-800'
            >
              <svg
                xmlns='http://www.w3.org/2000/svg'
                width='24'
                height='24'
                viewBox='0 0 24 24'
                fill='#4267B2'
                className='w-5 h-auto'
              >
                <path d='M24 12.07C24 5.41 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.1 10.13 24v-8.44H7.08v-3.49h3.04V9.41c0-3.02 1.8-4.7 4.54-4.7 1.31 0 2.68.24 2.68.24v2.97h-1.5c-1.5 0-1.96.93-1.96 1.89v2.26h3.32l-.53 3.5h-2.8V24C19.62 23.1 24 18.1 24 12.07' />
              </svg>
              Sign up with Facebook
            </button>

            <button
              type='button'
              className='w-full py-3 px-4 inline-flex justify-center items-center gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-600 transition-all text-sm bg-gray-800 hover:bg-slate-800 dark:border-gray-700 text-gray-400 hover:text-white focus:ring-offset-gray-800'
            >
              <svg
                xmlns='http://www.w3.org/2000/svg'
                width='24'
                height='24'
                viewBox='0 0 24 24'
                fill='#1DA1F2'
                className='w-5 h-auto'
              >
                <path d='M24 4.37a9.6 9.6 0 0 1-2.83.8 5.04 5.04 0 0 0 2.17-2.8c-.95.58-2 1-3.13 1.22A4.86 4.86 0 0 0 16.61 2a4.99 4.99 0 0 0-4.79 6.2A13.87 13.87 0 0 1 1.67 2.92 5.12 5.12 0 0 0 3.2 9.67a4.82 4.82 0 0 1-2.23-.64v.07c0 2.44 1.7 4.48 3.95 4.95a4.84 4.84 0 0 1-2.22.08c.63 2.01 2.45 3.47 4.6 3.51A9.72 9.72 0 0 1 0 19.74 13.68 13.68 0 0 0 7.55 22c9.06 0 14-7.7 14-14.37v-.65c.96-.71 1.79-1.6 2.45-2.61z' />
              </svg>
              Sign up with Twitter
            </button>
            <p className='mt-2 text-center text-sm text-gray-600 dark:text-gray-400'>
              Already have an account?{' '}
              <Link
                className='text-purple-600 decoration-2 hover:underline font-medium'
                href='/login'
              >
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}

export default SignupModal
