'use client'

import React, { Ref } from 'react'
import ArrowLeftWhite from '@/svg/HomePage/arrow-left-white.svg'

interface DropdownProps {
    onItemClick: (value: string) => void;
    activeSort: string
}

const Dropdown: React.FC<DropdownProps> = ({ onItemClick, activeSort }) => {
    return (
        <div className="hs-dropdown relative inline-flex flex-grow flex-shrink-0">
            <button id="hs-dropdown-default" type="button" className="text-[#979797] h-[50px] hs-dropdown-toggle py-3 px-4 inline-flex justify-center items-center gap-2 rounded-md font-medium shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-600 transition-all text-sm bg-[#1E1E1E] hover:bg-[rgb(25,25,25)] text-gray-400 focus:ring-offset-gray-800">
                Sort: {activeSort}
                <svg className="hs-dropdown-open:rotate-180 w-2.5 h-2.5 text-gray-600" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M2 5L8.16086 10.6869C8.35239 10.8637 8.64761 10.8637 8.83914 10.6869L15 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
            </button>

            <div className="hs-dropdown-menu transition-[opacity,margin] duration-[0.1ms] hs-dropdown-open:opacity-100 opacity-0 w-[160px] hidden z-10 mt-2 min-w-[160px] bg-white shadow-md rounded-lg p-2 dark:bg-gray-800 dark:border dark:border-gray-700 dark:divide-gray-700" aria-labelledby="hs-dropdown-default">
                <button
                    onClick={onItemClick.bind(null, "Newest")}
                    className="w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300">
                    Newest
                </button>
                <button
                    onClick={onItemClick.bind(null, "Oldest")}
                    className="w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300">
                    Oldest
                </button>
                <button
                    onClick={onItemClick.bind(null, "Most Chats")}
                    className="w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300">
                    Most Chats
                </button>
                <button
                    onClick={onItemClick.bind(null, "Trending")}
                    className="w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300">
                    Trending
                </button>
                <button
                    onClick={onItemClick.bind(null, "Similarity")}
                    className="w-full flex items-center gap-x-3.5 py-2 px-3 rounded-md text-sm text-gray-800 hover:bg-gray-100 focus:ring-2 focus:ring-purple-500 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300">
                    Similarity
                </button>
            </div>
        </div>
    )
}

export default Dropdown
