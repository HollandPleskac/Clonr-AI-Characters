import NextAuth from "next-auth"

// visit https://reacthustle.com/blog/extend-user-session-nextauth-typescript
declare module "next-auth" {
  interface User {
    privateChatName: string,
    numFreeMessagesSent: number,
    isActive: boolean
  }
}