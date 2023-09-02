'use client'

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

export function useAuth() {
  const { data: session, status } = useSession();
  const loading = status === "loading";

  return { session, loading };
}