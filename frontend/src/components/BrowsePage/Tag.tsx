'use client'

import React, { Ref } from 'react'
import ArrowLeftWhite from '@/svg/HomePage/arrow-left-white.svg'

interface TagProps {
    name: string
    onClick: () => void
    active: boolean
}

const Tag: React.FC<TagProps> = ({ name, onClick, active }) => {
    return (
        <button className={`${active && 'bg-gray-600 border-gray-600'} text-gray-300 px-3 py-2 font-semibold rounded-lg border border-gray-700 hover:border-gray-600 bg-black hover:bg-gray-600 transition duration-200`}
            onClick={onClick}
        >
            {name}
        </button>
    )
}

export default Tag