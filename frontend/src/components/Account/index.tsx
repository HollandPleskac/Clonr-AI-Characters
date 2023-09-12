'use client'

import TopBarStatic from '@/components/TopBarStatic'
import React, { useEffect } from 'react'
import Link from 'next/link'
import axios from 'axios';
import { useRouter } from 'next/navigation'
import useSWR from "swr"
import { Subscription, SubscriptionsService } from '@/client';
import router from 'next/router';
import { Session } from 'next-auth';
import { useUser } from '@/hooks/useUser';
import { useClosePrelineModal } from '@/hooks/useClosePrelineModal';


function SubscriptionPortal() {
  const { push } = useRouter()
  const { userObject, isUserLoading } = useUser()

  const { data: subscription, isLoading, error } = useSWR<Subscription>(
    'http://localhost:8000/subscriptions/me',
    async () => await SubscriptionsService.getMySubscriptionsSubscriptionsMeGet()
  );

  useEffect(() => {
    require('preline')
  }, [])

  useClosePrelineModal()



  if (isLoading || isUserLoading) {
    return <p></p>
  }

  if (!subscription) {
    return (
      <div className="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-2">

        <h1 className="text-3xl font-bold text-gray-200">Current Plan</h1>

        <div className="bg-[#1c1c1c] border-gray-400 shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-200">Billing Information</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-400">Personal details and application.</p>
          </div>
          <div className="px-4 border-t-gray-800 border-t-[1px] py-5 sm:p-0">
            <dl className="sm:divide-y sm:divide-[#2c2c2c]">

              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-400">Plan</dt>
                <dd className="mt-1 text-sm text-purple-400 sm:mt-0 sm:col-span-2 font-semibold">
                  Free Tier
                </dd>
              </div>
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-400">
                  Free messages
                </dt>
                <dd className="mt-1 text-sm text-purple-400 sm:mt-0 sm:col-span-2">
                  {10 - (userObject?.num_free_messages_sent ?? 0)}/10
                </dd>
              </div>
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-400">Email address</dt>
                <dd className="mt-1 text-sm text-purple-400 sm:mt-0 sm:col-span-2">
                  {userObject?.email ?? ""}
                </dd>
              </div>
              <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 items-center">
                <dt className="text-sm font-medium  text-gray-400">Change Plan</dt>
                <dd className="mt-1 text-sm text-purple-400 sm:mt-0 sm:col-span-2">
                  <button onClick={() => {
                    push('/pricing')
                  }}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium text-gray-300 rounded-xl bg-[#5424cd] hover:bg-[#5f38c2]"
                  >Manage</button>
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto sm:px-6 lg:px-8 space-y-2">

      <h1 className="text-3xl font-bold text-gray-200">Current Plan</h1>
      <div className="rounded-md bg-[#5424cd] p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-[#966cff]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3 flex-1 md:flex md:justify-between">
            <p className="text-sm text-blue-100">This dashboard is only for paying users like you.</p>
          </div>
        </div>
      </div>

      <div className="bg-[#1c1c1c] border-gray-400 shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-200">Billing Information</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-400">Personal details and application.</p>
        </div>
        <div className="px-4 border-t-gray-800 border-t-[1px] py-5 sm:p-0">
          <dl className="sm:divide-y sm:divide-[#2c2c2c]">
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-400">
                Stripe Customer
              </dt>
              <dd className="mt-1 text-sm text-purple-400 sm:mt-0 sm:col-span-2">
                {subscription.stripe_customer_id}
              </dd>
            </div>
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 ">
              <dt className="text-sm font-medium text-gray-400 ">
                Stripe Subscription
              </dt>
              <dd className="mt-1 text-sm text-purple-400 sm:mt-0 sm:col-span-2">
                {subscription.stripe_subscription_id}
                {subscription.stripe_status === 'active' ?
                  <span className="inline-flex items-center ml-4 px-2 py-0.5 rounded-md text-sm font-medium bg-[#D7F7C2] text-[#016808]"> {subscription.stripe_status}</span> :
                  <span className="inline-flex items-center ml-4 px-2 rounded-md text-sm font-medium bg-[#f7c2c2] text-[#680101]"> {subscription.stripe_status}</span>
                }
              </dd>
            </div>
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-400">Plan</dt>
              <dd className="mt-1 text-sm text-purple-400 sm:mt-0 sm:col-span-2 font-semibold">
                {subscription.stripe_product_name}
              </dd>
            </div>
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-400">
                Price
              </dt>
              <dd className="mt-1 text-sm text-purple-400 sm:mt-0 sm:col-span-2">
                ${subscription.amount / 100} {subscription.currency.toUpperCase()} / {subscription.interval}
              </dd>
            </div>
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-400">Email address</dt>
              <dd className="mt-1 text-sm text-purple-400 sm:mt-0 sm:col-span-2">
                {subscription.stripe_email}
              </dd>
            </div>
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 items-center">
              <dt className="text-sm font-medium  text-gray-400">Change Plan</dt>
              <dd className="mt-1 text-sm text-purple-400 sm:mt-0 sm:col-span-2">
                <button onClick={async () => {
                  try {
                    const res = await axios.get('http://localhost:8000/stripe/create-portal-session', {
                      withCredentials: true
                    })
                    console.log("response", res)
                    push(res.data)
                  } catch (e) {
                    console.log("Error", e)
                  }
                }}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium text-gray-300 rounded-xl bg-[#5424cd] hover:bg-[#5f38c2]"
                >Manage</button>
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  )
}



export default function AccountComponent() {
  const { push } = useRouter()
  const [activeTab, setActiveTab] = React.useState('billing')

  useClosePrelineModal()

  return (
    <>
      <main className='w-full flex flex-col h-full'>
        <TopBarStatic />
        <div className='flex flex-col sm:flex-row overflow-auto'
          style={{ height: "100vh - 76px" }}
        >
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
                    className={` ${activeTab === 'billing'
                      ? 'bg-gray-900 text-gray-400'
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
                        fillRule='evenodd'
                        d='M2 13.5V7h1v6.5a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V7h1v6.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 13.5zm11-11V6l-2-2V2.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5z'
                      />
                      <path
                        fillRule='evenodd'
                        d='M7.293 1.5a1 1 0 0 1 1.414 0l6.647 6.646a.5.5 0 0 1-.708.708L8 2.207 1.354 8.854a.5.5 0 1 1-.708-.708L7.293 1.5z'
                      />
                    </svg>
                    Billing
                  </button>
                </li>

                <li className='flex-grow'>
                  <button
                    className={` ${activeTab === 'usage'
                      ? 'bg-gray-900 text-gray-400'
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
                    className={` ${activeTab === 'settings'
                      ? 'bg-gray-900 text-gray-400'
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
            className='hidden sm:block hs-overlay z-[0] w-64 border-r pt-7 pb-10 overflow-y-auto scrollbar-y  scrollbar-y bg-black border-[#1d1e1e]'
            style={{ height: 'calc(100vh - 76px)' }}
          >
            <div className='px-6'>
              <a
                className='flex-none text-xl font-semibold dark:text-gray-400'
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
                    className={` ${activeTab === 'billing'
                      ? 'bg-gray-900 text-gray-400'
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
                        fillRule='evenodd'
                        d='M2 13.5V7h1v6.5a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V7h1v6.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 13.5zm11-11V6l-2-2V2.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5z'
                      />
                      <path
                        fillRule='evenodd'
                        d='M7.293 1.5a1 1 0 0 1 1.414 0l6.647 6.646a.5.5 0 0 1-.708.708L8 2.207 1.354 8.854a.5.5 0 1 1-.708-.708L7.293 1.5z'
                      />
                    </svg>
                    Billing
                  </button>
                </li>

                <li>
                  <button
                    className={` ${activeTab === 'usage'
                      ? 'bg-gray-900 text-gray-400'
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
                    className={` ${activeTab === 'settings'
                      ? 'bg-gray-900 text-gray-400'
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
                <h2 className='text-lg sm:text-xl font-semibold mb-4 text-gray-400'>
                  Current Plan: Startup
                </h2>
                <div className='inline-flex flex-col text-start shadow-xl rounded-xl'>
                  <span className='font-bold text-2xl text-gray-800 dark:text-gray-200'>
                    <span className='font-bold text-lg mr-1'>$</span>
                    39
                  </span>
                  <p className='mt-2 text-sm text-gray-400'>
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
              <div className='grid place-items-center h-full' >
                <h2 className='text-lg sm:text-xl font-semibold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-[#a974f3] to-[#ed74f3]'>
                  Not enough data yet
                </h2>
                {/* <h2 className='text-lg sm:text-xl font-semibold mb-4 text-gray-400'>
                  Message Limit for this month
                </h2>
                <div className='flex w-[50%] h-4 bg-gray-200 rounded-full overflow-hidden dark:bg-gray-700'>
                  <div
                    className='flex flex-col justify-center overflow-hidden bg-purple-500 text-xs text-gray-400 text-center'
                    role='progressbar'
                    style={{ width: '57%' }}
                    aria-valuenow='57'
                    aria-valuemin='0'
                    aria-valuemax='100'
                  >
                    57%
                  </div>
                </div> */}
              </div>
            )}

            {activeTab === 'settings' && (
              <div>
                <h2 className='text-lg sm:text-xl font-semibold mb-4 text-gray-400'>
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
                    className='py-3 px-4 inline-flex flex-shrink-0 justify-center items-center gap-2 rounded-r-md border border-transparent font-semibold bg-purple-500 text-gray-400 hover:bg-purple-600 focus:z-10 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all text-sm'
                  >
                    Update
                  </button>
                </div>
                <button
                  type='button'
                  className='block py-3 px-4 justify-center items-center gap-2 rounded-md border border-transparent font-semibold bg-red-500 text-gray-400 hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all text-sm dark:focus:ring-offset-gray-800'
                >
                  Deactivate Account
                </button>
              </div>
            )}

            {activeTab === 'billing' && (
              <SubscriptionPortal />
            )}
          </div>
        </div>
      </main>
    </>
  )
}
