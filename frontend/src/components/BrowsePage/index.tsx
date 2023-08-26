'use client'

import { useEffect, useRef, useState } from 'react'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'

//const axios = require('axios').default

import TopBarStatic from '@/components/TopBarStatic'
import AlertBar from '@/components/AlertBar'
import { Character, Tag } from '@/types'
import AuthModal from '../AuthModal'
import SearchGrid from '@/components/HomePage/SearchGrid'
import TagComponent from './Tag'
import SearchIcon from '../SearchIcon'
import XIcon from '../XIcon'
import Dropdown from './Dropdown'
import { useQueryTags } from '@/hooks/useTags'
import { useQueryClones } from '@/hooks/useClones'
import { CloneSortType } from '@/client/models/CloneSortType'
import { Swiper, SwiperSlide } from 'swiper/react'
import { Navigation, Pagination, Scrollbar } from 'swiper/modules'

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
    const [activeSortType, setActiveSortType] = useState<string>("TOP")

    // search grid characters state
    const [searchedCharacters, setSearchedCharacters] = useState<any[]>(initialCharacters)
    const [doneSearching, setDoneSearching] = useState(true)
    const [hasMoreData, setHasMoreData] = useState(true)

    const { data: tagsData, error: tagsError, isLoading: isLoadingTags } = useQueryTags();

    useEffect(() => {
        if (!isLoadingTags && tagsData) {
            setTags(tagsData)
            setDoneSearching(true)
            setLoading(false)
        }
    }, [tagsData, isLoadingTags])

    const fetchMoreGridData = () => {
        // TODO: edit, incorporate useSWRInfinite on infinite scroll side
    }


    useEffect(() => {
        require('preline')
    }, [])

    const searchQueryParams = {
        tags: activeTag ? [activeTag.id] : null,
        name: searchInput,
        sort: CloneSortType[activeSortType],
        similar: searchInput,
        offset: 0,
        limit: 20
    }
    const { data: searchData, isLoading: isLoadingSearch } = useQueryClones(searchQueryParams);

    useEffect(() => {
        if (!isLoadingSearch && searchData) {
            console.log("this is activeTag: ", activeTag)
            setSearchedCharacters(searchData)
            setDoneSearching(true)
            setLoading(false)
        }
    }, [searchInput, isLoadingSearch, activeTag, activeSortType])



    function handleTagClick(tag: Tag) {
        console.log("clicked tag: ", tag)
        setActiveTag(tag)
        setSearchInput('')
        // can update searched characters here
    }

    function mapSortClickToSortType(sort: string) {
        switch (sort) {
            case "Trending":
                return "HOT"
            case "Newest":
                return "NEWEST"
            case "Oldest":
                return "OLDEST"
            case "Most Chats":
                return "TOP"
            default:
                return "TOP"
        }
    }

    function handleSortClick(sort: string) {
        console.log("sort", sort)
        const sort_type = mapSortClickToSortType(sort)
        console.log("sort_type: ", sort_type)
        setActiveSort(sort)
        setActiveSortType(sort_type)
    }

    if (tags.length === 0) {
        return (
            <div> Loading tags... </div>
        )
    }



    return (
        <div className=''>
            <AlertBar />

            <TopBarStatic
            />

            <div className='flex px-[4%] gap-x-8 mt-[50px]'  >
                <Swiper
                    modules={[Navigation, Pagination, Scrollbar]}
                    navigation={true}
                    spaceBetween={4}
                    slidesPerView={'auto'}
                    slidesPerGroup={5}
                    speed={1100}
                    className={`w-full flex gap-x-2`}
                    style={{
                        zIndex: 50,
                    }}
                >
                    {tags.map((tag, index) => {
                        return (
                            <SwiperSlide
                                key={tag.id}
                                className='w-auto inline-flex flex-grow flex-shrink-0'
                                style={{
                                    width: 'auto'
                                }}
                            >
                                <TagComponent
                                    name={tag.name}
                                    onClick={() => {
                                        handleTagClick(tag)
                                    }}
                                    active={tag.id === activeTag?.id}

                                />
                            </SwiperSlide>
                        )
                    })}
                </Swiper>
                <Dropdown onItemClick={handleSortClick} activeSort={activeSort} />
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

