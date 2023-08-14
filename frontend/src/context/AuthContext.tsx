// got from: https://stackoverflow.com/questions/72385641/supabase-onauthstatechanged-how-do-i-properly-wait-for-the-request-to-finish-p
import React, { createContext, useContext, useEffect, useState } from 'react'

import { useRouter } from 'next/router'

export const AuthContext = createContext<{
  user: string | null
  session: string | null
}>({
  user: null,
  session: null,
})

const AuthContextProvider = (props: any) => {
  const router = useRouter()
  const [userSession, setUserSession] = useState<string | null>(null)
  const [user, setUser] = useState<string | null>(null)

  useEffect(() => {
    
  }, [])

  const value = {
    userSession,
    user,
  }
  return <AuthContext.Provider value={value} {...props} />
}

export default AuthContextProvider