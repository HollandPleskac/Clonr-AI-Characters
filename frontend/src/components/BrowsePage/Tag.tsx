'use client'

import React, { Ref } from 'react'
import ArrowLeftWhite from '@/svg/HomePage/arrow-left-white.svg'

interface TagProps {
    name: string
    onClick: (tagName: string | null) => void
    active: boolean
}

const Tag: React.FC<TagProps> = ({ name, onClick, active }) => {
    const handleClick = () => {
        onClick(active ? null : name);
    };

    return (
        <button className={`${active && 'bg-gray-600 border-gray-600'} h-full text-sm text-gray-300 px-4 py-2 font-semibold rounded-lg border border-gray-700 hover:border-gray-600 bg-black hover:bg-gray-600 transition duration-200`}
            onClick={handleClick}
        >
            {name}
        </button>
    )
}

export default Tag
