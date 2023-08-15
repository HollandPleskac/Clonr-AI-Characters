'use client'

import { useEffect, useRef, useState } from 'react'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'

const axios = require('axios').default

import TopBar from '@/components/TopBar'
import AlertBar from '@/components/AlertBar'
import { Character, Tag } from '@/types'
import useClones from '@/hooks/useClones'
import AuthModal from '../AuthModal'
import SearchGrid from '@/components/HomePage/SearchGrid'
import TagComponent from './Tag'
import SearchIcon from '../SearchIcon'
import XIcon from '../XIcon'

// search state


const dummyTags = [
    {
        id: 'test',
        created_at: 'string',
        updated_at: 'string',
        name: 'Anime',
        color_code: '#848282'
    },
    {
        id: 'test1',
        created_at: 'string',
        updated_at: 'string',
        name: 'Gaming',
        color_code: '#848282'
    },
    {
        id: 'test3',
        created_at: 'string',
        updated_at: 'string',
        name: 'Movies',
        color_code: '#848282'
    },
    {
        id: 'testasdf',
        created_at: 'string',
        updated_at: 'string',
        name: 'Male',
        color_code: '#848282'
    },
    {
        id: 'test5324',
        created_at: 'string',
        updated_at: 'string',
        name: 'Female',
        color_code: '#848282'
    },
    {
        id: 'test53dvfsgd2afd4',
        created_at: 'string',
        updated_at: 'string',
        name: 'Hero',
        color_code: '#848282'
    },
    {
        id: 'teserrherhrasdft5324',
        created_at: 'string',
        updated_at: 'string',
        name: 'Villan',
        color_code: '#848282'
    },
    {
        id: 'testhererhasdf324',
        created_at: 'string',
        updated_at: 'string',
        name: 'Celebrities',
        color_code: '#848282'
    },
    {
        id: 'teasdfeeest5324',
        created_at: 'string',
        updated_at: 'string',
        name: 'Horror',
        color_code: '#848282'
    },
    {
        id: 'teasdfrrrst5324',
        created_at: 'string',
        updated_at: 'string',
        name: 'Vampire',
        color_code: '#848282'
    },
    {
        id: 'teasdfsthhh5324',
        created_at: 'string',
        updated_at: 'string',
        name: 'Demon',
        color_code: '#848282'
    },
    {
        id: 'teasdfcccst5324',
        created_at: 'string',
        updated_at: 'string',
        name: 'Alien',
        color_code: '#848282'
    },
    {
        id: 'teasdfgggst5324',
        created_at: 'string',
        updated_at: 'string',
        name: 'History',
        color_code: '#848282'
    },
    {
        id: 'teadddsdfst5324',
        created_at: 'string',
        updated_at: 'string',
        name: 'Twitch',
        color_code: '#848282'
    },
    {
        id: 'teasdfsffft5324',
        created_at: 'string',
        updated_at: 'string',
        name: 'VTuber',
        color_code: '#848282'
    },
    {
        id: 'teasdffdsaast5324',
        created_at: 'string',
        updated_at: 'string',
        name: 'Non-English',
        color_code: '#848282'
    },
    {
        id: 'tefdasasdfst5324',
        created_at: 'string',
        updated_at: 'string',
        name: 'Books',
        color_code: '#848282'
    },
    {
        id: 'teasfddfsasdft5324',
        created_at: 'string',
        updated_at: 'string',
        name: 'Elf',
        color_code: '#848282'
    },
    {
        id: 'teasdfst5adsf324',
        created_at: 'string',
        updated_at: 'string',
        name: 'Orc',
        color_code: '#848282'
    },
]

interface BrowsePageProps {
    initialCharacters: Character[]
}

export default function BrowsePage({
    initialCharacters
}: BrowsePageProps) {
    const [searchedCharacters, setSearchedCharacters] = useState<Character[]>(initialCharacters)
    const [doneSearching, setDoneSearching] = useState(false)
    const [trill, setTrill] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const duration = 500
    const { queryClones, queryCloneById } = useClones()

    // search state
    const [searchInput, setSearchInput] = useState('')
    const [isInputActive, setInputActive] = useState(false)
    const handleInputFocus = () => setInputActive(true)
    const handleInputBlur = () => {
        if (searchInput === '') setInputActive(false)
    }
    const inputRefLg = useRef<HTMLInputElement>(null)
    const inputRefSm = useRef<HTMLInputElement>(null)

    const [tags, setTags] = useState<Tag[]>(dummyTags)
    const [activeTag, setActiveTag] = useState<Tag | null>()

    useEffect(() => {
        // fetch tags here (need another function to get tags in the useTags hook)
    }, [])

    useEffect(() => {
        require('preline')
    }, [])

    const handleCloneSearch = async () => {
        setLoading(true)
        setError(null)

        try {
            const queryParams = {
                // tags - convert arr to str
                tags: tags ? tags.map((tag) => tag.id).join(',') : null,
                name: searchInput,
                sort: 'top',
                similar: searchInput,
                offset: 0,
                limit: 10
            }
            const data = await queryClones(queryParams)
            setSearchedCharacters(data)
            setDoneSearching(searchInput !== '')
            setActiveTag(null)
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        const debounceTimeout = setTimeout(handleCloneSearch, 500)
        return () => {
            clearTimeout(debounceTimeout)
        }
    }, [searchInput])

    function handleTagClick(tag: Tag) {
        setActiveTag(tag)
        setSearchInput('')
        // can update searched characters here
    }

    return (
        <div className='pb-[75px]'>
            <AlertBar />

            <TopBar
                searchInput={searchInput}
                onSearchInput={(x) => setSearchInput(x)}
                clearSearchInput={() => setSearchInput('')}
            />



            <div
                className='relative group w-[500px] mx-auto my-10'
                onClick={() => {
                    console.log('active')
                    if (inputRefSm.current) {
                        inputRefSm.current.focus()
                    }
                }}
            >
                <button className='group absolute peer left-[10px] top-[13px] peer cursor-default'>
                    <SearchIcon
                        strokeClasses={` group-focus:stroke-[#5848BC] ${isInputActive ? 'stroke-[#5848BC]' : 'stroke-[#515151]'
                            } transition duration-100`}
                    />
                </button>
                <input
                    ref={inputRefSm}
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    onFocus={handleInputFocus}
                    onBlur={handleInputBlur}
                    className={`w-[500px] bg-[#1E1E1E] focus:cursor-auto peer py-auto h-[50px] transition-all  duration-500 rounded-lg border-none  pr-0 pl-[44px] text-[15px] font-light leading-6 text-[#979797] focus:ring-1 focus:ring-transparent`}
                    type='text'
                    placeholder='Search'
                    style={{ outline: 'none', resize: 'none' }}
                />
                <button
                    className={`absolute right-[10px] top-[17px] ${searchInput === '' ? 'hidden' : 'flex'
                        }`}
                    onClick={() => { setSearchInput('') }}
                >
                    <XIcon />
                </button>
            </div>




            <div className='flex flex-wrap px-[4%] gap-x-2 gap-y-2' >
                {tags.map(
                    (tag) => <TagComponent
                        key={tag.id}
                        name={tag.name}
                        onClick={() => {
                            handleTagClick(tag)
                        }}
                        active={tag.id === activeTag?.id}

                    />
                )}
            </div>
            <SearchGrid characters={searchedCharacters} doneSearching={true} paddingTop='100px' />
            <AuthModal />
        </div>
    )
}


