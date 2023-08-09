'use client'

import Footer from '@/components/Footer'
import TopBarStatic from '@/components/TopBarStatic'
import React from 'react'
import Link from 'next/link'

export default function Login() {
  const [activeTab, setActiveTab] = React.useState('billing')
  return (
    <>
      <main className='w-full flex flex-col h-full'>
        <TopBarStatic />
        <div className='flex flex-col sm:flex-row'>
          {/* MOBILE NAV */}
          <div
            id='docs-sidebar'
            className='sm:hidden flex items-center justify-center hs-overlay z-[60] w-full border-b bg-black border-[#1d1e1e]'
            style={{ height: 'calc(72px)' }}
          >
            <nav
              className='hs-accordion-group p-6 w-full flex '
              data-hs-accordion-always-open
            >
              <ul className='flex space-x-1.5 w-full'>
                <li className='flex-grow'>
                  <button
                    className={` ${
                      activeTab === 'billing'
                        ? 'bg-gray-900 text-white'
                        : 'hover:bg-gray-900 text-slate-400 hover:text-slate-300'
                    } flex items-center gap-x-3.5 py-2 px-2.5 text-sm rounded-md w-full`}
                    onClick={() => setActiveTab('billing')}
                  >
                    <svg
                      className='w-3.5 h-3.5'
                      xmlns='http://www.w3.org/2000/svg'
                      width='16'
                      height='16'
                      fill='currentColor'
                      viewBox='0 0 16 16'
                    >
                      <path
                        fill-rule='evenodd'
                        d='M2 13.5V7h1v6.5a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V7h1v6.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 13.5zm11-11V6l-2-2V2.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5z'
                      />
                      <path
                        fill-rule='evenodd'
                        d='M7.293 1.5a1 1 0 0 1 1.414 0l6.647 6.646a.5.5 0 0 1-.708.708L8 2.207 1.354 8.854a.5.5 0 1 1-.708-.708L7.293 1.5z'
                      />
                    </svg>
                    Billing
                  </button>
                </li>

                <li className='flex-grow'>
                  <button
                    className={` ${
                      activeTab === 'usage'
                        ? 'bg-gray-900 text-white'
                        : 'hover:bg-gray-900 text-slate-400 hover:text-slate-300'
                    } flex items-center gap-x-3.5 py-2 px-2.5 text-sm rounded-md w-full`}
                    onClick={() => setActiveTab('usage')}
                  >
                    <svg
                      className='w-3.5 h-3.5'
                      xmlns='http://www.w3.org/2000/svg'
                      width='16'
                      height='16'
                      fill='currentColor'
                      viewBox='0 0 16 16'
                    >
                      <path d='M11 6.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1zm-3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1zm-5 3a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1zm3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1z' />
                      <path d='M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z' />
                    </svg>
                    Usage
                  </button>
                </li>
                <li className='flex-grow'>
                  <button
                    className={` ${
                      activeTab === 'settings'
                        ? 'bg-gray-900 text-white'
                        : 'hover:bg-gray-900 text-slate-400 hover:text-slate-300'
                    } flex items-center gap-x-3.5 py-2 px-2.5 text-sm rounded-md w-full`}
                    onClick={() => setActiveTab('settings')}
                  >
                    <svg
                      className='w-3.5 h-3.5'
                      xmlns='http://www.w3.org/2000/svg'
                      width='16'
                      height='16'
                      fill='currentColor'
                      viewBox='0 0 16 16'
                    >
                      <path d='M1 2.828c.885-.37 2.154-.769 3.388-.893 1.33-.134 2.458.063 3.112.752v9.746c-.935-.53-2.12-.603-3.213-.493-1.18.12-2.37.461-3.287.811V2.828zm7.5-.141c.654-.689 1.782-.886 3.112-.752 1.234.124 2.503.523 3.388.893v9.923c-.918-.35-2.107-.692-3.287-.81-1.094-.111-2.278-.039-3.213.492V2.687zM8 1.783C7.015.936 5.587.81 4.287.94c-1.514.153-3.042.672-3.994 1.105A.5.5 0 0 0 0 2.5v11a.5.5 0 0 0 .707.455c.882-.4 2.303-.881 3.68-1.02 1.409-.142 2.59.087 3.223.877a.5.5 0 0 0 .78 0c.633-.79 1.814-1.019 3.222-.877 1.378.139 2.8.62 3.681 1.02A.5.5 0 0 0 16 13.5v-11a.5.5 0 0 0-.293-.455c-.952-.433-2.48-.952-3.994-1.105C10.413.809 8.985.936 8 1.783z' />
                    </svg>
                    Settings
                  </button>
                </li>
              </ul>
            </nav>
          </div>

          {/* SIDE NAV */}

          <div
            id='docs-sidebar'
            className='hidden sm:block  hs-overlay z-[60] w-64 border-r pt-7 pb-10 overflow-y-auto scrollbar-y  scrollbar-y bg-black border-[#1d1e1e]'
            style={{ height: 'calc(100vh - 72px)' }}
          >
            <div className='px-6'>
              <a
                className='flex-none text-xl font-semibold dark:text-white'
                href='javascript:;'
                aria-label='Brand'
              >
                My Account
              </a>
            </div>
            <nav
              className='hs-accordion-group p-6 w-full flex flex-col flex-wrap'
              data-hs-accordion-always-open
            >
              <ul className='space-y-1.5'>
                <li>
                  <button
                    className={` ${
                      activeTab === 'billing'
                        ? 'bg-gray-900 text-white'
                        : 'hover:bg-gray-900 text-slate-400 hover:text-slate-300'
                    } flex items-center gap-x-3.5 py-2 px-2.5 text-sm rounded-md w-full`}
                    onClick={() => setActiveTab('billing')}
                  >
                    <svg
                      className='w-3.5 h-3.5'
                      xmlns='http://www.w3.org/2000/svg'
                      width='16'
                      height='16'
                      fill='currentColor'
                      viewBox='0 0 16 16'
                    >
                      <path
                        fill-rule='evenodd'
                        d='M2 13.5V7h1v6.5a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V7h1v6.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 13.5zm11-11V6l-2-2V2.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5z'
                      />
                      <path
                        fill-rule='evenodd'
                        d='M7.293 1.5a1 1 0 0 1 1.414 0l6.647 6.646a.5.5 0 0 1-.708.708L8 2.207 1.354 8.854a.5.5 0 1 1-.708-.708L7.293 1.5z'
                      />
                    </svg>
                    Billing
                  </button>
                </li>

                <li>
                  <button
                    className={` ${
                      activeTab === 'usage'
                        ? 'bg-gray-900 text-white'
                        : 'hover:bg-gray-900 text-slate-400 hover:text-slate-300'
                    } flex items-center gap-x-3.5 py-2 px-2.5 text-sm rounded-md w-full`}
                    onClick={() => setActiveTab('usage')}
                  >
                    <svg
                      className='w-3.5 h-3.5'
                      xmlns='http://www.w3.org/2000/svg'
                      width='16'
                      height='16'
                      fill='currentColor'
                      viewBox='0 0 16 16'
                    >
                      <path d='M11 6.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1zm-3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1zm-5 3a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1zm3 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1z' />
                      <path d='M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z' />
                    </svg>
                    Usage
                  </button>
                </li>
                <li>
                  <button
                    className={` ${
                      activeTab === 'settings'
                        ? 'bg-gray-900 text-white'
                        : 'hover:bg-gray-900 text-slate-400 hover:text-slate-300'
                    } flex items-center gap-x-3.5 py-2 px-2.5 text-sm rounded-md w-full`}
                    onClick={() => setActiveTab('settings')}
                  >
                    <svg
                      className='w-3.5 h-3.5'
                      xmlns='http://www.w3.org/2000/svg'
                      width='16'
                      height='16'
                      fill='currentColor'
                      viewBox='0 0 16 16'
                    >
                      <path d='M1 2.828c.885-.37 2.154-.769 3.388-.893 1.33-.134 2.458.063 3.112.752v9.746c-.935-.53-2.12-.603-3.213-.493-1.18.12-2.37.461-3.287.811V2.828zm7.5-.141c.654-.689 1.782-.886 3.112-.752 1.234.124 2.503.523 3.388.893v9.923c-.918-.35-2.107-.692-3.287-.81-1.094-.111-2.278-.039-3.213.492V2.687zM8 1.783C7.015.936 5.587.81 4.287.94c-1.514.153-3.042.672-3.994 1.105A.5.5 0 0 0 0 2.5v11a.5.5 0 0 0 .707.455c.882-.4 2.303-.881 3.68-1.02 1.409-.142 2.59.087 3.223.877a.5.5 0 0 0 .78 0c.633-.79 1.814-1.019 3.222-.877 1.378.139 2.8.62 3.681 1.02A.5.5 0 0 0 16 13.5v-11a.5.5 0 0 0-.293-.455c-.952-.433-2.48-.952-3.994-1.105C10.413.809 8.985.936 8 1.783z' />
                    </svg>
                    Settings
                  </button>
                </li>
              </ul>
            </nav>
          </div>
          <div className='text-red-400 w-full p-8'>
            {activeTab === 'billing' && (
              <div>
                <h2 className='text-lg sm:text-xl font-semibold mb-4 text-white'>
                  Current Plan
                </h2>
                <div className='bg-purple-500 rounded-lg px-4 py-2 inline-flex items-center justify-center text-white'>
                  Clonr Pro
                </div>
                <Link
                  className='text-lg sm:text-xl font-semibold mb-4 text-purple-600  mt-6 hover:underline '
                  href='/pricing'
                >
                  Switch Plans Here
                </Link>
              </div>
            )}

            {activeTab === 'usage' && (
              <div>
                <h2 className='text-lg sm:text-xl font-semibold mb-4 text-white'>
                  Message Limit for this month
                </h2>
                <div className='flex w-[50%] h-4 bg-gray-200 rounded-full overflow-hidden dark:bg-gray-700'>
                  <div
                    className='flex flex-col justify-center overflow-hidden bg-blue-500 text-xs text-white text-center'
                    role='progressbar'
                    style={{ width: '57%' }}
                    aria-valuenow='57'
                    aria-valuemin='0'
                    aria-valuemax='100'
                  >
                    57%
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  )
}
