import HomePage from '@/components/HomePage'
import Footer from '@/components/Footer'
export default async function Home() {

  return (
    <>
      <main className='w-full flex flex-col h-full'>
        <HomePage
        />
        
      </main>
      <Footer />
    </>
  )
}
