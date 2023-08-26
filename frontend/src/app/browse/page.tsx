'use client'

import { useState, useEffect } from 'react'
import BrowsePage from '@/components/BrowsePage'
import PlusModal from '@/components/PlusModal'
import { carouselData } from '@/data/carouselData'
import Footer from '@/components/Footer'
import AuthModal from '@/components/AuthModal'
import { useQueryClones } from '@/hooks/useClones'

async function fetchCharacters() {
  return carouselData
}

export default function Browse() {
  const [characters, setCharacters] = useState([])

  const queryParams = {
    sort: 'top',
    offset: 0,
    limit: 20
  }
  const {data, error, isLoading} = useQueryClones(queryParams);

  useEffect(() => {
    if(!isLoading && data) {
      setCharacters(data)
    }
  }, [data])

  if (isLoading || !characters || characters.length === 0) {
    return <div>Loading...</div>
  }

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
