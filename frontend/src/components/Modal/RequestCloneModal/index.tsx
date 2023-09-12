'use client'
import Image from 'next/image'
import Link from 'next/link'
import Multiselect from './Multiselect'
import { useQueryTags } from '@/hooks/useTags';
import { useState } from 'react';
import { Tag } from '@/client';

export default function RequestCloneModal() {
  const [selectedTags, setSelectedTags] = useState<Tag[]>([])
  const { data: tags, isLoading: isLoadingTags } = useQueryTags();
  const [charName, setCharName] = useState('')
  const [moreInfo, setMoreInfo] = useState('')
  const [isError, setIsError] = useState(false)

  return (
    <>
      <div
        id='hs-slide-down-animation-modal-request'
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
                          Request a clone
                        </h3>
                      </Link>
                    </div>
                    <div className='mt-5 flex flex-col gap-y-4 '>
                      <div>
                        <input value={charName} onChange={(e) => {
                          if (isError) {
                            setIsError(false)
                          }
                          setCharName(e.target.value)
                        }} type="text" name="name" id="name" className="text-gray-400 block w-full pl-3 block flex-1 border-0 rounded-md border-0 py-1.5 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" placeholder="Clone Name" />
                        <p className={`text-red-400 text-sm mt-1 ${isError ? 'visible' : 'hidden'}`} >Name needs to be filled out</p>
                      </div>

                      <Multiselect
                        selectedTags={selectedTags}
                        addSelectedTag={(x: Tag) => {
                          setSelectedTags([...selectedTags ?? [], x])
                        }}
                        removeSelectedTag={(x: Tag) => {
                          const updatedTags = selectedTags.filter(tag => tag.name !== x.name);
                          setSelectedTags(updatedTags);
                        }}
                        tags={tags}
                      />
                      <textarea value={moreInfo} onChange={(e) => setMoreInfo(e.target.value)} id="desc" name="desc" rows={3} placeholder='Short description of clone' className="text-gray-400 block w-full rounded-md border-0 py-1.5 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"></textarea>

                      <button
                        type='button'
                        onClick={() => {
                          setIsError(true)
                        }}
                        className='relative hover:bg-opacity-80 flex justify-center items-center bg-[#f0f0f0] active:opacity-90 text-black w-full py-3  gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#f0f0f0] transition-all text-sm border-[#f0f0f0] focus:ring-offset-gray-800'
                      >
                        <div className='w-full flex items-center' >
                          <p className='grow' >Request Clone</p>
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
    </>
  )
}
