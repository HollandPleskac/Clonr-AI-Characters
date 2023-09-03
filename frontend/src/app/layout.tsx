import './globals.css'
import 'regenerator-runtime/runtime'
import type { Metadata } from 'next'
// import { Inter } from 'next/font/google'
// const inter = Inter({ subsets: ['latin'] })
import NextAuthProvider from '@/auth/Providers'

export const metadata: Metadata = {
  title: 'Clonr',
  description: 'Advanced clones or people, real and fictional',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang='en'>
      <body
        // className={inter.className}
        className='w-full bg-[#141414] lg:inline'
      >
        <NextAuthProvider>
          {children}
        </NextAuthProvider>

      </body>
    </html>
  )
}