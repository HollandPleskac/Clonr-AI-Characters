import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import Account from '@/components/Account'

export default async function AccountPage() {

  const cookieStore = cookies()
  const userCookie = cookieStore.get('fastapiusersauth')

  if (!userCookie) {
    redirect("/login")
  }
  return (
    <Account/>
  )
}
