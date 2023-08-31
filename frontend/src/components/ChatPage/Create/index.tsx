'use client'

import React, { useEffect } from 'react'
import Image from 'next/image'
import useConversations from '@/hooks/useConversations'
import { useRouter } from 'next/navigation'
import PopoverCreate from './PopoverCreate'
import SmallNav from '../Characters/SmallSidebar'
import TagsComponent from '@/components/HomePage/Tags'
import { MemoryStrategy } from '@/client/models/MemoryStrategy'
import { InformationStrategy } from '@/client/models/InformationStrategy'
import { useQueryClonesById } from '@/hooks/useClones'
import { ColorRing } from 'react-loader-spinner'
import Dropdown from './DropdownCreate'
import { AdaptationStrategy } from '@/client'
import { useSidebarClonesPagination } from '@/hooks/useSidebarClonesPagination'

type CreateProps = {
    characterId: string
}

const tags = [
    {
        id: '1',
        created_at: new Date(),
        updated_at: new Date(),
        color_code: '48FF83',
        name: "Anime"
    }, {
        id: '2',
        created_at: new Date(),
        updated_at: new Date(),
        color_code: 'FF0392',
        name: "Warrior"
    },
    , {
        id: '2',
        created_at: new Date(),
        updated_at: new Date(),
        color_code: 'DD04FF',
        name: "Female"
    }
]



const Create = ({ characterId }: CreateProps) => {
    const router = useRouter();

    // clone information
    const { data: character, error, isLoading } = useQueryClonesById({
        cloneId: characterId
    });

    // last clone id
    const {
        paginatedData: sidebarClone,
        isLoading: isLoadingSidebarClone,
    } = useSidebarClonesPagination({ cloneId: characterId, limit: 1 })


    const { createConversation } = useConversations();

    async function createCharacterConversation(
        characterId: string,
        memoryStrategy: string,
    ) {
        const conversationData = {
            name: 'Test Conversation',
            user_name: 'Test User',
            memory_strategy: MemoryStrategy[memoryStrategy],
            information_strategy: InformationStrategy['internal'],
            adaptation_strategy: AdaptationStrategy["zero"],
            clone_id: characterId,
        }
        console.log("conv data", conversationData)
        const conversationId = await createConversation(conversationData)
        return conversationId
    }

    useEffect(() => {
        require('preline')
    }, [])

    const lastConversationId = "test"

    return (
        <div className='w-[100%] border-r-[2px] border-[#252525] bg-[#121212] lg:inline'>
            {isLoading && (
                <div className='h-screen w-full grid place-items-center' >
                    <ColorRing
                        visible={true}
                        height="80"
                        width="80"
                        ariaLabel="blocks-loading"
                        wrapperStyle={{}}
                        wrapperClass="blocks-wrapper"
                        colors={['#9333ea', '#9333ea', '#9333ea', '#9333ea', '#9333ea']}
                    />
                </div>
            )}
            {!isLoading && (
                <div
                    className='h-full flex flex-col gap-x-8'
                    style={{ height: 'calc(100vh)' }}
                >
                    <div className='flex h-[122px] w-full items-center justify-between border-b border-[#252525] px-10'>
                        <div className='flex items-center'>
                            <SmallNav characterId={characterId} />
                            <div className='h-[55px] w-[55px] relative'>
                                <Image
                                    src={character.avatar_uri}
                                    alt='Character Profile Picture'
                                    layout='fill'
                                    objectFit='cover'
                                    className='rounded-full'
                                />
                            </div>

                            {character ? (
                                <div className='flex flex-col ml-6 gap-y-3'>
                                    <h3 className='text-3xl font-bold leading-5 text-white'>
                                        {character.name}
                                    </h3>
                                </div>
                            ) : (
                                <p>Loading character</p>
                            )}


                        </div>
                        <div>
                            {
                                isLoadingSidebarClone && (
                                    <div className='w-[40px] h-[40px]' >&nbsp;</div>
                                )
                            }
                            {
                                (!isLoadingSidebarClone && sidebarClone && sidebarClone.length == 1) && (
                                    <Dropdown characterId={character.id} lastConversationId={sidebarClone[0].id} />
                                )
                            }
                        </div>

                    </div>

                    <div className='overflow-auto pb-[40px] md:pb-0 flex flex-col md:flex-row gap-x-[48px] items-center md:items-start md:justify-center my-auto mt-[80px] md:mt-auto'>
                        <div className='w-[50%] md:w-[240px] flex flex-col mb-8 md:mb-0'>
                            <div className='h-[240px] w-full md:w-[240px] relative'>
                                <Image
                                    src={character.avatar_uri}
                                    alt='logo'
                                    layout='fill'
                                    objectFit='cover'
                                    className='rounded-lg mb-5'
                                />
                            </div>

                            <h2 className='text-lg text-center text-left my-4 font-light text-gray-500'>
                                {character.num_conversations} Chats
                            </h2>

                            <button
                                onClick={async () => {
                                    const conversationId = await createCharacterConversation(characterId, 'short_term')
                                    const new_url = `http://localhost:3000/clones/${characterId}/conversations/${conversationId}`
                                    console.log("NEW URL -> ", new_url)
                                    router.push(new_url)
                                }}
                                className='flex items-center justify-between w-full py-2 px-4 inline-flex bg-purple-500 rounded-lg hover:bg-purple-600 text-white'
                            >
                                Short Term Memory Chat
                                <PopoverCreate />
                            </button>
                            <button
                                onClick={async () => {
                                    const conversationId = await createCharacterConversation(characterId, 'long_term')
                                    const new_url = `http://localhost:3000/clones/${characterId}/conversations/${conversationId}`
                                    router.push(new_url)
                                }}
                                className='mt-2 flex items-center justify-between w-full py-2 px-4 inline-flex bg-purple-500 rounded-lg hover:bg-purple-600 text-white'
                            >
                                Long Term Memory Chat
                                <PopoverCreate />
                            </button>
                        </div>
                        <div className='w-[50%] md:w-1/3 flex flex-col justify-start'>
                            <h2 className='text-lg sm:text-4xl font-semibold mb-4 text-white'>
                                {character.name}
                            </h2>
                            <TagsComponent tags={tags} />
                            <p className='mb-4 mt-4 text-lg text-gray-400'>
                                {character.short_description}{' '}
                            </p>

                            <h2 className='text-lg mb-2 sm:text-xl font-semibold text-white flex justify-start gap-x-2  items-center'>
                                Long Description
                                <svg className='cursor-pointer' fill="#fff" width="22px" height="22px" viewBox="0 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg" stroke="#fff">
                                    <g id="SVGRepo_bgCarrier" stroke-width="0" />
                                    <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round" />
                                    <g id="SVGRepo_iconCarrier"> <title>popout</title> <path d="M15.694 13.541l2.666 2.665 5.016-5.017 2.59 2.59 0.004-7.734-7.785-0.046 2.526 2.525-5.017 5.017zM25.926 16.945l-1.92-1.947 0.035 9.007-16.015 0.009 0.016-15.973 8.958-0.040-2-2h-7c-1.104 0-2 0.896-2 2v16c0 1.104 0.896 2 2 2h16c1.104 0 2-0.896 2-2l-0.074-7.056z" /> </g>
                                </svg>
                            </h2>
                            <p className='text-gray-400 line-clamp-3' >
                                {character.long_description}{' '}
                            </p>
                            <h2 className='text-lg mb-2 mt-4 sm:text-xl font-semibold text-white flex justify-start gap-x-2  items-center'>
                                Greeting Message
                                <svg className='cursor-pointer' fill="#fff" width="22px" height="22px" viewBox="0 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg" stroke="#fff">
                                    <g id="SVGRepo_bgCarrier" stroke-width="0" />
                                    <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round" />
                                    <g id="SVGRepo_iconCarrier"> <title>popout</title> <path d="M15.694 13.541l2.666 2.665 5.016-5.017 2.59 2.59 0.004-7.734-7.785-0.046 2.526 2.525-5.017 5.017zM25.926 16.945l-1.92-1.947 0.035 9.007-16.015 0.009 0.016-15.973 8.958-0.040-2-2h-7c-1.104 0-2 0.896-2 2v16c0 1.104 0.896 2 2 2h16c1.104 0 2-0.896 2-2l-0.074-7.056z" /> </g>
                                </svg>
                            </h2>
                            <p className='text-gray-400 line-clamp-3' >
                                {character.long_description}{' '}
                            </p>

                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Create