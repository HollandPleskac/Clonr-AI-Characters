'use client'

import BrowsePage from '@/components/BrowsePage'
import Footer from '@/components/Footer'
import { usePathname, useSearchParams } from 'next/navigation'

export default function Browse() {
  const searchParams = useSearchParams()
  const pathname = usePathname()
  const q = searchParams.get('q')
  const tagName = searchParams.get('tag')
  const sort = searchParams.get('sort')

  // get initialTag from the name

  return (
    <>
      <main className='w-full flex flex-col h-full'>
        <BrowsePage
          initialQ={q ?? ""}
          initialTag={null}
          initialSort={sort ?? "Trending"}
        />

      </main>
      <Footer />
    </>
  )
}
