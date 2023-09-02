"use client"
import React from 'react'
import FireflyBackground from '@/components/Auth/FireflyBackground'
import LoginModal from '@/components/Auth/Login'
import { useSession } from 'next-auth/react'
import { redirect } from 'next/navigation'


export default function Login() {
 const { data: session, status} = useSession({ required: false })

  if (status === "loading") {
    return <p></p>
  }

  if (status === "authenticated") {
    redirect('/')
  }
  return (
    <FireflyBackground>
      <LoginModal />
    </FireflyBackground>
  )
}
