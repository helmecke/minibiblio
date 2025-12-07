import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import Credentials from "next-auth/providers/credentials";

const ENABLE_GOOGLE_AUTH = process.env.ENABLE_GOOGLE_AUTH === "true";
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Credentials({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          return null;
        }

        try {
          const response = await fetch(`${API_BASE_URL}/api/python/auth/login`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              username: credentials.username,
              password: credentials.password,
            }),
          });

          if (!response.ok) {
            return null;
          }

          const data = await response.json();
          
          // Fetch user details
          const userResponse = await fetch(`${API_BASE_URL}/api/python/auth/me`, {
            headers: {
              Authorization: `Bearer ${data.access_token}`,
            },
          });

          if (!userResponse.ok) {
            return null;
          }

          const user = await userResponse.json();

          return {
            id: user.id,
            name: user.username,
            email: user.email || "",
            role: user.role,
            accessToken: data.access_token,
          };
        } catch (error) {
          console.error("Authentication error:", error);
          return null;
        }
      },
    }),
    ...(ENABLE_GOOGLE_AUTH ? [Google] : []),
  ],
  pages: {
    signIn: "/login",
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = (user as any).accessToken;
        token.role = (user as any).role;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).accessToken = token.accessToken as string;
        (session.user as any).role = token.role as string;
      }
      return session;
    },
  },
});
