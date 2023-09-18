'use client'
import Image from 'next/image'
import Link from 'next/link'
import { useQueryTags } from '@/hooks/useTags';
import { useState } from 'react';
import { CreatorPartnerProgramSignupCreate, Tag } from '@/client';
import { SignupsService } from '@/client';
import { useSession } from 'next-auth/react';

export default function CreatorProgramModal() {    
    const [email, setEmail] = useState('')
    const [moreInfo, setMoreInfo] = useState('')
    const [isError, setIsError] = useState(false)
    const [nsfw, setNSFW] = useState(false)
    const [personal, setPersonal] = useState(false)
    const [quality, setQuality] = useState(false)
    const [story, setStory] = useState(false)
    const [roleplay, setRoleplay] = useState(false)

    return (
        <>
            <div
                id='hs-slide-down-animation-modal-creator-program'
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
                                                    { true && 'Become a creator'}
                                                    {/* {true && "You're already on the creator waitlist"} */}
                                                </h3>
                                            </Link>
                                        </div>
                                        {/* <div className='mt-5 flex flex-col gap-y-4' >
                                        <button
                                                type='button'
                                                onClick={async () => {
                                                    if (email === '') {
                                                        setIsError(true)
                                                        return
                                                    }

                                                    const requestBody: CreatorPartnerProgramSignupCreate = {
                                                        email: email,
                                                        nsfw: nsfw,
                                                        personal: personal,
                                                        quality: quality,
                                                        story: story,
                                                        roleplay: roleplay
                                                    }
                                                    console.log("request body",requestBody)
                                                    await SignupsService.creatorSignupSignupCreatorsPost(requestBody)
                                                }}
                                                className='relative hover:bg-opacity-80 flex justify-center items-center bg-[#f0f0f0] active:opacity-90 text-black w-full py-3  gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#f0f0f0] transition-all text-sm border-[#f0f0f0] focus:ring-offset-gray-800'
                                            >
                                                <div className='w-full flex items-center' >
                                                    <p className='grow' >Back to Clonr</p>
                                                </div>
                                            </button>
                                        </div> */}
                                        <div className='mt-5 flex flex-col gap-y-4 '>
                                            <div  >
                                                <input value={email} onChange={(e) => {
                                                    if (isError) {
                                                        setIsError(false)
                                                    }
                                                    setEmail(e.target.value)
                                                }} type="email" name="name" id="name" className="text-gray-400 block w-full pl-3 block flex-1 border-0 rounded-md border-0 py-1.5 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" placeholder="email address" />
                                                <p className={`text-red-400 text-sm mt-1 ${isError ? 'visible' : 'hidden'}`} >Email needs to be filled out</p>

                                            </div>
                                            <textarea value={moreInfo} onChange={(e) => setMoreInfo(e.target.value)} id="desc" name="desc" rows={3} placeholder='Tell us why you signed up ...' className="text-gray-400 block w-full rounded-md border-0 py-1.5 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"></textarea>
                                            <p className='text-gray-400 text-sm' >What kind of bots do you want to create?</p>
                                            <div className='flex items-center'>
                                                <div className='flex items-center h-5'>
                                                    <input
                                                        checked={nsfw}
                                                        onChange={() => setNSFW(prevState => !prevState)}
                                                        id='nsfw'
                                                        aria-describedby='nsfw'
                                                        type='checkbox'
                                                        className='w-4 h-4 border focus:ring-transparent border-gray-300 rounded bg-gray-50  dark:bg-gray-700 dark:border-gray-600  checked:text-purple-500'
                                                        required={false}
                                                        style={{ boxShadow: 'none' }}
                                                    />
                                                </div>
                                                <div className='ml-3 text-sm'>
                                                    <label
                                                        htmlFor='nsfw'
                                                        className='font-light text-gray-500 dark:text-gray-300'
                                                    >
                                                        NSFW
                                                    </label>
                                                </div>
                                            </div>
                                            <div className='flex items-center'>
                                                <div className='flex items-center h-5'>
                                                    <input
                                                        checked={personal}
                                                        onChange={() => setPersonal(prevState => !prevState)}
                                                        id='personal'
                                                        aria-describedby='personal'
                                                        type='checkbox'
                                                        className='w-4 h-4 border focus:ring-transparent border-gray-300 rounded bg-gray-50  dark:bg-gray-700 dark:border-gray-600  checked:text-purple-500'
                                                        required={false}
                                                        style={{ boxShadow: 'none' }}
                                                    />
                                                </div>
                                                <div className='ml-3 text-sm'>
                                                    <label
                                                        htmlFor='personal'
                                                        className='font-light text-gray-500 dark:text-gray-300'
                                                    >
                                                        Personal
                                                    </label>
                                                </div>
                                            </div>
                                            <div className='flex items-center'>
                                                <div className='flex items-center h-5'>
                                                    <input
                                                        checked={quality}
                                                        onChange={() => setQuality(prevState => !prevState)}
                                                        id='quality'
                                                        aria-describedby='quality'
                                                        type='checkbox'
                                                        className='w-4 h-4 border focus:ring-transparent border-gray-300 rounded bg-gray-50  dark:bg-gray-700 dark:border-gray-600  checked:text-purple-500'
                                                        required={false}
                                                        style={{ boxShadow: 'none' }}
                                                    />
                                                </div>
                                                <div className='ml-3 text-sm'>
                                                    <label
                                                        htmlFor='quality'
                                                        className='font-light text-gray-500 dark:text-gray-300'
                                                    >
                                                        Quality
                                                    </label>
                                                </div>
                                            </div>
                                            <div className='flex items-center'>
                                                <div className='flex items-center h-5'>
                                                    <input
                                                        checked={story}
                                                        onChange={() => setStory(prevState => !prevState)}
                                                        id='story'
                                                        aria-describedby='story'
                                                        type='checkbox'
                                                        className='w-4 h-4 border focus:ring-transparent border-gray-300 rounded bg-gray-50  dark:bg-gray-700 dark:border-gray-600  checked:text-purple-500'
                                                        required={false}
                                                        style={{ boxShadow: 'none' }}
                                                    />
                                                </div>
                                                <div className='ml-3 text-sm'>
                                                    <label
                                                        htmlFor='story'
                                                        className='font-light text-gray-500 dark:text-gray-300'
                                                    >
                                                        Story
                                                    </label>
                                                </div>
                                            </div>
                                            <div className='flex items-center'>
                                                <div className='flex items-center h-5'>
                                                    <input
                                                        checked={roleplay}
                                                        onChange={() => setRoleplay(prevState => !prevState)}
                                                        id='roleplay'
                                                        aria-describedby='roleplay'
                                                        type='checkbox'
                                                        className='w-4 h-4 border focus:ring-transparent border-gray-300 rounded bg-gray-50  dark:bg-gray-700 dark:border-gray-600  checked:text-purple-500'
                                                        required={false}
                                                        style={{ boxShadow: 'none' }}
                                                    />
                                                </div>
                                                <div className='ml-3 text-sm'>
                                                    <label
                                                        htmlFor='roleplay'
                                                        className='font-light text-gray-500 dark:text-gray-300'
                                                    >
                                                        Roleplay
                                                    </label>
                                                </div>
                                            </div>
                                            <button
                                                type='button'
                                                onClick={async () => {
                                                    if (email === '') {
                                                        setIsError(true)
                                                        return
                                                    }

                                                    const requestBody: CreatorPartnerProgramSignupCreate = {
                                                        email: email,
                                                        nsfw: nsfw,
                                                        personal: personal,
                                                        quality: quality,
                                                        story: story,
                                                        roleplay: roleplay
                                                    }
                                                    console.log("request body",requestBody)
                                                    await SignupsService.creatorSignupSignupCreatorsPost(requestBody)
                                                }}
                                                className='relative hover:bg-opacity-80 flex justify-center items-center bg-[#f0f0f0] active:opacity-90 text-black w-full py-3  gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#f0f0f0] transition-all text-sm border-[#f0f0f0] focus:ring-offset-gray-800'
                                            >
                                                <div className='w-full flex items-center' >
                                                    <p className='grow' >Join the creator partner program</p>
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
