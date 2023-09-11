'use client'
import TopBarStatic from '../TopBarStatic'
import PricingTable from './PricingTable'
import Footer from '../Footer'
import { useEffect } from 'react'

export default function PricingScreen() {

  return (
    <>
    <main className='w-full flex flex-col h-full'>
        <TopBarStatic />
        <PricingTable />

      </main>
      <Footer />
      </>
  )
}
