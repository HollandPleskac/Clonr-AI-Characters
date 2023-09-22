'use client'

import { useEffect, useState } from 'react'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'swiper/css/scrollbar'

import { Tag } from '@/types'
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

export default function BrowsePage({ initialTagName, initialSort }: { initialTagName: string, initialSort: string}) {

    const router = useRouter()
    const pathname = usePathname()
    const searchParams = useSearchParams()

    const duration = 500

    const [activeSort, setActiveSort] = useState<string>(initialSort)
    const [activeTag, setActiveTag] = useState<Tag|null>(null)
    const [isLoadingInitialActiveTag, setIsLoadingInitialActiveTag] = useState(!activeTag)

    // tags state
    const { data: tags, isLoading: isLoadingTags } = useQueryTags();
    
    function getActiveTag(tags:Tag[], tagName:string) {
        const activeTag = tags.find(tag => tag.name === tagName);
        return activeTag || null;
    }

    useEffect(() => {
        if (tags && initialTagName) {
            setActiveTag(getActiveTag(tags, initialTagName))
        } else if (tags && initialTagName==="") {
            setActiveTag(null)
        }
            
        setIsLoadingInitialActiveTag(false)
    }, [initialTagName, tags])

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
            <AuthModal />
            <RequestCloneModal />
            <CreatorProgramModal />

            <ScaleFadeIn loaded={!(isLoadingCharacters || isLoadingTags)} duration={duration}>


                <div className='flex px-[4%] gap-x-8 mt-[50px]'  >

                    <div className='flex flex-wrap gap-[6px]' >
                        {(!tags || isLoadingInitialActiveTag) && (
                            <div className='text-white h-[300px] bg-purple-400 w-[300px]' >asdf&nbsp;</div>
                        )}
                        {tags && tags.map((tag) => (
                            <div
                                key={tag.id}
                            >
                                <TagComponent
                                    name={tag.name}
                                    onClick={(tagName) => {
                                        if (tagName === activeTag?.name) {
                                            if (router) {
                                                router.push(pathname + updateUrlParams(searchParams, "tag", ""))
                                            }
                                        } else {
                                            if (router) {
                                                router.push(pathname + updateUrlParams(searchParams, "tag", tagName))
                                            }
                                        }
                                    }}
                                    active={tag.id === activeTag?.id}

                                />
                            </div>
                        ))}
                    </div>

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

        </div>
    )
}

