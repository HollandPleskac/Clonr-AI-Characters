import Counter from "@/utils/Counter"
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";


type SuggestionBarProps = {
    tags: string[],
    topP?: number
    handleClearSearchInput?: () => void
}

export default function SuggestionBar({tags, topP = 0.5, handleClearSearchInput}: SuggestionBarProps) {
    const pathname = usePathname()
    const router = useRouter()
    
    if (!tags || tags.length < 10) {
        return null
    }
    const N = tags.length;
    let threshold = Math.round(topP * N);
    let counter = new Counter<string>(tags);
    // let topTags: [string, number][] = [];
    let topTags: string[] = [];
    for (const [k, v] of counter.mostCommon()) {
        threshold -= v;
        if (threshold < 0) {
            break
        }
        topTags.push(k)
    }
    if (!topTags || topTags.length < 1) {
        return null
    }
    return (
        <div className="ml-[4%] mb-[20px] w-full flex flex-initial items-center justify-start">
            <h2 className="text-white opacity-50 text-sm">
                Explore clones related to:
            </h2>
            <ul className="flex">
                {
                    topTags.map((value, index) =>
                    (
                        <li key={index} className={`border-white border-opacity-50 px-2 py-1 hover:cursor-pointer ${index > 0 ? "border-l-[1px]" : ""}`}>
                            <button className="text-white text-opacity-90 text-sm hover:text-opacity-75" onClick={() => {
                                router.push(`/browse?tag=${value}`)
                                if (handleClearSearchInput) {
                                    handleClearSearchInput()
                                }
                            }}>
                                {value}
                            </button>
                        </li>
                        )
                    )
                }
            </ul>
        </div>
    )
}
