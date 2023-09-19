'use client'
import HomePage from '@/components/HomePage'
import Footer from '@/components/Footer'
import { useSearchParams } from 'next/navigation'

export default function Home() {
  const searchParams = useSearchParams()
  const q = searchParams.get('q')


  return (
    <>
      <main className='w-full flex flex-col h-full'>
        <HomePage
          initialQ={q ?? ""}
        />

      </main>
      <Footer />
    </>
  )
}
