'use client'
import Footer from '@/components/Footer'
import { ReadonlyURLSearchParams, useSearchParams } from 'next/navigation'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useSearchContext } from '@/context/searchContext'
import ScaleFadeIn from '@/components/Transitions/ScaleFadeIn'
import CharacterGrid from '@/components/HomePage/CharacterGrid'
import { useClonesPagination } from '@/hooks/useClonesPagination'
import { CloneSortType } from '@/client/models/CloneSortType'
import { useClosePrelineModal } from '@/hooks/useClosePrelineModal'
import AuthModal from '@/components/Modal/AuthModal'
import RequestCloneModal from '@/components/Modal/RequestCloneModal'
import CreatorProgramModal from '@/components/Modal/CreatorProgramModal'

export default function Home() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const ctx = useSearchContext()

    const queryParamsSearch = {
        // name: searchParam,
        sort: CloneSortType["TOP"],
        similar: ctx.searchParam,
        limit: 30
    }

    const {
        paginatedData: searchedCharacters,
        isLastPage: isLastSearchedCharactersPage,
        isLoading: isLoadingSearchedCharacters,
        size,
        setSize
    } = useClonesPagination(queryParamsSearch)

    function getURLParams(searchParams: ReadonlyURLSearchParams): string {
        const newParams = new URLSearchParams(searchParams.toString());
        newParams.delete("q")
        return `?${newParams.toString()}`;
    }

    useEffect(() => {
        if (ctx.searchInput === '') {
            router.push(ctx.lastPage + getURLParams(searchParams))
        }
    }, [ctx.searchInput])

    useEffect(() => {
        require('preline')
    }, [])

    useClosePrelineModal()

    return (
        <>
            <main className='w-full flex flex-col h-full'>
                <AuthModal />
                <RequestCloneModal />
                <CreatorProgramModal />
                <ScaleFadeIn loaded={true} duration={500}>
                    <CharacterGrid
                        characters={searchedCharacters}
                        loading={isLoadingSearchedCharacters}
                        fetchMoreData={() => setSize(size + 1)}
                        hasMoreData={!isLastSearchedCharactersPage}
                        handleClearSearchInput={() => {
                            // ?? timeout makes this work
                            setTimeout(() => {
                                ctx.setSearchInput("")
                                ctx.setIsInputActive(false)
                            }, 300)
                        }}
                    />
                </ScaleFadeIn>

            </main>
            <Footer />
        </>
    )
}
