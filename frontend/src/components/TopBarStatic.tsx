'use client'

import React, { useEffect, useRef, useState } from 'react'

import Link from 'next/link'
import Image from 'next/image'

import SearchIcon from './SearchIcon'
import XIcon from './XIcon'
import { usePathname } from 'next/navigation'
import AccountDropdown from './AccountDropdown'
import { useUser } from '@/hooks/useUser'
import { signOut, useSession } from 'next-auth/react'

function SocialMedia() {
  return (
    <div className='space-x-2 translate-y-1'>
      <a
        className='inline-flex justify-center items-center w-8 h-8 text-center text-gray-500 hover:bg-gray-100 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2 focus:ring-offset-white transition dark:text-[#515151] dark:hover:text-gray-200 dark:hover:bg-gray-700 dark:focus:ring-offset-slate-900'
        href='#'
      >
        <svg
          width='16'
          height='16'
          viewBox='0 0 16 16'
          fill='#5661F7'
          xmlns='http://www.w3.org/2000/svg'
        >
          <path d='M12.8467 3.55332C11.96 3.13999 11 2.83999 10 2.66666C9.99123 2.66638 9.98251 2.66802 9.97444 2.67148C9.96638 2.67493 9.95917 2.68011 9.95333 2.68666C9.83333 2.90666 9.69333 3.19332 9.6 3.41332C8.53933 3.25332 7.46066 3.25332 6.4 3.41332C6.30666 3.18666 6.16666 2.90666 6.04 2.68666C6.03333 2.67332 6.01333 2.66666 5.99333 2.66666C4.99333 2.83999 4.04 3.13999 3.14666 3.55332C3.14 3.55332 3.13333 3.55999 3.12666 3.56666C1.31333 6.27999 0.81333 8.91999 1.06 11.5333C1.06 11.5467 1.06666 11.56 1.08 11.5667C2.28 12.4467 3.43333 12.98 4.57333 13.3333C4.59333 13.34 4.61333 13.3333 4.62 13.32C4.88666 12.9533 5.12666 12.5667 5.33333 12.16C5.34666 12.1333 5.33333 12.1067 5.30666 12.1C4.92666 11.9533 4.56666 11.78 4.21333 11.58C4.18666 11.5667 4.18666 11.5267 4.20666 11.5067C4.28 11.4533 4.35333 11.3933 4.42666 11.34C4.44 11.3267 4.46 11.3267 4.47333 11.3333C6.76666 12.38 9.24 12.38 11.5067 11.3333C11.52 11.3267 11.54 11.3267 11.5533 11.34C11.6267 11.4 11.7 11.4533 11.7733 11.5133C11.8 11.5333 11.8 11.5733 11.7667 11.5867C11.42 11.7933 11.0533 11.96 10.6733 12.1067C10.6467 12.1133 10.64 12.1467 10.6467 12.1667C10.86 12.5733 11.1 12.96 11.36 13.3267C11.38 13.3333 11.4 13.34 11.42 13.3333C12.5667 12.98 13.72 12.4467 14.92 11.5667C14.9333 11.56 14.94 11.5467 14.94 11.5333C15.2333 8.51332 14.4533 5.89332 12.8733 3.56666C12.8667 3.55999 12.86 3.55332 12.8467 3.55332ZM5.68 9.93999C4.99333 9.93999 4.42 9.30666 4.42 8.52666C4.42 7.74666 4.98 7.11332 5.68 7.11332C6.38666 7.11332 6.94666 7.75332 6.94 8.52666C6.94 9.30666 6.38 9.93999 5.68 9.93999ZM10.3267 9.93999C9.64 9.93999 9.06666 9.30666 9.06666 8.52666C9.06666 7.74666 9.62666 7.11332 10.3267 7.11332C11.0333 7.11332 11.5933 7.75332 11.5867 8.52666C11.5867 9.30666 11.0333 9.93999 10.3267 9.93999Z' />
        </svg>
      </a>

      <a
        className='inline-flex justify-center items-center w-8 h-8 text-center text-gray-500 hover:bg-gray-100 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2 focus:ring-offset-white transition dark:text-[#515151] dark:hover:text-gray-200 dark:hover:bg-gray-700 dark:focus:ring-offset-slate-900'
        href='#'
      >
        <svg
          width='16'
          height='16'
          viewBox='0 0 16 16'
          fill='#FF4500'
          xmlns='http://www.w3.org/2000/svg'
        >
          <path
            fillRule='evenodd'
            clipRule='evenodd'
            d='M13.3067 1.16666C12.7247 1.16666 12.216 1.48599 11.948 1.95866L9.548 1.46599C9.4349 1.44282 9.31726 1.45951 9.21506 1.51322C9.11286 1.56694 9.0324 1.65436 8.98734 1.76066C8.71334 2.40466 8.30267 3.38132 7.95934 4.21732C7.80867 4.58532 7.67 4.92799 7.562 5.20399C6.28334 5.26532 5.10067 5.59732 4.124 6.12666C3.94046 5.87685 3.70251 5.67206 3.42815 5.52778C3.15379 5.3835 2.8502 5.30352 2.54037 5.29388C2.23053 5.28424 1.92256 5.34519 1.63976 5.47214C1.35696 5.59908 1.10673 5.78868 0.90802 6.0266C0.709306 6.26451 0.567308 6.54451 0.492771 6.8454C0.418233 7.14629 0.413109 7.46019 0.477785 7.76335C0.542461 8.06652 0.675244 8.351 0.866085 8.59527C1.05693 8.83955 1.30083 9.03722 1.57934 9.17332C1.52068 9.43301 1.49116 9.69843 1.49134 9.96466C1.49134 11.3247 2.25867 12.526 3.43867 13.374C4.61867 14.2227 6.23267 14.7367 8 14.7367C9.76667 14.7367 11.3807 14.2227 12.5613 13.374C13.7413 12.526 14.5087 11.3253 14.5087 9.96466C14.5087 9.69466 14.4787 9.42999 14.4207 9.17399C14.6987 9.03766 14.9421 8.83992 15.1325 8.59572C15.3229 8.35151 15.4553 8.06723 15.5197 7.76435C15.5841 7.46146 15.5788 7.1479 15.5043 6.84736C15.4297 6.54681 15.2878 6.26715 15.0893 6.02948C14.8908 5.79182 14.6409 5.60238 14.3584 5.47548C14.076 5.34858 13.7684 5.28754 13.4589 5.29696C13.1494 5.30639 12.846 5.38603 12.5718 5.52988C12.2976 5.67373 12.0597 5.87803 11.876 6.12732C10.9493 5.62399 9.83667 5.29999 8.63334 5.21532L8.88467 4.59666C9.164 3.91599 9.48934 3.13999 9.748 2.52799L11.76 2.94132C11.8008 3.23842 11.9263 3.51748 12.1215 3.74518C12.3166 3.97287 12.5732 4.13958 12.8606 4.22537C13.1479 4.31117 13.4539 4.31243 13.742 4.229C14.03 4.14558 14.288 3.981 14.485 3.75492C14.682 3.52884 14.8098 3.25082 14.8531 2.95407C14.8964 2.65732 14.8533 2.35439 14.7291 2.08145C14.6048 1.80852 14.4046 1.57712 14.1524 1.4149C13.9002 1.25269 13.6066 1.16651 13.3067 1.16666ZM12.7453 2.72799C12.7453 2.57903 12.8045 2.43616 12.9098 2.33083C13.0152 2.2255 13.158 2.16632 13.307 2.16632C13.456 2.16632 13.5988 2.2255 13.7042 2.33083C13.8095 2.43616 13.8687 2.57903 13.8687 2.72799C13.8687 2.87695 13.8095 3.01982 13.7042 3.12515C13.5988 3.23048 13.456 3.28966 13.307 3.28966C13.158 3.28966 13.0152 3.23048 12.9098 3.12515C12.8045 3.01982 12.7453 2.87695 12.7453 2.72799ZM14.0673 8.22799C13.754 7.63932 13.29 7.11266 12.718 6.67199C12.8147 6.55517 12.9356 6.4608 13.0724 6.39545C13.2093 6.3301 13.3587 6.29534 13.5103 6.29358C13.6619 6.29182 13.8121 6.32311 13.9504 6.38527C14.0887 6.44743 14.2118 6.53897 14.3111 6.65353C14.4105 6.76808 14.4837 6.9029 14.5256 7.04861C14.5676 7.19431 14.5773 7.34741 14.5541 7.49725C14.5309 7.64709 14.4753 7.79008 14.3913 7.91628C14.3072 8.04247 14.1967 8.14884 14.0673 8.22799ZM3.282 6.67199C3.18539 6.55498 3.06444 6.46044 2.92756 6.39494C2.79069 6.32945 2.64118 6.29458 2.48945 6.29276C2.33772 6.29094 2.18742 6.32222 2.04901 6.38442C1.91061 6.44662 1.78742 6.53824 1.68804 6.6529C1.58866 6.76756 1.51546 6.90251 1.47355 7.04835C1.43165 7.19418 1.42203 7.3474 1.44538 7.49734C1.46873 7.64727 1.52448 7.79031 1.60875 7.91649C1.69302 8.04268 1.80379 8.14898 1.93334 8.22799C2.24667 7.63932 2.71 7.11266 3.282 6.67199ZM10.358 9.96532C10.6139 9.96532 10.8594 9.86365 11.0404 9.68268C11.2213 9.50171 11.323 9.25626 11.323 9.00032C11.323 8.74439 11.2213 8.49894 11.0404 8.31797C10.8594 8.13699 10.6139 8.03532 10.358 8.03532C10.1022 8.03532 9.85679 8.13696 9.67588 8.31787C9.49497 8.49878 9.39334 8.74414 9.39334 8.99999C9.39334 9.25584 9.49497 9.5012 9.67588 9.68211C9.85679 9.86302 10.1022 9.96466 10.358 9.96466V9.96532ZM6.60334 8.99999C6.60334 9.25592 6.50167 9.50138 6.32069 9.68235C6.13972 9.86332 5.89427 9.96499 5.63834 9.96499C5.3824 9.96499 5.13695 9.86332 4.95598 9.68235C4.77501 9.50138 4.67334 9.25592 4.67334 8.99999C4.67334 8.74406 4.77501 8.4986 4.95598 8.31763C5.13695 8.13666 5.3824 8.03499 5.63834 8.03499C5.89427 8.03499 6.13972 8.13666 6.32069 8.31763C6.50167 8.4986 6.60334 8.74406 6.60334 8.99999ZM5.9 11.086C5.78802 11.0201 5.6548 11.0004 5.52855 11.0311C5.4023 11.0617 5.29294 11.1403 5.22362 11.2502C5.15429 11.36 5.13046 11.4926 5.15716 11.6197C5.18386 11.7469 5.259 11.8586 5.36667 11.9313L5.59667 12.0767C6.31534 12.5299 7.14766 12.7705 7.99734 12.7705C8.84702 12.7705 9.67933 12.5299 10.398 12.0767L10.628 11.932C10.6836 11.897 10.7317 11.8513 10.7697 11.7977C10.8077 11.7441 10.8347 11.6835 10.8492 11.6194C10.8638 11.5554 10.8656 11.4891 10.8545 11.4243C10.8434 11.3595 10.8197 11.2976 10.7847 11.242C10.7497 11.1864 10.704 11.1382 10.6504 11.1003C10.5968 11.0623 10.5362 11.0353 10.4721 11.0208C10.408 11.0062 10.3417 11.0044 10.277 11.0155C10.2122 11.0266 10.1503 11.0503 10.0947 11.0853L9.86467 11.2307C9.30567 11.5833 8.65826 11.7704 7.99734 11.7704C7.33641 11.7704 6.689 11.5833 6.13 11.2307L5.9 11.086Z'
          />
        </svg>
      </a>

      <a
        className='inline-flex justify-center items-center w-8 h-8 text-center text-gray-500 hover:bg-gray-100 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2 focus:ring-offset-white transition dark:text-[#515151] dark:hover:text-gray-200 dark:hover:bg-gray-700 dark:focus:ring-offset-slate-900'
        href='#'
      >
        <svg
          width='16'
          height='16'
          viewBox='0 0 1227 1200'
          fill='white'
          className='align-center'
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M714.163 519.284L1160.89 0H1055.03L667.137 450.887L357.328 0H0L468.492 681.821L0 1226.37H105.866L515.491 750.218L842.672 1226.37H1200L714.137 519.284H714.163ZM569.165 687.828L521.697 619.934L144.011 79.6944H306.615L611.412 515.685L658.88 583.579L1055.08 1150.3H892.476L569.165 687.854V687.828Z" fill="white" />
        </svg>
      </a>
    </div>
  )
}

export default function TopBarStatic() {
  const { data: session, status } = useSession()

  const pathname = usePathname()

  return (
    <>
      <div className='h-[76px]' >
      <header className={`sticky top-0 flex flex-wrap lg:justify-start lg:flex-nowrap w-full bg-black text-sm py-[19.2px] border-b border-[#141414] px-[4%] z-[50] shadow-md shadow-[rgb(255,255,255,0.02)]`}>
        <nav
          className='w-full mx-auto lg:flex lg:items-center lg:justify-between'
          aria-label='Global'
        >
          <div className='flex items-center justify-between'>
            <Link href='/' className='flex items-center cursor-pointer'>
              <div className='h-8 w-8 relative'>
                <Image
                  src='/clonr-logo.png'
                  alt='logo'
                  layout='fill'
                  objectFit='cover'
                  className=''
                />
              </div>
              <h3 className='ml-2 text-[30px] font-semibold leading-5 text-white font-fabada'>
                clonr
              </h3>
              <p className='text-white font-thin ml-2 align-middle'>users</p>
            </Link>
            <div className='flex lg:hidden gap-x-4'>
              <button
                type='button'
                className='w-[35px] h-[35px] hs-collapse-toggle p-2 inline-flex justify-center items-center gap-2 rounded-md border font-medium bg-white text-gray-700 shadow-sm align-middle hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white focus:ring-purple-600 transition-all text-sm dark:bg-slate-900 dark:hover:bg-slate-800 dark:border-gray-700 dark:text-gray-400 dark:hover:text-white dark:focus:ring-offset-gray-800'
                data-hs-collapse='#navbar-collapse-with-animation'
                aria-controls='navbar-collapse-with-animation'
                aria-label='Toggle navigation'
              >
                <svg
                  className='hs-collapse-open:hidden w-4 h-4'
                  width='16'
                  height='16'
                  fill='currentColor'
                  viewBox='0 0 16 16'
                >
                  <path
                    fillRule='evenodd'
                    d='M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z'
                  />
                </svg>
                <svg
                  className='hs-collapse-open:block hidden w-4 h-4'
                  width='16'
                  height='16'
                  fill='currentColor'
                  viewBox='0 0 16 16'
                >
                  <path d='M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z' />
                </svg>
              </button>
            </div>
          </div>
          <div
            id='navbar-collapse-with-animation'
            className='pb-1 hs-collapse hidden overflow-hidden transition-all duration-300 basis-full grow lg:block'
          >
            <div className='flex mt-5 lg:items-center lg:justify-between lg:mt-0 lg:pl-5 '>
              <div className='flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-start '>
                <Link
                  href='/browse?sort=Trending'
                  className={`transition duration-200 ${pathname === '/browse'
                    ? 'text-white font-semibold'
                    : 'text-[#e5e5e5] hover:text-[#979797]'
                    } translate-y-[6px]`}
                >
                  Browse
                </Link>
                {(status !== "loading" && session) && (
                  <Link
                    href='/clones'
                    className={`transition duration-200 ${pathname === '/clones'
                      ? 'text-white font-semibold'
                      : 'text-[#e5e5e5] hover:text-[#979797]'
                      } translate-y-[6px]`}
                  >
                    Chat
                  </Link>
                )}
                {(status !== "loading" && session) && (
                  <Link
                    href='/pricing'
                    className={`transition duration-200 ${pathname === '/pricing'
                      ? 'text-white font-semibold'
                      : 'text-[#e5e5e5] hover:text-[#979797]'
                      } translate-y-[6px]`}
                  >
                    Upgrade
                  </Link>
                )}

                <button
                  onClick={() => {
                    const modalElement = document.querySelector('#hs-slide-down-animation-modal-creator-program');
                    if (window.HSOverlay && typeof window.HSOverlay.close === 'function' && modalElement) {
                      window.HSOverlay.open(modalElement);
                    }
                  }}
                  className={`transition duration-200 ${pathname === '/create'
                    ? 'text-white font-semibold'
                    : 'text-[#e5e5e5] hover:text-[#979797]'
                    } translate-y-[6px]`}
                >
                  <span>
                    Create <sup className=''>Coming Soon</sup>
                  </span>
                </button>
                <div className='hidden lg:inline-flex'>
                  <SocialMedia />
                </div>
                <Link
                  href='/account'
                  className={`transition duration-200 ${pathname === '/account'
                    ? 'text-white font-semibold'
                    : 'text-[#e5e5e5] hover:text-[#979797]'
                    } translate-y-[6px] block lg:hidden`}
                >
                  Manage Account
                </Link>
                <div
                  className={`transition duration-200 leading-6 hover:cursor-pointer ${pathname === '/account'
                    ? 'text-white font-semibold'
                    : 'text-[#e5e5e5] hover:text-[#979797]'
                    } translate-y-[6px] block lg:hidden`}
                  onClick={() => signOut()}
                >
                  Logout
                </div>
                <div className='lg:hidden'>
                  <SocialMedia />
                </div>
              </div>
              <div className='hidden lg:flex items-center gap-x-4 text-white'>
                {(status !== 'loading' && session) && <AccountDropdown />}
                {(status !== 'loading' && !session) && (
                  <div className='flex items-center gap-x-3 text-white font-semibold' >
                    <Link href='/login' className='text-[#e5e5e5] hover:text-[#979797]' >Login</Link>
                  </div>
                )}
                {status === "loading" && (
                  <div className='h-[40px] w-[40px] ' >&nbsp;</div>
                )}
              </div>
            </div>
          </div>
        </nav>
      </header>
      </div>
    </>
  )
}