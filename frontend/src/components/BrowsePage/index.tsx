'use client'

import { useEffect, useState } from 'react'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'

import TopBar from '@/components/TopBar'
import AlertBar from '@/components/AlertBar'
import { Character, Tag } from '@/types'
import CharacterGrid from '@/components/HomePage/CharacterGrid'
import TagComponent from './Tag'
import Dropdown from './Dropdown'
import { useQueryTags } from '@/hooks/useTags'
import { CloneSortType } from '@/client/models/CloneSortType'
import { useClonesPagination } from '@/hooks/useClonesPagination'
import ScaleFadeIn from '../Transitions/ScaleFadeIn'
import AuthModal from '../Modal/AuthModal'
import { useClosePrelineModal } from '@/hooks/useClosePrelineModal'
import RequestCloneModal from '../Modal/RequestCloneModal'
import CreatorProgramModal from '../Modal/CreatorProgramModal'
import { ReadonlyURLSearchParams, usePathname, useSearchParams, useRouter } from 'next/navigation'

export default function BrowsePage({ initialQ, initialTag, initialSort }: { initialQ: string, initialTag: Tag | null, initialSort: string }) {

    const router = useRouter()
    const pathname = usePathname()
    const searchParams = useSearchParams()

    const [searchInput, setSearchInput] = useState(initialQ)
    const [searchParam, setSearchParam] = useState(initialQ)
    const [showSearchGrid, setShowSearchGrid] = useState(false)
    const duration = 500

    const [activeTag, setActiveTag] = useState<Tag | null>(initialTag)

    const [activeSort, setActiveSort] = useState<string>(initialSort)

    // tags state
    const { data: tags, isLoading: isLoadingTags } = useQueryTags();

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

    function updateUrlParams(searchParams: ReadonlyURLSearchParams, updateKey: string, updateValue: string): string {
        const newParams = new URLSearchParams(searchParams.toString());
    
        if (updateValue) {
            newParams.set(updateKey, updateValue);
        } else {
            newParams.delete(updateKey);
        }
    
        return `?${newParams.toString()}`;
    }

    // search delay
    useEffect(() => {
        const timer = setTimeout(() => {
            if (router) {
                router.push(pathname + updateUrlParams(searchParams, "q", searchInput))
            }
            setSearchParam(searchInput)
        }, duration)
        return () => clearTimeout(timer)
    }, [searchInput])

    // search grid state
    const queryParamsSearch = {
        // name: searchParam,
        sort: CloneSortType["TOP"],
        similar: searchParam,
        limit: 30
    }

    const {
        paginatedData: searchedCharacters,
        isLastPage: isLastSearchedCharactersPage,
        isLoading: isLoadingSearchedCharacters
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
        if (router) {
            router.push(pathname + updateUrlParams(searchParams, "sort", sort))
        }
        setActiveSort(sort)

    }

    useEffect(() => {
        require('preline')
    }, [])

    useClosePrelineModal()

    return (
        <div className=''>
            <AlertBar />

            <AuthModal />
            <RequestCloneModal />
            <CreatorProgramModal />

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
                            <div className='w-full flex-grow' >&nbsp;</div>
                        )}
                        {!isLoadingTags && (
                            <div className='flex flex-wrap gap-[6px]' >
                                {tags!.map((tag, idnex) => (
                                    <div
                                        key={tag.id}
                                    >
                                        <TagComponent
                                            name={tag.name}
                                            onClick={(tagName) => {
                                                if (tagName === activeTag?.name) {
                                                    setActiveTag(null);
                                                } else {
                                                    setActiveTag(tag);
                                                }
                                            }}
                                            active={tag.id === activeTag?.id}

                                        />
                                    </div>
                                ))}
                            </div>
                        )}
                        <Dropdown onItemClick={handleSortClick} activeSort={activeSort} />
                    </div>

                    {isLoadingCharacters && (
                        <div className="grid place-items-center"
                            style={{
                                height: "calc(100vh - 50px - 75px - 80px)"
                            }}>
                            &nbsp;
                            {/* <ColorRing
                                visible={true}
                                height="80"
                                width="80"
                                ariaLabel="blocks-loading"
                                wrapperStyle={{}}
                                wrapperClass="blocks-wrapper"
                                colors={['#9333ea', '#9333ea', '#9333ea', '#9333ea', '#9333ea']}
                            /> */}
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
        </div>
    )
}

