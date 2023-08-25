import Footer from '@/components/Footer'
import TopBarStatic from '@/components/TopBarStatic'
import { loadStripe } from '@stripe/stripe-js';
import PricingTable from './PricingTable'
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default function PrivacyPage({
  params,
}: {
  params: { characterId: string; conversationId: string }
}) {

  // Route Protection
  const cookieStore = cookies()
  const userCookie = cookieStore.get('fastapiusersauth')

  if (!userCookie) {
    redirect("/login")
  }

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
