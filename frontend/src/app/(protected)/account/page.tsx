'use client'
import Account from '@/components/Account'
import { useSession } from "next-auth/react"


export default function AccountPage() {
  const { data: session, status } = useSession({required: true})
  const loading = status === "loading"

  if (loading) {
    return (
      <div className='text-white' ></div>
    )
  }
  if (!loading && session) {
    return (
      <Account />
    )
  }
}