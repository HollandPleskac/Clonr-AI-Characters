'use client'

import BrowsePage from '@/components/BrowsePage'
import Footer from '@/components/Footer'
import { useQueryTags } from '@/hooks/useTags'
import { Tag } from '@/types'
import { usePathname, useSearchParams } from 'next/navigation'

export default function Browse() {
  const searchParams = useSearchParams()
  const pathname = usePathname()
  const q = searchParams.get('q')
  const tagName = searchParams.get('tag')
  const sort = searchParams.get('sort')

  // tags state
  const { data: tags, isLoading: isLoadingTags } = useQueryTags();

  function findActiveTag(tags:Tag[], tagName:string) {
    const activeTag = tags.find(tag => tag.name === tagName);
    return activeTag || null;
  }

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
        {(isLoadingTags || !tags)  && (
          <div className='h-screen w-full' >&nbsp;</div>
        )}
        {(!isLoadingTags && tags) && (
          <BrowsePage
            initialQ={q ?? ""}
            initialTag={findActiveTag(tags, tagName??"")}
            initialSort={getSortName(sort)}
            tags={tags}
          />
        )}

      </main>
      <Footer />
    </>
  )
}
