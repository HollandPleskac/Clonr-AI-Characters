'use client'
import Footer from '@/components/Footer'
import TopBarStatic from '@/components/TopBarStatic'
import Image from 'next/image'
import Link from 'next/link'

export default function CreatorPartnerProgram() {

  function scrollToElement(selector) {
    console.log("selector", selector)
    const element = document.getElementById(selector);
    console.log("el", element)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  }

  return (
    <>
      <main className='w-full flex flex-col h-full'>
        <TopBarStatic />
        <div className='mt-24 md:max-w-screen-sm lg:max-w-[992px] px-4 sm:px-6 lg:px-8 pb-12 md:pt-6 sm:pb-20 mx-auto'>
          <div className='flex items-center mb-6'>
            <div className='h-[28px] w-[28px] relative'>
              <Image
                src='/clonr-logo.png'
                alt='logo'
                layout='fill'
                objectFit='cover'
                className=''
              />
            </div>
            <h3 className='ml-2 text-[28px] font-semibold leading-5 text-white font-fabada'>
              clonr
            </h3>
          </div>
          <h1 className='text-2xl font-bold md:text-4xl text-white mb-4'>
            Partner Program
          </h1>
          <div>
            <p className='mb-5 text-gray-400'>
              Welcome to the Egirls.ai Partner Program! Join us in the digital revolution that is empowering creators worldwide
            </p>
          </div>
          <div className='my-[64px] font-bold' >
            <h3 className='text-xl md:text-3xl text-white mb-8'>
              On this page:
            </h3>
            <button onClick={() => {
              scrollToElement("#benefits")
            }}
              className='block text-purple-400 mb-2' >1. Benefits of Joining the Partner Program
            </button>
            <button
              onClick={() => {
                scrollToElement("#how-it-works")
              }}
              className='block text-purple-400 mb-2' >2. How it works
            </button>
            <button
              onClick={() => {
                scrollToElement("#for-creators-with-digital-persona")
              }}
              className='block text-purple-400 mb-2' >3. For creators with an existing digital persona
            </button>
            <button
              onClick={() => {
                scrollToElement("#for-creators-without-digital-persona")
              }}
              className='block text-purple-400 mb-2' >4. For creators without an existing digital persona
            </button>
          </div>

          <div className='grid gap-4 md:gap-8'>

            <div>
              <h3 className='font-bold text-xl md:text-3xl text-white mb-8' id='#benefits' >
                Benefits of Joining the Partner Program:
              </h3>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                1. Fully custom images & voice:
              </h2>

              <p className='text-gray-400'>
                In addition to uploading photos, influencers can also upload voice files to train AI models to emulate their voices accurately. Whether you have a distinct vocal tone or a unique accent, this feature allows you to recreate your voice in an AI model, providing an immersive experience for your audience.
              </p>
            </div>

            <div>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                2. Higher revenue split:
              </h2>

              <p className='text-gray-400'>
                We believe in recognizing the value that talented creators bring to the platform. Partnered creators will earn a higher revenue split (50/50).
              </p>
            </div>

            <div>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                3. Priority support:
              </h2>

              <p className='text-gray-400'>
                You gain access to a dedicated support team that is committed to addressing your needs promptly and efficiently. Whether you have technical questions, need assistance with customization, or require guidance in maximizing your AI models' potential, our support team ensures that you receive personalized attention and solutions.              </p>
            </div>

            <div>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                4. Partner-only opportunities:
              </h2>

              <p className='text-gray-400'>
                We believe in recognizing the value that talented creators bring to the platform. Partnered creators will earn a higher revenue split (50/50).
              </p>
            </div>

            <div>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                5. Community
              </h2>

              <p className='text-gray-400'>
                Egirls.ai is more than just a platform—it's a vibrant community of creators. By joining the partner program, you gain access to a network of creative individuals who are passionate about AI modeling. Engage in discussions, share insights, and collaborate with fellow partnered creators in              </p>
            </div>

          </div>

          <div className='grid gap-4 md:gap-8 mt-[64px]'>

            <div>
              <h3 className='font-bold text-xl md:text-3xl text-white mb-8' id="#how-it-works" >
                How it Works:
              </h3>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                1. Apply to the Partner Program:
              </h2>

              <p className='text-gray-400'>
                Visit <span className='text-purple-400' >https://www.Egirls.ai/partner-program</span> and submit your application to join the partner program. The Egirls.ai team will review your application and notify you once your application is accepted.              </p>
            </div>

            <div>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                2. Upload Photos and Voice Files:
              </h2>

              <p className='text-gray-400'>
                Once accepted, you can start uploading your own photos and voice files. These will be used to train AI models that will emulate your appearance and voice accurately.              </p>
            </div>

            <div>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                3. Customize Your AI Models:
              </h2>

              <p className='text-gray-400'>
                You gain access to a dedicated support team that is committed to addressing your needs promptly and efficiently. Whether you have technical questions, need assistance with customization, or require guidance in maximizing your AI models' potential, our support team ensures that you receive personalized attention and solutions.
              </p>
            </div>

            <div>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                4. Engage with the Creator Community:
              </h2>

              <p className='text-gray-400'>
                Interact with other creators within the Egirls.ai community. Participate in discussions, share your experiences, and collaborate to enhance your AI modeling skills and discover new possibilities.
              </p>
            </div>

            <div>
              <h2 className='text-lg sm:text-xl font-semibold mb-2 text-white'>
                5. Engage with your audience:
              </h2>

              <p className='text-gray-400'>
                Create and post content that will captivate your fans. Use our analytics tools to see which content is working for you, iterate with ease.
              </p>
            </div>

          </div>

          <div className='grid gap-4 md:gap-8 mt-[64px]'>
            <div>
              <h3 className='font-bold text-xl md:text-3xl text-white mb-8' id="#for-creators-with-digital-persona" >
                For creators with an existing digital persona  </h3>
              <ul>

                <li className='text-gray-400 mb-2' >
                  • Partnering with Egirls allows you to build an AI version of yourself or your digital digital persona
                </li>
                <li className='text-gray-400' >
                  • Tap into our state of the art machine learning models, and build an amazing experience for your fans
                </li>
              </ul>
            </div>
          </div>

          <div className='grid gap-4 md:gap-8 mt-[64px]'>
            <div>
              <h3 className='font-bold text-xl md:text-3xl text-white mb-8' id="#for-creators-without-digital-persona" >
                For creators without an existing digital persona
              </h3>
              <ul>

                <li className='text-gray-400 mb-2' >
                  • Partnering with Egirls allows you to create novel persona’s and characters
                </li>
                <li className='text-gray-400' >
                  • Build an Egirl from scratch right on our platform, having every tool we offer at your disposal
                </li>
              </ul>
            </div>
          </div>


        </div>
      </main>
      <Footer />
    </>
  )
}
