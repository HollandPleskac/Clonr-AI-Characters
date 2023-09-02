import { type NextAuthOptions } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import FacebookProvider from "next-auth/providers/facebook"
import TwitterProvider from "next-auth/providers/twitter"
import DiscordProvider from "next-auth/providers/discord"
import RedditProvider from "next-auth/providers/reddit"
import PostgresAdapter from "./PostgresAdapter"
import pool from "./db"


export const authOptions: NextAuthOptions = {
    adapter: PostgresAdapter(pool),
    providers: [
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
        RedditProvider({
            clientId: process.env.REDDIT_ID as string,
            clientSecret: process.env.REDDIT_SECRET as string,
        }),
    ],
    pages: {
        signIn: '/login',
    },
    callbacks: {
        async session({ session, token, user }) {
            session.email = user?.email
            session.image = user?.image
            session.privateChatName = user?.privateChatName
            return session
        },
      }
};