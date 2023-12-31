'use client'
import TopBarStatic from '../TopBarStatic'
import PricingTable from './PricingTable'
import Footer from '../Footer'
import { useEffect } from 'react'
import { useClosePrelineModal } from '@/hooks/useClosePrelineModal'
import AuthModal from '../Modal/AuthModal'
import CreatorProgramModal from '../Modal/CreatorProgramModal'

export default function PricingScreen() {

  useEffect(() => {
    require('preline')
  }, [])

  useClosePrelineModal()

  return (
    <>
      <main className='w-full flex flex-col h-full'>
        <CreatorProgramModal/>
        <TopBarStatic />
        <PricingTable />

      </main>
      <Footer />
    </>
  )
}
