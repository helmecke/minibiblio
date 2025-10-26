import Link from "next/link";
import LoginForm from "../../../components/LoginForm";

export default function LibrarianLoginPage() {
  return (
    <>
      <LoginForm heading="Librarian Login" endpoint="/auth/admin/login" successStorageKey="minibiblio.librarian.token" />
      <section className="card">
        <h3>Need librarian credentials?</h3>
        <p>
          Replace the seed user store in <code>backend/app/users.py</code> with your own data source. Once authenticated,
          navigate to the <Link href="/admin/dashboard">librarian dashboard</Link> to showcase privileged flows.
        </p>
      </section>
    </>
  );
}
