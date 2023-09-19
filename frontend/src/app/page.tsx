'use client'
import HomePage from '@/components/HomePage'
import Footer from '@/components/Footer'
import { ReadonlyURLSearchParams, usePathname, useRouter, useSearchParams } from 'next/navigation'

export default function Home() {
  const searchParams = useSearchParams()
  const pathname = usePathname()
  const q = searchParams.get('q')


  return (
    <>
      <main className='w-full flex flex-col h-full'>
        <button className=' text-white p-4 border border-white' onClick={() => {
          console.log("push pathname", pathname)
          
        }} >CLICKME</button>
        <HomePage
          initialQ={q ?? ""}
        />

      </main>
      <Footer />
    </>
  )
}
