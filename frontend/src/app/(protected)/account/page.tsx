import { redirect } from 'next/navigation'
import Account from '@/components/Account'
import { cookies } from 'next/headers'
import cookiesToString from '@/utils/cookiesToString'


export default async function AccountPage() {
  console.log("status")
  const isAuthenticated = await getAuthStatus()
  console.log("status", isAuthenticated)

  if (!isAuthenticated) {
    redirect("/login")
  }
  return (
    <Account />
  )
}


// Return Character based on characterId
async function getAuthStatus(): Promise<boolean> {
  // look at auth gen function for this
  const cookieStore = cookies()
  const all = cookieStore.getAll()
  console.log("all::::::::::::",all)
  console.log("cookies",cookiesToString(all))
  try {
    const res = await fetch(`http://localhost:8000/users/me`, {
    cache: 'no-store',
    method: 'GET',
    headers: {
      'Cookie': cookiesToString(cookieStore.getAll())
    },
    credentials: 'include'
  });
  return true
  } catch(e) {
    console.log("error",e)
    return true
  }

  return true
}