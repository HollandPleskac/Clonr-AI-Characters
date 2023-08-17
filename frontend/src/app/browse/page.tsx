'use client'

import BrowsePage from '@/components/BrowsePage'
import PlusModal from '@/components/PlusModal'
import { carouselData } from '@/data/carouselData'
import Footer from '@/components/Footer'
import AuthModal from '@/components/AuthModal'
import useClones from '@/hooks/useClones'

async function fetchCharacters() {
  return carouselData
}

export default async function Browse() {
  const { queryClones, queryCloneById } = useClones()

  // TODO: edit
  const queryParams = {}
  const characters = await queryClones(queryParams)

  return (
    <>
      <main className='w-full flex flex-col h-full'>
        <BrowsePage
          initialCharacters={characters}
        />
        
      </main>
      <Footer />
    </>
  )
}
