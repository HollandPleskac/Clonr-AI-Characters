import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import Account from '@/components/Account'

export default async function AccountPage() {

  const cookieStore = cookies()
  console.log("COOOKIE STORE", cookieStore)
  const userCookie = cookieStore.get('clonrauth')

  if (!userCookie) {
    redirect("/login")
  }
  return (
    <Account/>
  )
}
