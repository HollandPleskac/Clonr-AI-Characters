'use client'

import TopBarStatic from '@/components/TopBarStatic'
import React from 'react'
import Link from 'next/link'


function SubscriptionPortal() {
    const stripe_id = "stripe_id";
    const interval = "interval";
    const price = "14.99";
    const product_name = "Buckwheat";
    const email = 'test@example.com';
    const status = 'active';

    return (
        <div className="max-w-7xl mx-auto sm:px-6 lg:px-8 py-10 space-y-4">

  <h1 className="text-3xl font-bold text-white">Dashboard</h1>
  <div className="rounded-md bg-[#240b65] p-4">
    <div className="flex">
      <div className="flex-shrink-0">
        <svg className="h-5 w-5 text-[#6b40d7]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>
      </div>
      <div className="ml-3 flex-1 md:flex md:justify-between">
        <p className="text-sm text-blue-700">This dashboard is only for paying users like you.</p>
      </div>
    </div>
  </div>

  <div className="bg-white shadow overflow-hidden sm:rounded-lg">
    <div className="px-4 py-5 sm:px-6">
      <h3 className="text-lg leading-6 font-medium text-gray-900">Billing Information</h3>
      <p className="mt-1 max-w-2xl text-sm text-gray-500">Personal details and application.</p>
    </div>
    <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
      <dl className="sm:divide-y sm:divide-gray-200">
        <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt className="text-sm font-medium text-gray-500">Stripe Customer</dt>
                            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{stripe_id}</dd>
        </div>
        <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt className="text-sm font-medium text-gray-500">Stripe Subscription</dt>
          <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            {stripe_id}
                                <span className="inline-flex items-center ml-4 px-3 py-0.5 rounded-full text-sm font-medium bg-green-100 text-green-800"> {status}</span>
          </dd>
        </div>
        <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt className="text-sm font-medium text-gray-500">Plan</dt>
          <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            {product_name}
            {price}
            {interval}
          </dd>
        </div>
        <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt className="text-sm font-medium text-gray-500">Email address</dt>
          <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{email}</dd>
        </div>
        <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
          <dt className="text-sm font-medium text-gray-500">Manage</dt>
          <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
            <form action="http://localhost:8000/stripe/create-portal-session" method="post" data-turbo="false">
              <input type="hidden"/>
              <button className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium text-emerald-900 bg-emerald-400 hover:bg-gray-700">Manage</button>
            </form>
          </dd>
        </div>
      </dl>
    </div>
  </div>
</div>
    )
}

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
            {activeTab === 'deprecated' && (
              <div>
                <h2 className='text-lg sm:text-xl font-semibold mb-4 text-white'>
                  Current Plan: Startup
                </h2>
                <div className='inline-flex flex-col text-start shadow-xl rounded-xl'>
                  <span className='font-bold text-2xl text-gray-800 dark:text-gray-200'>
                    <span className='font-bold text-lg mr-1'>$</span>
                    39
                  </span>
                  <p className='mt-2 text-sm text-gray-500'>
                    All the basics for starting a new business
                  </p>

                  <ul className='mt-2 space-y-2.5 text-sm'>
                    <li className='flex space-x-2'>
                      <svg
                        className='flex-shrink-0 h-5 w-5 text-purple-600'
                        width='16'
                        height='16'
                        viewBox='0 0 16 16'
                        fill='none'
                        xmlns='http:www.w3.org/2000/svg'
                      >
                        <path
                          d='M11.5219 4.0949C11.7604 3.81436 12.181 3.78025 12.4617 4.01871C12.7422 4.25717 12.7763 4.6779 12.5378 4.95844L6.87116 11.6251C6.62896 11.91 6.1998 11.94 5.9203 11.6916L2.9203 9.02494C2.64511 8.78033 2.62032 8.35894 2.86493 8.08375C3.10955 7.80856 3.53092 7.78378 3.80611 8.02839L6.29667 10.2423L11.5219 4.0949Z'
                          fill='currentColor'
                        />
                      </svg>
                      <span className='text-gray-800 dark:text-gray-400'>
                        2 users
                      </span>
                    </li>

                    <li className='flex space-x-2'>
                      <svg
                        className='flex-shrink-0 h-5 w-5 text-purple-600'
                        width='16'
                        height='16'
                        viewBox='0 0 16 16'
                        fill='none'
                        xmlns='http:www.w3.org/2000/svg'
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
                        className='flex-shrink-0 h-5 w-5 text-purple-600'
                        width='16'
                        height='16'
                        viewBox='0 0 16 16'
                        fill='none'
                        xmlns='http:www.w3.org/2000/svg'
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
                </div>
                <Link
                  className='block text-lg sm:text-xl font-semibold mb-4 text-purple-600  mt-6 hover:underline '
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
                    className='flex flex-col justify-center overflow-hidden bg-purple-500 text-xs text-white text-center'
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

            {activeTab === 'settings' && (
              <div>
                <h2 className='text-lg sm:text-xl font-semibold mb-4 text-white'>
                  Change private chat name
                </h2>
                <label htmlFor='hs-trailing-button-add-on' className='sr-only'>
                  Label
                </label>
                <div className='inline-flex rounded-md shadow-sm mb-6'>
                  <input
                    type='text'
                    id='hs-trailing-button-add-on'
                    name='hs-trailing-button-add-on'
                    className='py-3 px-4 block w-full shadow-sm rounded-l-md text-sm focus:z-10 focus:border-purple-500 focus:ring-purple-500 bg-slate-900 border-gray-700 text-gray-400'
                  />
                  <button
                    type='button'
                    className='py-3 px-4 inline-flex flex-shrink-0 justify-center items-center gap-2 rounded-r-md border border-transparent font-semibold bg-purple-500 text-white hover:bg-purple-600 focus:z-10 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all text-sm'
                  >
                    Update
                  </button>
                </div>
                <button
                  type='button'
                  className='block py-3 px-4 justify-center items-center gap-2 rounded-md border border-transparent font-semibold bg-red-500 text-white hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all text-sm dark:focus:ring-offset-gray-800'
                >
                  Deactivate Account
                </button>
              </div>
            )}

            {activeTab === 'billing' && (
              <SubscriptionPortal/>
            )}
          </div>
        </div>
      </main>
    </>
  )
}