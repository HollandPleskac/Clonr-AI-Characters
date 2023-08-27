'use client'

import { useEffect, useState } from 'react'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'

import TopBar from '@/components/TopBar'
import AlertBar from '@/components/AlertBar'
import { Character, Tag } from '@/types'
import AuthModal from '../AuthModal'
import CharacterGrid from '@/components/HomePage/CharacterGrid'
import TagComponent from './Tag'
import Dropdown from './Dropdown'
import { useQueryTags } from '@/hooks/useTags'
import { useQueryClones } from '@/hooks/useClones'
import { CloneSortType } from '@/client/models/CloneSortType'
import { Swiper, SwiperSlide } from 'swiper/react'
import { Navigation, Pagination, Scrollbar } from 'swiper/modules'
import { ColorRing } from 'react-loader-spinner'
import { useClonesPagination } from '@/hooks/useClonesPagination'
import ScaleFadeIn from '../Transitions/ScaleFadeIn'

export default function BrowsePage() {

    const [searchInput, setSearchInput] = useState('')
    const [showSearchGrid, setShowSearchGrid] = useState(false)
    const duration = 500

    const [activeTag, setActiveTag] = useState<Tag | null>()
    const [activeSort, setActiveSort] = useState<string>("Trending")

    // tags state
    const { data: tags, error: tagsError, isLoading: isLoadingTags } = useQueryTags();

    // character grid state
    const queryParams = {
        tags: activeTag ? [activeTag.id] : null,
        sort: CloneSortType[mapSortClickToSortType(activeSort)],
        limit: 30
    }

    const {
        paginatedData: characters,
        isLastPage: isLastCharactersPage,
        isLoading: isLoadingCharacters,
        size,
        setSize
    } = useClonesPagination(queryParams)

    // search grid state
    const queryParamsSearch = {
        name: searchInput,
        sort: CloneSortType["TOP"],
        similar: searchInput,
        limit: 30
    }

    const {
        paginatedData: searchedCharacters,
        isLastPage: isLastSearchedCharactersPage,
        isLoading: isLoadingSearchedCharacters,
        size: searchedCharactersSize,
        setSize: setSearchedCharactersSize
    } = useClonesPagination(queryParamsSearch)

    useEffect(() => {
        if (searchInput === '') {
            setShowSearchGrid(false)
            console.log(searchInput)
        } else {
            if (!showSearchGrid) {
                const timer = setTimeout(() => {
                    setShowSearchGrid(true)
                }, duration)
                return () => clearTimeout(timer)
            }
        }
    }, [searchInput])


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
        setActiveSort(sort)
    }

    useEffect(() => {
        require('preline')
    }, [])

    return (
        <div className=''>
            <AlertBar />

            <TopBar
                searchInput={searchInput}
                onSearchInput={(x) => setSearchInput(x)}
                clearSearchInput={() => setSearchInput('')}
            />

            {showSearchGrid && (
                <ScaleFadeIn loaded={showSearchGrid} duration={duration}>
                    <CharacterGrid
                        characters={searchedCharacters}
                        loading={isLoadingSearchedCharacters}
                        fetchMoreData={() => setSize(size + 1)}
                        hasMoreData={!isLastSearchedCharactersPage}
                    />
                </ScaleFadeIn>
            )}

            {!showSearchGrid && (
                <ScaleFadeIn loaded={!searchInput} duration={duration}>


                <div className='flex px-[4%] gap-x-8 mt-[50px]'  >
                    {isLoadingTags && (
                        <div className='w-full flex-grow text-white' >&nbsp;</div>
                    )}
                    {!isLoadingTags && (
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
                            {tags!.map((tag, index) => {
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
                                                setActiveTag(tag)
                                            }}
                                            active={tag.id === activeTag?.id}

                                        />
                                    </SwiperSlide>
                                )
                            })}
                        </Swiper>
                    )}
                    <Dropdown onItemClick={handleSortClick} activeSort={activeSort} />
                </div>

                {isLoadingCharacters && (
                    <div className="grid place-items-center"
                        style={{
                            height: "calc(100vh - 50px - 75px - 80px)"
                        }}>
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

                {!isLoadingCharacters && (
                    <CharacterGrid
                        characters={characters}
                        loading={isLoadingCharacters}
                        fetchMoreData={() => setSize(size + 1)}
                        hasMoreData={!isLastCharactersPage}
                        showPadding2={true}

                    />
                )}
            </ScaleFadeIn>
            )}

            <AuthModal />
        </div>
    )
}

