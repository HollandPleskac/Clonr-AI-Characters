'use client'

import AlertBar from "@/components/AlertBar"
import TopBar from "@/components/TopBar"
import { SearchContextProvider } from '@/context/searchContext'
import { useSearchParams } from "next/navigation"

export default function SearchWrapperLayout({
    children,
}: {
    children: React.ReactNode
}) {

    const searchParams = useSearchParams()
    const q = searchParams.get('q')

    return (
        <div>
            <SearchContextProvider initialSearchInput={q} >
                <AlertBar />    
                <TopBar />
                {children}
            </SearchContextProvider>
        </div>
    )
}
