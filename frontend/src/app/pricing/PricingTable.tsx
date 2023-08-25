'use client'

import Script from "next/script"

const NextStripePricingTable = () => {
  return (
    <>
      {/* <Script async strategy="lazyOnload" src="https://js.stripe.com/v3/pricing-table.js" /> */}
      {/* <stripe-pricing-table
        pricing-table-id="prctbl_1NihCICJiKhdlW4vUJAadYuv"
        publishable-key="pk_test_51NiAqMCJiKhdlW4vSWdNiuLoIPGcaXZGL8lAP7eR4CCNSnJYODauUTKORQd1WqiNIeKwpawzonb1vBH9LRr17Qbf00hOXX52tV"
        client-reference-id="clientReferenceId"
      /> */}
      {/* <stripe-pricing-table
        pricing-table-id="prctbl_1NihCICJiKhdlW4vUJAadYuv"
        publishable-key="pk_test_51NiAqMCJiKhdlW4vSWdNiuLoIPGcaXZGL8lAP7eR4CCNSnJYODauUTKORQd1WqiNIeKwpawzonb1vBH9LRr17Qbf00hOXX52tV">
      </stripe-pricing-table> */}

      <div className="min-h-[543px]" >
        <Script async
          // strategy='lazyOnload'
          src="https://js.stripe.com/v3/pricing-table.js" />
        <stripe-pricing-table pricing-table-id="prctbl_1NihCICJiKhdlW4vUJAadYuv"
          publishable-key="pk_test_51NiAqMCJiKhdlW4vSWdNiuLoIPGcaXZGL8lAP7eR4CCNSnJYODauUTKORQd1WqiNIeKwpawzonb1vBH9LRr17Qbf00hOXX52tV">
        </stripe-pricing-table >
      </div>
    </>
  )
}

export default NextStripePricingTable