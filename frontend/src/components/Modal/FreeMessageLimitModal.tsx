'use client'
import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/navigation'


export default function FreeMessageLimitModal() {
  const router = useRouter()

  async function handlePushPricing() {
    const modalElement = document.querySelector("#hs-slide-down-animation-modal");
    if (window.HSOverlay && typeof window.HSOverlay.close === 'function' && modalElement) {
      window.HSOverlay.close(modalElement);
    }
    router.push('/pricing')
  }

  return (
    <div
      id='hs-slide-down-animation-modal-free-message-limit'
      className='hs-overlay hidden w-full h-full fixed top-0 left-0 z-[200] overflow-x-hidden overflow-y-auto flex items-center justify-center hs-overlay-open:backdrop-blur-md hs-overlay-open:bg-black hs-overlay-open:bg-opacity-50'
    >
      <div className='hs-overlay-open:mt-7 hs-overlay-open:mb-7 hs-overlay-open:opacity-100 hs-overlay-open:duration-500 mt-0 opacity-0 ease-out transition-all sm:max-w-[466px] sm:w-full m-3 sm:mx-auto'>
        <div className='flex flex-col '>
          <div className='relative'>
            <main className='w-full max-w-md mx-auto p-6 bg-transparent'>
              <div className='mt-7 rounded-xl shadow-sm border-white border-[1px] border-opacity-50 bg-[#141414] rounded-2xl'>
                <div className='p-4 sm:p-7'>
                  <div className='text-center flex justify-start'>
                    <Link href='/' className=' flex items-center justify-start cursor-pointer'>
                      <div className='h-8 w-8 relative'>
                        <Image
                          src='/clonr-logo.png'
                          alt='logo'
                          layout='fill'
                          objectFit='cover'
                          className=''
                        />
                      </div>
                      <h3 className='ml-2 text-[20px] font-semibold leading-5 text-white font-fabada'>
                        You've reached your free message limit
                      </h3>
                    </Link>
                  </div>
                  <div className='mt-5 flex flex-col gap-y-4 '>

                    <button
                      type='button'
                      onClick={() => handlePushPricing()}
                      className='relative hover:bg-opacity-80 flex justify-center items-center bg-[#f0f0f0] active:opacity-90 text-black w-full py-3  gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#f0f0f0] transition-all text-sm border-[#f0f0f0] focus:ring-offset-gray-800'
                    >
                      <div className='w-full flex items-center' >
                        {/* <svg
                  width='24px'
                  height='24px'
                  viewBox='0 0 46 47'
                  fill='none'
                  className='ml-4 absolute w-[30px]'
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
                </svg> */}
                        <p className='grow' >Sign up for a plan here</p>
                      </div>
                    </button>

                  </div>
                </div>

              </div>
            </main>

          </div>
        </div>
      </div>
    </div>
  )
}
