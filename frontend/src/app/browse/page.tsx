import BrowsePage from '@/components/BrowsePage'
import PlusModal from '@/components/PlusModal'
import { carouselData } from '@/data/carouselData'
import Footer from '@/components/Footer'
import AuthModal from '@/components/AuthModal'

async function fetchCharacters() {
  return carouselData
}

export default async function Browse() {
  const [characters] = await Promise.all([
    fetchCharacters()
  ])

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
