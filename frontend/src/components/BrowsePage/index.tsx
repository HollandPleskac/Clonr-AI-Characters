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
import useTags from '@/hooks/useTags'
import AuthModal from '../AuthModal'
import SearchGrid from '@/components/HomePage/SearchGrid'
import TagComponent from './Tag'
import SearchIcon from '../SearchIcon'
import XIcon from '../XIcon'
import Dropdown from './Dropdown'


const dummyTags = [
    {
        id: 'test',
        created_at: 'string',
        updated_at: 'string',
        name: 'Anime',
        color_code: '#848282'
    }
]

interface BrowsePageProps {
    initialCharacters: Character[]
}

export default function BrowsePage({
    initialCharacters
}: BrowsePageProps) {
    const [trill, setTrill] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const duration = 500
    const { queryClones, queryCloneById } = useClones()

    const { queryTags } = useTags()

    // search input state
    const [searchInput, setSearchInput] = useState('')
    const [isInputActive, setInputActive] = useState(false)
    const handleInputFocus = () => setInputActive(true)
    const handleInputBlur = () => {
        if (searchInput === '') setInputActive(false)
    }
    const inputRef = useRef<HTMLInputElement>(null)
    const didMountRef = useRef(false);

    // tags state
    const [tags, setTags] = useState<Tag[]>([])
    const [activeTag, setActiveTag] = useState<Tag | null>()

    // Sort state
    const [activeSort, setActiveSort] = useState<string>("Trending")

    // search grid characters state
    const [searchedCharacters, setSearchedCharacters] = useState<Character[]>(initialCharacters)
    const [doneSearching, setDoneSearching] = useState(true)
    const [hasMoreData, setHasMoreData] = useState(true)

    const fetchTags = async () => {
        try {
            const currTags = await queryTags()
            setTags(currTags)
        } catch (error) {
            console.log(error)
        }
    }

    useEffect(() => {
        fetchTags();
    }, []);

    const fetchMoreGridData = () => {
        // Simulate fetching 50 more characters from a server or other data source
        const newCharacter: Character[] = Array.from(
            { length: 50 },
            (_, index) => (
                {
                    id: 'test' + index,
                    created_at: 'string',
                    updated_at: 'string',
                    creator_id: 'string',
                    name: 'string',
                    short_description: 'ring',
                    avatar_uri: 'https://image.tmdb.org/t/p/w500/rktDFPbfHfUbArZ6OOOKsXcv0Bm.jpg',
                    num_messages: 34234,
                    num_conversations: 34,
                    tags: []
                }
            )
        )

        // Add the new characters to the end of the existing characters
        setSearchedCharacters((prevCharacters) => [
            ...prevCharacters,
            ...newCharacter,
        ])
        setHasMoreData(false)
    }


    useEffect(() => {
        require('preline')
    }, [])

    const handleCloneSearch = async () => {
        setLoading(true)
        setError(null)
        console.log("SEARCHING... this is searchInput: ", searchInput)
        try {
            // TODO: edit
            const queryParams = {
                tags: null, // tags ? tags.map((tag) => tag.id).join(',') : null,
                name: searchInput != '' ? searchInput : null,
                sort: 'top',
                similar: searchInput != '' ? searchInput : null,
                offset: 0,
                limit: 20
            }
            const data = await queryClones(queryParams)
            setSearchedCharacters(data)
            setDoneSearching(searchInput !== '')
            console.log("success")
        } catch (err: any) {
            setError(err.message)
            console.log("ERROR", err.message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        if (!didMountRef.current) {
            didMountRef.current = true;
            return;
        }

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

    function handleSortClick(sort: string) {
        console.log("sort", sort)
        setActiveSort(sort)
    }

    if (tags.length === 0) {
        return (
            <div> Loading tags... </div>
        )
    }
    

    return (
        <div className=''>
            <AlertBar />

            <TopBar
                searchInput={searchInput}
                onSearchInput={(x) => setSearchInput(x)}
                clearSearchInput={() => setSearchInput('')}
            />

            <div className='flex w-full justify-center items-center gap-x-4' >
                <div
                    className='relative group w-[500px]  my-10'
                    onClick={() => {
                        console.log('active')
                        if (inputRef.current) {
                            inputRef.current.focus()
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
                        ref={inputRef}
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
                        className={`absolute right-[10px] top-[17px] ${searchInput === '' ? 'hidden' : 'flex'}`}
                        onClick={() => { setSearchInput('') }}
                    >
                        <XIcon />
                    </button>
                </div>
                <Dropdown onItemClick={handleSortClick} activeSort={activeSort} />
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

            <SearchGrid
                characters={searchedCharacters}
                doneSearching={doneSearching}
                fetchMoreData={fetchMoreGridData}
                hasMoreData={hasMoreData}
                showPadding2={true}

            />

            <AuthModal />
        </div>
    )
}


