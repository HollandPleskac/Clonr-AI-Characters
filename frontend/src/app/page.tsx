import HomePage from '@/components/HomePage'
import PlusModal from '@/components/PlusModal'
import { carouselData } from '@/data/carouselData'
import Footer from '@/components/Footer'
import AuthModal from '@/components/AuthModal'

async function fetchCharacters() {
  return carouselData
}

export default async function Home() {
  const [topCharacters, continueChatting, trending, anime] = await Promise.all([
    fetchCharacters(),
    fetchCharacters(),
    fetchCharacters(),
    fetchCharacters(),
  ])

  return (
    <>
      <main className='w-full flex flex-col h-full'>
        <HomePage
          topCharacters={topCharacters}
          continueChatting={continueChatting}
          trending={trending}
          anime={anime}
        />
        <AuthModal />
      </main>
      <Footer />
    </>
  )
}
