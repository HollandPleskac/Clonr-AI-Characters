'use client'
import LoginModal from './Auth/Login'


export default function AuthModal() {
  return (
    <div
      id='hs-slide-down-animation-modal'
      className='hs-overlay hidden w-full h-full fixed top-0 left-0 z-[200] overflow-x-hidden overflow-y-auto flex items-center justify-center hs-overlay-open:backdrop-blur-md hs-overlay-open:bg-black hs-overlay-open:bg-opacity-50'
    >
      <div className='hs-overlay-open:mt-7 hs-overlay-open:mb-7 hs-overlay-open:opacity-100 hs-overlay-open:duration-500 mt-0 opacity-0 ease-out transition-all sm:max-w-[366px] sm:w-full m-3 sm:mx-auto'>
        <div className='flex flex-col '>
          <div className='relative'>
            <LoginModal />
          </div>
        </div>
      </div>
    </div>
  )
}
