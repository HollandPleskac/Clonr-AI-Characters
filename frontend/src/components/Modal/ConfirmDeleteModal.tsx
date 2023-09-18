'use client'
import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { ConversationsService } from '@/client'


export default function ConfirmDeleteModal({ conversationId }: { conversationId: string | null }) {

  async function handleConfirmDelete(conversationId: string | null) {
    if (conversationId) {
      await ConversationsService.deleteConversationConversationsConversationIdDelete(conversationId)
    }

    // close modal after deleting conversation
    const modalElement = document.querySelector('#hs-slide-down-animation-modal-confirm-delete');
    console.log("modal el", modalElement)
    if (window.HSOverlay && typeof window.HSOverlay.close === 'function' && modalElement) {
      window.HSOverlay.close(modalElement);
    }
  }

  return (
    <div
      id='hs-slide-down-animation-modal-confirm-delete'
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
                      <div className='h-8 w-8 min-w-8 relative'>
                        <Image
                          src='/clonr-logo.png'
                          alt='logo'
                          layout='fill'
                          objectFit='cover'
                          className=''
                        />
                      </div>
                      <h3 className='ml-2 text-[20px] font-semibold leading-5 text-white font-fabada'>
                        Are you sure you want to delete this conversation
                      </h3>
                    </Link>
                  </div>
                  <div className='mt-5 flex flex-col gap-y-4 '>

                    <button
                      type='button'
                      onClick={() => handleConfirmDelete(conversationId)}
                      className='relative hover:bg-opacity-80 flex justify-center items-center bg-[#f0f0f0] active:opacity-90 text-black w-full py-3  gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#f0f0f0] transition-all text-sm border-[#f0f0f0] focus:ring-offset-gray-800'
                    >
                      <div className='w-full flex items-center' >
                        <p className='grow' >Confirm Delete</p>
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
