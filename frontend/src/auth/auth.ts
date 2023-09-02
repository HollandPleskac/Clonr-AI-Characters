import { type NextAuthOptions } from "next-auth"
import GithubProvider from "next-auth/providers/github"
import Auth0Provider from "next-auth/providers/auth0"
import GoogleProvider from "next-auth/providers/google"
import FacebookProvider from "next-auth/providers/facebook"
import TwitterProvider from "next-auth/providers/twitter"
import DiscordProvider from "next-auth/providers/discord"
import PostgresAdapter from "./PostgresAdapter"
import pool from "./db"
import { stringify } from "querystring"


export const authOptions: NextAuthOptions = {
    adapter: PostgresAdapter(pool),
    providers: [
        // Auth0Provider({
        //     clientId: process.env.AUTH0_ID as string,
        //     clientSecret: process.env.AUTH0_SECRET as string,
        //     issuer: process.env.AUTH0_ISSUER as string,
        // }),
        // GithubProvider({
        //     clientId: process.env.GITHUB_ID as string,
        //     clientSecret: process.env.GITHUB_SECRET as string,
        // }),
        FacebookProvider({
            clientId: process.env.FACEBOOK_ID as string,
            clientSecret: process.env.FACEBOOK_SECRET as string,
        }),
        GoogleProvider({
            clientId: process.env.GOOGLE_ID as string,
            clientSecret: process.env.GOOGLE_SECRET as string,
        }),
        TwitterProvider({
            clientId: process.env.TWITTER_ID as string,
            clientSecret: process.env.TWITTER_SECRET as string,
            version: "2.0",
        }),
        DiscordProvider({
            clientId: process.env.DISCORD_ID as string,
            clientSecret: process.env.DISCORD_SECRET as string,
        }),
    ],
    pages: {
        signIn: '/login',
        // signOut: '/auth/signout',
        // error: '/auth/error', // Error code passed in query string as ?error=
        // verifyRequest: '/auth/verify-request', // (used for check email message)
        // newUser: '/auth/new-user' // New users will be directed here on first sign in (leave the property out if not of interest)
    },
    callbacks: {
        async session({ session, token, user }) {
          // Send properties to the client, like an access_token and user id from a provider.
        //   session.accessToken = token.accessToken
        //   session.user.id = token.id
          session.email = user?.email
        //   console.log(JSON.stringify(user))
          session.image = user?.image
          return session
        },
        // async redirect({ url, baseUrl }) {
            // console.log("return, base", url,baseUrl)
            // Allows relative callback URLs
            // if (url.startsWith("/")) return `${baseUrl}${url}`
            // Allows callback URLs on the same origin
            // else if (new URL(url).origin === baseUrl) return url
            // return baseUrl
        //   }
      }
};