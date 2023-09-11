import Footer from '@/components/Footer'
import PricingTable from '@/components/Pricing/PricingTable'
import TopBarStatic from '@/components/TopBarStatic'

export default async function PricingPage() {

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
