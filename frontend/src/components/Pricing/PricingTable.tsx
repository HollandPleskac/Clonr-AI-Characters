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
      <div className="flex" >
        <div className="w-1/2 grid place-items-center bg-gray-700" >
        <h1 className='text-4xl'> <span className='font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-700 '>Clonr Pricing</span></h1>

        </div>
        <div className="min-h-[543px] w-1/2 flex flex-col justify-center" >
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
      </div>
    </>
  )
}

export default NextStripePricingTable