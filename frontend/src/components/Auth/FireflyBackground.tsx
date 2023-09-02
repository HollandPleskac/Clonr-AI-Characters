'use client'
import React from 'react'
import styles from '@/styles/Firefly.module.sass'
import TopBarStatic from '@/components/TopBarStatic'


const FireflyBackground = ({ children }) => {
  return (
    <main className='bg-black h-screen overflow-y-hidden flex flex-col'>
      {Array.from({ length: 200 }).map((_, i) => (
        <div key={i} className={styles.firefly} />
      ))}
      {/* <TopBarStatic /> */}
      <div className='flex justify-center items-center h-full'>
          <div className='mx-auto bg-opacity-0 relative w-full max-w-md px-4 h-full md:h-auto'>
            {children}
        </div>
      </div>
    </main>
  )
}

export default FireflyBackground