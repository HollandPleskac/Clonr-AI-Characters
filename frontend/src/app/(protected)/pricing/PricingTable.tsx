'use client'

import axios from "axios"
import Script from "next/script"
import { useEffect } from "react"
import useSWR from "swr"
import { StripeService } from "@/client"

const NextStripePricingTable = () => {

  const fetcher = async (url: string): Promise<string> => {
    // const res = await axios.get(url, {
    //   withCredentials: true
    // })
    // return res.data
    const response = await StripeService.createCheckoutTokenStripeCheckoutTokenGet()
    return response.token
  }

  const { data: tokenData, isLoading, error } = useSWR('http://localhost:8000/stripe/checkout-token', fetcher);

  // Todo: redirect or error page with error page if cannot get tokenData.token
  return (
    <>
      <div className="min-h-[543px]" >
        {isLoading && <p>&nbsp;</p>}

        {(!isLoading && tokenData) && (
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