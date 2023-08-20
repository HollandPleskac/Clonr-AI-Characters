'use client';

import Link from 'next/link'
import React from 'react'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useOAuth } from '../hooks/useOAuth'

const AuthPopup = () => {
  const router = useRouter()
  const [isSignIn, setIsSignIn] = React.useState(true)
  const [oauthCode, setOAuthCode] = useState<string | null>(null);

  const { user: googleUser, authError: googleAuthError, loginWithOAuth: loginWithGoogleOAuth, handleOAuthCallback: handleGoogleOAuthCallback } = useOAuth({
    provider: 'Google',
    authorizeUrl: 'http://localhost:8000/auth/google/authorize',
    callbackUrl: 'http://localhost:8000/auth/google/callback',
  });

  const { user: discordUser, authError: discordAuthError, loginWithOAuth: loginWithDiscordOAuth, handleOAuthCallback: handleDiscordOAuthCallback } = useOAuth({
    provider: 'Discord',
    authorizeUrl: 'http://localhost:8000/auth/discord/authorize',
    callbackUrl: 'http://localhost:8000/auth/discord/callback',
  });

  const { user: facebookUser, authError: facebookAuthError, loginWithOAuth: loginWithFacebookOAuth, handleOAuthCallback: handleFacebookOAuthCallback } = useOAuth({
    provider: 'Facebook',
    authorizeUrl: 'http://localhost:8000/auth/facebook/authorize',
    callbackUrl: 'http://localhost:8000/auth/facebook/callback',
  });

  const { user: redditUser, authError: redditAuthError, loginWithOAuth: loginWithRedditOAuth, handleOAuthCallback: handleRedditOAuthCallback } = useOAuth({
    provider: 'Reddit',
    authorizeUrl: 'http://localhost:8000/auth/reddit/authorize',
    callbackUrl: 'http://localhost:8000/auth/reddit/callback',
  });

  useEffect(() => {
    // TODO: edit
    const url = new URL(window.location.href);
    const code = url.searchParams.get('code');
    if (code) {
      const provider = url.searchParams.get('provider');
      if (provider === 'google') {
        handleGoogleOAuthCallback(code);
      } else if (provider === 'discord') {
        handleDiscordOAuthCallback(code);
      } else if (provider === 'facebook') {
        handleFacebookOAuthCallback(code);
      } else if (provider === 'reddit') {
        handleRedditOAuthCallback(code);
      } else {
        console.error('Unknown OAuth provider');
      }
    }
  }, []);

  return (
    <div className='p-4 sm:p-7'>
      <div className='text-center'>
        <h1 className='mb-2 block text-2xl font-bold text-gray-800 dark:text-white'>
          {isSignIn && 'Sign in to Clonr'}
          {!isSignIn && 'Sign up for Clonr'}
        </h1>
      </div>

      <div className='mt-5 flex flex-col gap-y-4 '>
        {!isSignIn && (
          <div className='flex items-center justify-center'>
            <div className='flex items-center h-5'>
              <input
                id='remember'
                aria-describedby='remember'
                type='checkbox'
                className='w-4 h-4 border focus:ring-transparent border-gray-300 rounded bg-gray-50  dark:bg-gray-700 dark:border-gray-600  checked:text-purple-500'
                required={false}
                style={{ boxShadow: 'none' }}
              />
            </div>
            <div className='ml-3 text-sm'>
              <label
                htmlFor='terms'
                className='font-light text-gray-500 dark:text-gray-300'
              >
                I accept the{' '}
                <a
                  className='font-medium text-purple-600 hover:underline dark:text-purple-500'
                  href='#'
                >
                  Terms and Conditions
                </a>
              </label>
            </div>
          </div>
        )}
        <button
          onClick={loginWithGoogleOAuth}
          type='button'
          className='w-full py-3 px-4 inline-flex justify-center items-center gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-600 transition-all text-sm bg-gray-800 hover:bg-slate-800 dark:border-gray-700 text-gray-400 hover:text-white focus:ring-offset-gray-800'
        >
          <svg
            className='w-5 h-auto'
            width='46'
            height='47'
            viewBox='0 0 46 47'
            fill='none'
          >
            <path
              d='M46 24.0287C46 22.09 45.8533 20.68 45.5013 19.2112H23.4694V27.9356H36.4069C36.1429 30.1094 34.7347 33.37 31.5957 35.5731L31.5663 35.8669L38.5191 41.2719L38.9885 41.3306C43.4477 37.2181 46 31.1669 46 24.0287Z'
              fill='#4285F4'
            />
            <path
              d='M23.4694 47C29.8061 47 35.1161 44.9144 39.0179 41.3012L31.625 35.5437C29.6301 36.9244 26.9898 37.8937 23.4987 37.8937C17.2793 37.8937 12.0281 33.7812 10.1505 28.1412L9.88649 28.1706L2.61097 33.7812L2.52296 34.0456C6.36608 41.7125 14.287 47 23.4694 47Z'
              fill='#34A853'
            />
            <path
              d='M10.1212 28.1413C9.62245 26.6725 9.32908 25.1156 9.32908 23.5C9.32908 21.8844 9.62245 20.3275 10.0918 18.8588V18.5356L2.75765 12.8369L2.52296 12.9544C0.909439 16.1269 0 19.7106 0 23.5C0 27.2894 0.909439 30.8731 2.49362 34.0456L10.1212 28.1413Z'
              fill='#FBBC05'
            />
            <path
              d='M23.4694 9.07688C27.8699 9.07688 30.8622 10.9863 32.5344 12.5725L39.1645 6.11C35.0867 2.32063 29.8061 0 23.4694 0C14.287 0 6.36607 5.2875 2.49362 12.9544L10.0918 18.8588C11.9987 13.1894 17.25 9.07688 23.4694 9.07688Z'
              fill='#EB4335'
            />
          </svg>
          Google
        </button>

        <button
          onClick={loginWithDiscordOAuth}
          type='button'
          className='w-full py-3 px-4 inline-flex justify-center items-center gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-600 transition-all text-sm bg-gray-800 hover:bg-slate-800 dark:border-gray-700 text-gray-400 hover:text-white focus:ring-offset-gray-800'
        >
          <svg
            fill='#5661F7'
            width='800px'
            height='800px'
            viewBox='0 0 32 32'
            version='1.1'
            xmlns='http://www.w3.org/2000/svg'
            className='w-5 h-auto'
          >
            <title>discord</title>
            <path d='M20.992 20.163c-1.511-0.099-2.699-1.349-2.699-2.877 0-0.051 0.001-0.102 0.004-0.153l-0 0.007c-0.003-0.048-0.005-0.104-0.005-0.161 0-1.525 1.19-2.771 2.692-2.862l0.008-0c1.509 0.082 2.701 1.325 2.701 2.847 0 0.062-0.002 0.123-0.006 0.184l0-0.008c0.003 0.050 0.005 0.109 0.005 0.168 0 1.523-1.191 2.768-2.693 2.854l-0.008 0zM11.026 20.163c-1.511-0.099-2.699-1.349-2.699-2.877 0-0.051 0.001-0.102 0.004-0.153l-0 0.007c-0.003-0.048-0.005-0.104-0.005-0.161 0-1.525 1.19-2.771 2.692-2.862l0.008-0c1.509 0.082 2.701 1.325 2.701 2.847 0 0.062-0.002 0.123-0.006 0.184l0-0.008c0.003 0.048 0.005 0.104 0.005 0.161 0 1.525-1.19 2.771-2.692 2.862l-0.008 0zM26.393 6.465c-1.763-0.832-3.811-1.49-5.955-1.871l-0.149-0.022c-0.005-0.001-0.011-0.002-0.017-0.002-0.035 0-0.065 0.019-0.081 0.047l-0 0c-0.234 0.411-0.488 0.924-0.717 1.45l-0.043 0.111c-1.030-0.165-2.218-0.259-3.428-0.259s-2.398 0.094-3.557 0.275l0.129-0.017c-0.27-0.63-0.528-1.142-0.813-1.638l0.041 0.077c-0.017-0.029-0.048-0.047-0.083-0.047-0.005 0-0.011 0-0.016 0.001l0.001-0c-2.293 0.403-4.342 1.060-6.256 1.957l0.151-0.064c-0.017 0.007-0.031 0.019-0.040 0.034l-0 0c-2.854 4.041-4.562 9.069-4.562 14.496 0 0.907 0.048 1.802 0.141 2.684l-0.009-0.11c0.003 0.029 0.018 0.053 0.039 0.070l0 0c2.14 1.601 4.628 2.891 7.313 3.738l0.176 0.048c0.008 0.003 0.018 0.004 0.028 0.004 0.032 0 0.060-0.015 0.077-0.038l0-0c0.535-0.72 1.044-1.536 1.485-2.392l0.047-0.1c0.006-0.012 0.010-0.027 0.010-0.043 0-0.041-0.026-0.075-0.062-0.089l-0.001-0c-0.912-0.352-1.683-0.727-2.417-1.157l0.077 0.042c-0.029-0.017-0.048-0.048-0.048-0.083 0-0.031 0.015-0.059 0.038-0.076l0-0c0.157-0.118 0.315-0.24 0.465-0.364 0.016-0.013 0.037-0.021 0.059-0.021 0.014 0 0.027 0.003 0.038 0.008l-0.001-0c2.208 1.061 4.8 1.681 7.536 1.681s5.329-0.62 7.643-1.727l-0.107 0.046c0.012-0.006 0.025-0.009 0.040-0.009 0.022 0 0.043 0.008 0.059 0.021l-0-0c0.15 0.124 0.307 0.248 0.466 0.365 0.023 0.018 0.038 0.046 0.038 0.077 0 0.035-0.019 0.065-0.046 0.082l-0 0c-0.661 0.395-1.432 0.769-2.235 1.078l-0.105 0.036c-0.036 0.014-0.062 0.049-0.062 0.089 0 0.016 0.004 0.031 0.011 0.044l-0-0.001c0.501 0.96 1.009 1.775 1.571 2.548l-0.040-0.057c0.017 0.024 0.046 0.040 0.077 0.040 0.010 0 0.020-0.002 0.029-0.004l-0.001 0c2.865-0.892 5.358-2.182 7.566-3.832l-0.065 0.047c0.022-0.016 0.036-0.041 0.039-0.069l0-0c0.087-0.784 0.136-1.694 0.136-2.615 0-5.415-1.712-10.43-4.623-14.534l0.052 0.078c-0.008-0.016-0.022-0.029-0.038-0.036l-0-0z'></path>
          </svg>
          Discord
        </button>

        <button
          onClick={loginWithFacebookOAuth}
          type='button'
          className='w-full py-3 px-4 inline-flex justify-center items-center gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-600 transition-all text-sm bg-gray-800 hover:bg-slate-800 dark:border-gray-700 text-gray-400 hover:text-white focus:ring-offset-gray-800'
        >
          <svg
            xmlns='http://www.w3.org/2000/svg'
            width='24'
            height='24'
            viewBox='0 0 24 24'
            fill='#4267B2'
            className='w-5 h-auto'
          >
            <path d='M24 12.07C24 5.41 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.1 10.13 24v-8.44H7.08v-3.49h3.04V9.41c0-3.02 1.8-4.7 4.54-4.7 1.31 0 2.68.24 2.68.24v2.97h-1.5c-1.5 0-1.96.93-1.96 1.89v2.26h3.32l-.53 3.5h-2.8V24C19.62 23.1 24 18.1 24 12.07' />
          </svg>
          Facebook
        </button>

        <button
          onClick={loginWithRedditOAuth}
          type='button'
          className='w-full py-3 px-4 inline-flex justify-center items-center gap-2 rounded-md border font-medium  shadow-sm align-middle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-600 transition-all text-sm bg-gray-800 hover:bg-slate-800 dark:border-gray-700 text-gray-400 hover:text-white focus:ring-offset-gray-800'
        >
          <svg
            xmlns='http://www.w3.org/2000/svg'
            viewBox='0 0 30 30'
            width='30px'
            height='30px'
            className='w-5 h-auto'
            fill='#FF4500'
          >
            <path d='M 17.662109 2 C 15.565005 2 14 3.7131367 14 5.6621094 L 14 9.0351562 C 11.24971 9.1810926 8.7344872 9.9143634 6.7265625 11.064453 C 5.9527826 10.321405 4.9166871 9.991448 3.9121094 9.9921875 C 2.8229214 9.9929893 1.7094525 10.370413 0.94140625 11.234375 L 0.92382812 11.253906 L 0.90625 11.273438 C 0.16947928 12.194228 -0.12225605 13.427747 0.07421875 14.652344 C 0.25365009 15.770711 0.90137168 16.893419 2.0273438 17.628906 C 2.0199689 17.753058 2 17.874618 2 18 C 2 22.962 7.832 27 15 27 C 22.168 27 28 22.962 28 18 C 28 17.874618 27.980031 17.753058 27.972656 17.628906 C 29.098628 16.893419 29.74635 15.770711 29.925781 14.652344 C 30.122256 13.427747 29.830521 12.194228 29.09375 11.273438 L 29.076172 11.253906 L 29.058594 11.234375 C 28.290448 10.370294 27.177168 9.9929893 26.087891 9.9921875 C 25.08323 9.991448 24.046988 10.321133 23.273438 11.064453 C 21.265513 9.9143634 18.75029 9.1810926 16 9.0351562 L 16 5.6621094 C 16 4.6830821 16.565214 4 17.662109 4 C 18.182797 4 18.817104 4.2609042 19.810547 4.609375 C 20.650361 4.9039572 21.743308 5.2016984 23.140625 5.2910156 C 23.474875 6.2790874 24.402814 7 25.5 7 C 26.875 7 28 5.875 28 4.5 C 28 3.125 26.875 2 25.5 2 C 24.561213 2 23.747538 2.5304211 23.320312 3.3007812 C 22.125831 3.2346294 21.248238 2.9947078 20.472656 2.7226562 C 19.568849 2.4056271 18.738422 2 17.662109 2 z M 3.9121094 11.992188 C 4.3072494 11.991896 4.6826692 12.095595 4.9921875 12.263672 C 3.8881963 13.18517 3.0505713 14.261821 2.5449219 15.4375 C 2.2764358 15.106087 2.114647 14.734002 2.0507812 14.335938 C 1.9430146 13.664243 2.1440212 12.966045 2.4628906 12.552734 C 2.7642172 12.228395 3.3144613 11.992626 3.9121094 11.992188 z M 26.085938 11.992188 C 26.683756 11.992627 27.235874 12.22849 27.537109 12.552734 C 27.855979 12.966045 28.056985 13.664243 27.949219 14.335938 C 27.885353 14.734002 27.723564 15.106087 27.455078 15.4375 C 26.949429 14.261821 26.111804 13.18517 25.007812 12.263672 C 25.316626 12.095792 25.690955 11.991896 26.085938 11.992188 z M 10 14 C 11.105 14 12 14.895 12 16 C 12 17.105 11.105 18 10 18 C 8.895 18 8 17.105 8 16 C 8 14.895 8.895 14 10 14 z M 20 14 C 21.105 14 22 14.895 22 16 C 22 17.105 21.105 18 20 18 C 18.895 18 18 17.105 18 16 C 18 14.895 18.895 14 20 14 z M 20.238281 19.533203 C 19.599281 21.400203 17.556 23 15 23 C 12.444 23 10.400719 21.400969 9.7617188 19.667969 C 10.911719 20.600969 12.828 21.267578 15 21.267578 C 17.172 21.267578 19.088281 20.600203 20.238281 19.533203 z' />
          </svg>
          Reddit
        </button>
        <p className='mt-2 text-center text-sm text-gray-600 dark:text-gray-400'>
          {isSignIn && 'Already have an account? '}
          {!isSignIn && "Don't have an account? "}
          <button
            onClick={() => setIsSignIn((prevState) => !prevState)}
            className='text-purple-600 decoration-2 hover:underline font-medium'
          >
            {isSignIn && 'Sign up'}
            {!isSignIn && 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  )
}

export default AuthPopup
