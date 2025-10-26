export default function HomePage() {
  return (
    <section className="card">
      <h2>Welcome</h2>
      <p>
        This Next.js frontend pairs with the FastAPI backend shipped in <code>/backend</code>. Use the top navigation to
        explore the patron and librarian sign-in flows. API responses are displayed inline so you can confirm the auth
        handshake before integrating real persistence or design systems.
      </p>
      <ul>
        <li>Patron login accepts the demo account <code>patron / patron123</code>.</li>
        <li>Librarian login accepts the demo account <code>librarian / library123</code>.</li>
        <li>Configure the backend URL via <code>NEXT_PUBLIC_API_BASE_URL</code>.</li>
      </ul>
    </section>
  );
}
