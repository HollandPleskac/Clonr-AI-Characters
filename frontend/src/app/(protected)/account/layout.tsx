'use client'
import { SessionProvider } from 'next-auth/react'
// import RootLayout from '../../layout'


export default function Layout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <SessionProvider>{children}</SessionProvider>
    )
}
