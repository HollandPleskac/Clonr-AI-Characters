import Footer from '@/components/Footer'
import TopBarStatic from '@/components/TopBarStatic'

export default async function PrivacyPage() {
  return (
    <>
      <main className='w-full flex flex-col h-full'>
        <TopBarStatic />
        <div className='md:max-w-screen-sm text-center px-4 sm:px-6 lg:px-8 pt-24 pb-6 mx-auto'>
          <h1 className='text-2xl font-bold md:text-4xl text-white'>
            Privacy &amp; Policy
          </h1>
        </div>
        <div className='md:max-w-screen-sm lg:max-w-[992px] px-4 sm:px-6 lg:px-8 pb-12 md:pt-6 sm:pb-20 mx-auto'>
          <div className='grid gap-4 md:gap-8'>
            <div>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                Our Privacy Policy
              </h2>

              <p className='mb-5 text-gray-400'>
                Preline does not share personal information of any kind with
                anyone. We will not sell or rent your name or personal
                information to any third party. We DO NOT sell, rent or provide
                outside access to our mailing list or any data we store. Any
                data that a user stores via our facilities is wholly owned by
                that user or business. At any time a user or business is free to
                take their data and leave, or to simply delete their data from
                our facilities.
              </p>

              <p className='mb-5 text-gray-400'>
                Preline only collects such personal information that is
                necessary for you to access and use our services. This personal
                information includes, but is not limited to, first and last
                name, email address and other personal information necessary to
                generate proper legal documents.
              </p>

              <p className='text-gray-400'>
                Preline may release personal information if Preline is required
                to by law, search warrant, subpoena, court order or fraud
                investigation. We may also use personal information in a manner
                that does not identify you specifically nor allow you to be
                contacted but does identify certain criteria about our Site&apos;s
                users in general (such as we may inform third parties about the
                number of registered users, number of unique visitors, and the
                pages most frequently browsed).
              </p>
            </div>

            <div>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                Privacy Changes
              </h2>

              <p className='text-gray-400'>
                If we change our privacy policy we will post those changes on
                this page. Registered users will be sent an email that outlines
                changes made to the privacy policy.
              </p>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}
