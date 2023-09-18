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
        <div className="w-1/2 grid items-center bg-gradient-to-r from-gray-800 via-gray-900 to-[#141414]" >
          <div className="flex flex-col items-center w-full">
            <p className='text-white text-4xl font-thin text-center'><span className="text-5xl">Join the future</span> of socializing </p>
            <p className="text-white text-opacity-60 mt-4 text-center">A world of limitless possibility starts here 🌎</p>
          </div>

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