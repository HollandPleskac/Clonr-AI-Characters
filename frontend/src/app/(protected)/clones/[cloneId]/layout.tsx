'use client'
import { useSession } from "next-auth/react"
import { redirect, useParams } from "next/navigation"

export default function Layout({
    children,
}: {
    children: React.ReactNode
}) {
    const params = useParams();

    const { data: session, status } = useSession({ required: true })
    const loading = status === "loading"

    if (loading) {
        return (
            <div > </div>
        )
    }

    if (!loading && !session) {
        return redirect("/login")
    }

    return (
        <div
        className='bg-gray-900 w-full flex justify-center items-center overflow-hidden'
        style={{ height: 'calc(100vh)' }}
      >
        {children}
      </div>
    )
}