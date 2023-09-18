'use client'
import Image from 'next/image'
import Link from 'next/link'
import { Dispatch, SetStateAction, useState } from 'react'
import SelectedTag from './SelectedTag'
import { Tag } from '@/client'

export default function Multiselect({ selectedTags, addSelectedTag, removeSelectedTag, tags }:
    { selectedTags: Tag[], addSelectedTag: (tag: Tag) => void, removeSelectedTag: (tag: Tag) => void, tags: Tag[]|undefined }) {
    const [showDropdown, setShowDropdown] = useState(false)

    return (
        <div className="w-full flex flex-col items-center mx-auto">
            <div className="w-full ">
                <div className="flex flex-col items-center relative">
                    <div className="w-full  svelte-1l8159u">
                        <div className="p-1 flex border border-gray-200 bg-white rounded svelte-1l8159u">
                            <div className="flex flex-auto flex-wrap">
                            {selectedTags && selectedTags.length===0 && (
                                <p className='text-black text-gray-400 text-sm my-auto' >Tags</p>
                            )}
                                {selectedTags && selectedTags.map((tag, index) => {
                                    return <SelectedTag key={index} name={tag.name} deselect={() => removeSelectedTag(tag)} />
                                })}
                            </div>
                            <div
                                className="text-gray-300 w-8 py-1 pl-2 pr-1 border-l flex items-center border-gray-200 svelte-1l8159u"
                                onClick={() => {
                                    setShowDropdown(prevState => !prevState)
                                }}
                            >
                                {!showDropdown && (
                                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M6 15L12 9L18 15" stroke="#4b5563" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path> </g></svg>
                                )}
                                {showDropdown && (
                                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" transform="matrix(1, 0, 0, -1, 0, 0)"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M6 15L12 9L18 15" stroke="#4b5563" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path> </g></svg>
                                )}
                            </div>
                        </div>
                    </div>
                    <div className={`${showDropdown ? 'visible' : 'hidden'} absolute shadow top-full bg-white z-40 w-full lef-0 rounded max-h-[300px] overflow-y-auto svelte-5uyqqj`}>
                        <div className="flex flex-col w-full">

                            {tags && tags.map((tag, index) => {
                                const isChosenTag = selectedTags.some(selectedTag => selectedTag.name === tag.name);

                                return <div
                                    key={tag.id}
                                    className="cursor-pointer w-full border-gray-100 rounded-t border-b hover:bg-purple-100"
                                    onClick={() => {
                                        if (!isChosenTag)
                                            addSelectedTag(tag)
                                    }}
                                >
                                    <div className={`flex w-full items-center p-2 pl-2 border-transparent border-l-2 relative border-l-3 hover:border-purple-100 ${isChosenTag ? 'border-l-purple-400 hover:border-l-purple-400' : 'border-l-purple-100 hover:border-l-purple-100'}`}>
                                        <div className="w-full items-center flex">
                                            <div className="mx-2 leading-6  ">{tag.name}</div>
                                        </div>
                                    </div>
                                </div>
                            })}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
