import { ReadonlyURLSearchParams, usePathname, useRouter, useSearchParams } from 'next/navigation';
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface SearchContextState {
    searchInput: string;
    setSearchInput: React.Dispatch<React.SetStateAction<string>>;
    isInputActive: boolean,
    setIsInputActive: React.Dispatch<React.SetStateAction<boolean>>;
    searchParam: string,
    setSearchParam: React.Dispatch<React.SetStateAction<string>>;
    lastPage: string
}

const MyContext = createContext<SearchContextState | undefined>(undefined);

interface SearchContextProviderProps {
    children: ReactNode;
    initialSearchInput?: string | null;
}

export const SearchContextProvider: React.FC<SearchContextProviderProps> = ({ children, initialSearchInput }) => {
    const router = useRouter()
    const searchParams = useSearchParams()
    const pathname = usePathname()

    const [searchInput, setSearchInput] = useState<string>(initialSearchInput || '');
    const [searchParam, setSearchParam] = useState(initialSearchInput || '')
    const [isInputActive, setIsInputActive] = useState(searchInput !== '')

    const duration = 500

    function updateUrlParams(searchParams: ReadonlyURLSearchParams, updateKey: string, updateValue: string): string {
        const newParams = new URLSearchParams(searchParams.toString());
        if (updateValue) {
            newParams.set(updateKey, updateValue);
        } else {
            newParams.delete(updateKey);
        }
        return `?${newParams.toString()}`;
    }

    const [lastPage, setLastPage] = useState<string>('/');

    useEffect(() => {
        if (pathname !== '/search')
            setLastPage(pathname)
    }, [pathname]);

    // useEffect(() => {
    //     if (searchInput !== '') {
    //         router.push('search' + updateUrlParams(searchParams, "q", searchInput))
    //     }
    // }, [searchInput]);

    useEffect(() => {
        const timer = setTimeout(() => {
            if (searchInput !== '') {
                setSearchParam(searchInput)
                router.push('search' + updateUrlParams(searchParams, "q", searchInput))
            }
        }, duration)
        return () => clearTimeout(timer)
    }, [searchInput])

    return (
        <MyContext.Provider value={{ searchInput, setSearchInput, isInputActive, setIsInputActive, searchParam, setSearchParam, lastPage }}>
            {children}
        </MyContext.Provider>
    );
};

export const useSearchContext = (): SearchContextState => {
    const context = useContext(MyContext);
    if (!context) {
        throw new Error('useSearchContext must be used within a SearchContextProvider');
    }
    return context;
};