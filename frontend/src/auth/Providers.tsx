"use client";

import { SessionProvider } from "next-auth/react";
import posthog from 'posthog-js';
import { usePathname, useSearchParams } from "next/navigation";
import { useEffect } from "react";

type Props = {
  children?: React.ReactNode;
};

export default function NextAuthProvider ({ children }: Props) {
  const posthogApiKey = process.env.NEXT_PUBLIC_POSTHOG_API_KEY;
  posthog.init(posthogApiKey ? posthogApiKey : '', 
    { api_host: 'https://app.posthog.com' }
  )

  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    const pageIdentifier = `${pathname}${searchParams.toString()}`;
    const devMode = process.env.NODE_ENV === 'development';

    if (devMode) {
      console.log("skipping posthog captures");
    } else {
      posthog.capture("$pageview", {
        page_identifier: pageIdentifier,
      });
    }
    
  }, [pathname, searchParams]);

  return <SessionProvider>{children}</SessionProvider>;
};