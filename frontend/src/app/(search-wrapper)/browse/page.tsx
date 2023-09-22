'use client'

import BrowsePage from '@/components/BrowsePage'
import Footer from '@/components/Footer'
import { useSearchParams } from 'next/navigation'

export default function Browse() {
  const searchParams = useSearchParams()
  const tagName = searchParams.get('tag')
  const sort = searchParams.get('sort')

  function getSortName(sort:string|null) {
    const validSortNames = ["Trending", "Newest", "Oldest", "Most Chats", "Similarity"];
    if (sort && validSortNames.includes(sort)) {
        return sort;
    }
    return "Trending";
  }


  return (
    <>
      <main className='w-full flex flex-col h-full'>
          <BrowsePage
            initialTagName={tagName||""}
            initialSort={getSortName(sort)}
          />

      </main>
      <Footer />
    </>
  )
}
