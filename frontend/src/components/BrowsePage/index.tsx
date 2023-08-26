'use client'

import { useEffect, useState } from 'react'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'

import TopBarStatic from '@/components/TopBarStatic'
import AlertBar from '@/components/AlertBar'
import { Character, Tag } from '@/types'
import AuthModal from '../AuthModal'
import SearchGrid from '@/components/HomePage/SearchGrid'
import TagComponent from './Tag'
import Dropdown from './Dropdown'
import { useQueryTags } from '@/hooks/useTags'
import { useQueryClones } from '@/hooks/useClones'
import { CloneSortType } from '@/client/models/CloneSortType'
import { Swiper, SwiperSlide } from 'swiper/react'
import { Navigation, Pagination, Scrollbar } from 'swiper/modules'
import { ColorRing } from 'react-loader-spinner'

export default function BrowsePage() {
    // tags state
    const { data: tags, error: tagsError, isLoading: isLoadingTags } = useQueryTags();
    const [activeTag, setActiveTag] = useState<Tag | null>()

    // Sort state
    const [activeSort, setActiveSort] = useState<string>("Trending")
    const [activeSortType, setActiveSortType] = useState<string>("TOP")

    // infinite scroll state
    const [hasMoreData, setHasMoreData] = useState(true)

    const fetchMoreGridData = () => {
        // TODO: edit, incorporate useSWRInfinite on infinite scroll side
    }

    // search grid characters state
    const searchQueryParams = {
        tags: activeTag ? [activeTag.id] : null,
        sort: CloneSortType[activeSortType],
        offset: 0,
        limit: 20
    }
    const { data: characters, isLoading: isLoadingCharacters } = useQueryClones(searchQueryParams);

    // handle sorting logic
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
        const sort_type = mapSortClickToSortType(sort)
        setActiveSort(sort)
        setActiveSortType(sort_type)
    }

    useEffect(() => {
        require('preline')
    }, [])

    return (
        <div className=''>
            <AlertBar />

            <TopBarStatic
            />

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
                <SearchGrid
                    characters={characters}
                    doneSearching={!isLoadingCharacters}
                    fetchMoreData={fetchMoreGridData}
                    hasMoreData={hasMoreData}
                    showPadding2={true}

                />
            )}

            <AuthModal />
        </div>
    )
}

