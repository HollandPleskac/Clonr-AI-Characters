'use client'

import Script from "next/script"
import useSWR from "swr"
import { StripeService } from "@/client"
import { useEffect } from "react"
import { useClosePrelineModal } from "@/hooks/useClosePrelineModal"

const NextStripePricingTable = () => {
  
  const { data: tokenData, isLoading, error } = useSWR('fetchToken', StripeService.createCheckoutTokenStripeCheckoutTokenGet);

  useClosePrelineModal()

  // Todo: redirect or error page with error page if cannot get tokenData.token
  return (
    <>
      <div className="min-h-[543px]" >
        {isLoading && <p>&nbsp;</p>}

        {(!isLoading && tokenData && tokenData.token.length > 10) && (
          <>
            <Script async
              // strategy='lazyOnload'
              src="https://js.stripe.com/v3/pricing-table.js" />
            <stripe-pricing-table
              pricing-table-id="prctbl_1NjE5FCJiKhdlW4viHW5r3Vt"
              publishable-key="pk_test_51NiAqMCJiKhdlW4vSWdNiuLoIPGcaXZGL8lAP7eR4CCNSnJYODauUTKORQd1WqiNIeKwpawzonb1vBH9LRr17Qbf00hOXX52tV"
              client-reference-id={tokenData.token}
            >
            </stripe-pricing-table >
          </>
        )}
      </div>
    </>
  )
}

export default NextStripePricingTable