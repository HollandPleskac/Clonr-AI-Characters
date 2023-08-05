import './globals.css'
import type { Metadata } from 'next'
// import { Inter } from 'next/font/google'
// const inter = Inter({ subsets: ['latin'] })
import Footer from '@/components/Footer'


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
        <Footer />
      </body>
    </html>
  )
}
