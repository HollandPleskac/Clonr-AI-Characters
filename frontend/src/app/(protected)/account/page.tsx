'use client'
import Account from '@/components/Account'
import { useSession } from "next-auth/react"
import { redirect } from "next/navigation"


export default function AccountPage() {
  const { data: session, status } = useSession({ required: true })
    const loading = status === "loading"

    if (loading) {
        return (
            <div></div>
        )
    }

    if (!loading && !session) {
        return redirect("/login")
    }

    return <Account />
}

