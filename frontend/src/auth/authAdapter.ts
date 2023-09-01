const Pool = require('pg').Pool;
import type { Adapter, AdapterAccount, AdapterSession, AdapterUser } from "next-auth/adapters"


interface ProviderArgs {
    providerAccountId: string
    provider: string
}


// from the docs: https://node-postgres.com/apis/pool
// "Do not use pool.query if you are using a transaction." Only use the Pool
// if we don't care about transactions! Otherwise, wait for a connection.
// Implement updateAccount and deleteAccount functions similarly
export default function PostgresAdapter(pool: typeof Pool): Adapter {
  return {
    async createUser(user: Omit<AdapterUser, "id">) {
        // // console.log("createUser " + JSON.stringify(user))
        const query = `
            INSERT INTO "users" (
                name, 
                email, 
                email_verified,
                image,
                is_superuser,
                private_chat_name,
                is_banned,
                is_active,
                nsfw_enabled,
                num_free_messages_sent
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING *;
        `;
        const is_superuser = false;
        const private_chat_name = "user";
        const is_active = true;
        const is_banned = false;
        const nsfw_enabled = false;
        const num_free_messages_sent = 0;
        const client = await pool.connect()
        try {
            const values = [
                user.name, 
                user.email, 
                user.emailVerified,
                user.image,
                is_superuser,
                private_chat_name,
                is_banned,
                is_active,
                nsfw_enabled,
                num_free_messages_sent,
            ];
            const result = await client.query(query, values);
            const u = result.rows ? result.rows[0] : null;
            if (u === null) {
              return u
            }
            const userResult: AdapterUser = {
              id: u.id,
              email: u.email,
              emailVerified: u.email_verified,
              privateChatName: u.private_chat_name,
              isActive: u.is_active,
              numFreeMessagesSent: u.num_free_messages_sent
            }
            return userResult
        }
        catch (err) {
            console.log(err)
        }
        finally {
            await client.release();
        }
    },
      async getUser(id: string) {
        // // console.log("getUser " + JSON.stringify(id))
          const query = `
            SELECT * FROM "users" WHERE users.id = $1::uuid LIMIT 1;
          `;
          try {
            const result = await pool.query(query, [id])
            const u = result.rows ? result.rows[0] : null;
            if (u === null) {
              return u
            }
            const userResult: AdapterUser = {
              id: u.id,
              email: u.email,
              emailVerified: u.email_verified,
              privateChatName: u.private_chat_name,
              isActive: u.is_active,
              numFreeMessagesSent: u.num_free_messages_sent
            }
            return userResult
          } catch (err) {
            console.log(err)
            return null;
          } 
    },
    async getUserByEmail(email: string) {
        // console.log("getUserByEmail " + JSON.stringify(email))
        const query = `
          SELECT * FROM "users" WHERE users.email = $1 LIMIT 1;
        `;
          try {
            const result = await pool.query(query, [email])
            const u = result.rows ? result.rows[0] : null;
            if (u === null) {
              return u
            }
            const userResult: AdapterUser = {
              id: u.id,
              email: u.email,
              emailVerified: u.email_verified,
              privateChatName: u.private_chat_name,
              isActive: u.is_active,
              numFreeMessagesSent: u.num_free_messages_sent
            }
            return userResult
          } catch (err) {
            console.log(err)
            return null;
          } 
    },
      async getUserByAccount({ providerAccountId, provider }: ProviderArgs) {
        // console.log("getUserByAccount " + JSON.stringify({ providerAccountId, provider }))
        const query = `
            SELECT users.* FROM users JOIN accounts ON users.id = accounts.user_id 
            WHERE provider_account_id = $1::text AND provider = $2::text LIMIT 1;
        `;
          try {
            const result = await pool.query(query, [providerAccountId, provider])
            const u = result.rows ? result.rows[0] : null;
            // console.log("FUCKING RESULT " + JSON.stringify(u))
            if (u === null) {
              return u
            }
            const userResult: AdapterUser = {
              id: u.id,
              email: u.email,
              emailVerified: u.email_verified,
              privateChatName: u.private_chat_name,
              isActive: u.is_active,
              numFreeMessagesSent: u.num_free_messages_sent
            }
            return userResult
          } catch (err) {
            console.log(err)
            return null;
          }
    },
      async updateUser(user: Partial<AdapterUser> & Pick<AdapterUser, "id">) {
        // console.log("updateUser " + JSON.stringify(user))
          const query = `
            UPDATE "users"
            SET private_chat_name = $1, is_active = $2
            WHERE users.id = $3::uuid
            RETURNING *;
          `
          const values = [user.privateChatName, user.isActive, user.id]
          const client = await pool.connect()
          try {
              const result = await client.query(query, values)
              const u = result.rows ? result.rows[0] : null;
              if (u === null) {
                return u
              }
              const userResult: AdapterUser = {
                id: u.id,
                email: u.email,
                emailVerified: u.email_verified,
                privateChatName: u.private_chat_name,
                isActive: u.is_active,
                numFreeMessagesSent: u.num_free_messages_sent
              }
              return userResult
          } catch (err) {
              console.log(err)
              return null;
          } finally {
              await client.release()
        }
    },
    async deleteUser(userId) {
        // console.log("deleteUser " + JSON.stringify(userId))
          const query = `
            UPDATE "users"
            SET is_active = $1
            WHERE users.id = $2::uuid
            RETURNING *;
          `
          const values = [false, userId]
          const client = await pool.connect()
          try {
              const result = await client.query(query, values)
              const u = result.rows ? result.rows[0] : null;
              if (u === null) {
                return u
              }
              const userResult: AdapterUser = {
                id: u.id,
                email: u.email,
                emailVerified: u.email_verified,
                privateChatName: u.private_chat_name,
                isActive: u.is_active,
                numFreeMessagesSent: u.num_free_messages_sent
              }
              return userResult
          } catch (err) {
              console.log(err)
              return null;
          }
                  finally {
              await client.release()
        }
    },
    async linkAccount(account) {
        // console.log("linkAccount " + JSON.stringify(account))
        const query = `
          INSERT INTO "accounts" (
                type, 
                provider, 
                provider_account_id,
                refresh_token,
                access_token,
                expires_at,
                token_type,
                scope,
                id_token,
                session_state,
                user_id
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING *;
        `
        const values = [
            account.type,
            account.provider,
            account.providerAccountId,
            account.refresh_token,
            account.access_token,
            account.expires_at,
            account.token_type,
            account.scope,
            account.id_token,
            account.session_state,
            account.userId
          ]
          const client = await pool.connect()
          try {
              const result = await client.query(query, values)
            const u = result.rows ? result.rows[0] : null;
            if (u === null) {
              return u
            }
            const accountResult: AdapterAccount = {
              type: u.type,
              provider: u.provider,
              providerAccountId: u.provider_account_id,
              refresh_token: u.refresh_token,
              access_token: u.access_token,
              expires_at: u.expires_at,
              token_type: u.token_type,
              scope: u.scope,
              id_token: u.id_token,
              session_state: u.session_state,
              userId: u.user_id
            }
            return accountResult
          } catch (err) {
              console.log(err)
              return null;
          }
          finally {
              await client.release()
          }
      },
    async unlinkAccount({ providerAccountId, provider }: ProviderArgs) {
        // console.log("unlinkAccount " + JSON.stringify({providerAccountId, provider}))
        const query = `
          DELETE FROM "accounts"
          WHERE provider_account_id = $1::text AND provider = $2
          RETURNING *;
        `
        const values = [
            providerAccountId,
            provider
          ]
          const client = await pool.connect()
          try {
              const result = await client.query(query, values)
              const u = result.rows ? result.rows[0] : null;
            if (u === null) {
              return u
            }
            const accountResult: AdapterAccount = {
              type: u.type,
              provider: u.provider,
              providerAccountId: u.provider_account_id,
              refresh_token: u.refresh_token,
              access_token: u.access_token,
              expires_at: u.expires_at,
              token_type: u.token_type,
              scope: u.scope,
              id_token: u.id_token,
              session_state: u.session_state,
              userId: u.user_id
            }
            return accountResult
          } catch (err) {
              console.log(err)
              return null;
          }
          finally {
              await client.release()
        }
    },
    async createSession({ sessionToken, userId, expires }) {
        // console.log("createSession " + JSON.stringify({ sessionToken, userId, expires }))
        const query = `
            INSERT INTO "sessions" (
                session_token, 
                expires, 
                user_id
            )
            VALUES ($1, $2, $3)
            RETURNING *;
        `
        const values = [sessionToken, expires, userId];
          const client = await pool.connect()
          try {
              const result = await client.query(query, values)
            const u = result.rows ? result.rows[0] : null
            if (u === null) {
              return u
            }
            const sessionResult: AdapterSession = {
              sessionToken: u.session_token,
              userId: u.user_id,
              expires: u.expires
            }
            return sessionResult
          } catch (err) {
              console.log(err)
              return null;
          }
          finally {
              await client.release()
          }
    },
    async getSessionAndUser(sessionToken: string) {
        // console.log("getSessionAndUser " + JSON.stringify(sessionToken))
        let session: AdapterSession;
      let user: AdapterUser;
        try {
            const query = `SELECT * FROM sessions WHERE session_token = $1 LIMIT 1;`
            const sess_result = await pool.query(query, [sessionToken])
            const v = sess_result.rows ? sess_result.rows[0] : null
            if (v === null) {
                throw "Session does not exist"
            } 
          session = {
              sessionToken: v.session_token,
              userId: v.user_id,
              expires: v.expires
            }
        } catch (err) {
            console.log(err)
            return null
        }
        try {
            const query = `SELECT * FROM users WHERE users.id = $1::uuid LIMIT 1;`
            const user_result = await pool.query(query, [session.userId])
            const u = user_result.rows ? user_result.rows[0] : null
            if (u === null) {
              throw "User does not exist"
            }
            user = {
              id: u.id,
              email: u.email,
              emailVerified: u.email_verified,
              privateChatName: u.private_chat_name,
              isActive: u.is_active,
              numFreeMessagesSent: u.num_free_messages_sent
            }
        } catch (err) {
            console.log(err)
            return null
        }
        return { user, session }
    },
      async updateSession(data) {
        // console.log("updateSession " + `WTF IS UPDATE SESSION??? ${JSON.stringify(data)}`)
        const query = `
            UPDATE "sessions"
            SET expires = $1, user_id = $2::uuid
            WHERE sessions.session_token = $3
            RETURNING *;
          `
          const values = [data.expires, data.userId, data.sessionToken]
          const client = await pool.connect()
          try {
              const result = await client.query(query, values)
            const u = result.rows ? result.rows[0] : null
            if (u === null) {
              return u
            }
            const sessionResult: AdapterSession = {
              sessionToken: u.session_token,
              userId: u.user_id,
              expires: u.expires
            }
            return sessionResult
          } catch (err) {
              console.log(err)
              return null;
          } finally {
              await client.release()
        }
    },
      async deleteSession(sessionToken: string) {
        // console.log("deleteSession")
        const query = `
          DELETE FROM "sessions"
          WHERE session_token = $1
          RETURNING *;
        `
        const values = [
            sessionToken
          ]
          const client = await pool.connect()
          try {
            const result = await client.query(query, values)
            const u = result.rows ? result.rows[0] : null
            if (u === null) {
              return u
            }
            const sessionResult: AdapterSession = {
              sessionToken: u.session_token,
              userId: u.user_id,
              expires: u.expires
            }
            return sessionResult
          } catch (err) {
              console.log(err)
              return null;
          }
          finally {
              await client.release()
        }
    },
    async createVerificationToken({ identifier, expires, token }) {
        const query = `
            INSERT INTO "verification_tokens"
            (identifier, token, expires)
            VALUES ($1, $2, $3)
            RETURNING *;
        `
        const values = [identifier, expires, token]
        const client = await pool.connect()
          try {
              const result = await client.query(query, values)
              const u = result.rows ? result.rows[0] : null
          } catch (err) {
              console.log(err)
              return null;
          }
          finally {
              await client.release()
        }        
    },
    async useVerificationToken({ identifier, token }) {
        const query = `
            DELETE FROM "verification_tokens
            WHERE identifier = $1 AND token = $2;
        `
        const values = [identifier, token]
        const client = await pool.connect()
        try {
            const result = await client.query(query, values)
            return result.rows ? result.rows[0] : null
        } catch (err) {
              console.log(err)
              return null;
          }
          finally {
              await client.release()
        } 
    },
  }
}