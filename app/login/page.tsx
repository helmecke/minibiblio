import { signIn } from "@/lib/auth";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 dark:bg-gray-900">
      <div className="w-full max-w-md space-y-8 rounded-lg bg-white p-8 shadow-lg dark:bg-gray-800">
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
            Admin Dashboard
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Sign in to access the admin panel
          </p>
        </div>
        <form
          action={async () => {
            "use server";
            await signIn("google", { redirectTo: "/admin" });
          }}
        >
          <Button type="submit" className="w-full" size="lg">
            Sign in with Google
          </Button>
        </form>
      </div>
    </div>
  );
}
