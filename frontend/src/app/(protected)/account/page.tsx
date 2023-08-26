//import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import Account from '@/components/Account'
import Cookies from 'js-cookie';



export default async function AccountPage() {

  //const cookieStore = cookies()
  //console.log("COOOKIE STORE", cookieStore)
  //const userCookie = cookieStore.get('clonrauth')

  const userCookie = Cookies.get('clonrauth')

  if (!userCookie) {
    redirect("/login")
  }
  return (
    <Account/>
  )
}
