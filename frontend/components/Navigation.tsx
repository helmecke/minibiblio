"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navLinks = [
  { href: "/", label: "Home" },
  { href: "/login", label: "Patron Login" },
  { href: "/admin/login", label: "Librarian Login" }
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav>
      <ul>
        {navLinks.map((link) => {
          const isActive = link.href === "/" ? pathname === "/" : pathname.startsWith(link.href);
          return (
            <li key={link.href} className={isActive ? "active" : ""}>
              <Link href={link.href}>{link.label}</Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
