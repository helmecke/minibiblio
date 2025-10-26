import type { Metadata } from "next";
import "../styles/globals.css";
import { Navigation } from "../components/Navigation";

export const metadata: Metadata = {
  title: "MiniBiblio Portal",
  description: "Frontend template for MiniBiblio fullstack starter"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header className="app-header">
          <div className="container">
            <h1>MiniBiblio</h1>
            <Navigation />
          </div>
        </header>
        <main className="container">{children}</main>
        <footer className="app-footer">
          <div className="container">
            <small>&copy; {new Date().getFullYear()} MiniBiblio Team</small>
          </div>
        </footer>
      </body>
    </html>
  );
}
