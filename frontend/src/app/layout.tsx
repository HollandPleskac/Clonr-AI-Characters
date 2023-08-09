import './globals.css'
import 'regenerator-runtime/runtime'
import type { Metadata } from 'next'
import AuthModal from '@/components/AuthModal'
// import { Inter } from 'next/font/google'
// const inter = Inter({ subsets: ['latin'] })

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
        className='w-full bg-black lg:inline'
      >
        {children}
        
      </body>
    </html>
  )
}
