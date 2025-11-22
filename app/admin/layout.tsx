import Link from "next/link";
import {
  Home,
  Package,
  Users2,
  Settings,
  PanelLeft,
  BookOpen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetTitle,
} from "@/components/ui/sheet";
import { NavItem } from "./nav-item";
import { UserMenu } from "./user";
import { Providers } from "./providers";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Providers>
      <div className="flex min-h-screen w-full flex-col bg-muted/40">
        {/* Desktop Sidebar */}
        <aside className="fixed inset-y-0 left-0 z-10 hidden w-14 flex-col border-r bg-background sm:flex">
          <nav className="flex flex-col items-center gap-4 px-2 sm:py-5">
            <Link
              href="/admin"
              className="group flex h-9 w-9 shrink-0 items-center justify-center gap-2 rounded-full bg-primary text-lg font-semibold text-primary-foreground md:h-8 md:w-8 md:text-base"
            >
              <BookOpen className="h-4 w-4 transition-all group-hover:scale-110" />
              <span className="sr-only">MiniBiblio</span>
            </Link>
            <NavItem href="/admin" icon={<Home className="h-5 w-5" />} label="Dashboard" />
            <NavItem href="/admin/catalog" icon={<Package className="h-5 w-5" />} label="Catalog" />
            <NavItem href="/admin/patrons" icon={<Users2 className="h-5 w-5" />} label="Patrons" />
          </nav>
          <nav className="mt-auto flex flex-col items-center gap-4 px-2 sm:py-5">
            <NavItem href="/admin/settings" icon={<Settings className="h-5 w-5" />} label="Settings" />
          </nav>
        </aside>

        {/* Main Content */}
        <div className="flex flex-col sm:gap-4 sm:py-4 sm:pl-14">
          {/* Header */}
          <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6">
            {/* Mobile Menu */}
            <Sheet>
              <SheetTrigger asChild>
                <Button size="icon" variant="outline" className="sm:hidden">
                  <PanelLeft className="h-5 w-5" />
                  <span className="sr-only">Toggle Menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="sm:max-w-xs">
                <SheetTitle className="sr-only">Navigation Menu</SheetTitle>
                <nav className="grid gap-6 text-lg font-medium">
                  <Link
                    href="/admin"
                    className="group flex h-10 w-10 shrink-0 items-center justify-center gap-2 rounded-full bg-primary text-lg font-semibold text-primary-foreground md:text-base"
                  >
                    <BookOpen className="h-5 w-5 transition-all group-hover:scale-110" />
                    <span className="sr-only">MiniBiblio</span>
                  </Link>
                  <Link
                    href="/admin"
                    className="flex items-center gap-4 px-2.5 text-foreground"
                  >
                    <Home className="h-5 w-5" />
                    Dashboard
                  </Link>
                  <Link
                    href="/admin/catalog"
                    className="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground"
                  >
                    <Package className="h-5 w-5" />
                    Catalog
                  </Link>
                  <Link
                    href="/admin/patrons"
                    className="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground"
                  >
                    <Users2 className="h-5 w-5" />
                    Patrons
                  </Link>
                  <Link
                    href="/admin/settings"
                    className="flex items-center gap-4 px-2.5 text-muted-foreground hover:text-foreground"
                  >
                    <Settings className="h-5 w-5" />
                    Settings
                  </Link>
                </nav>
              </SheetContent>
            </Sheet>

            {/* Breadcrumb placeholder */}
            <div className="flex-1" />

            {/* User Menu */}
            <UserMenu />
          </header>

          {/* Page Content */}
          <main className="grid flex-1 items-start gap-4 p-4 sm:px-6 sm:py-0 md:gap-8">
            {children}
          </main>
        </div>
      </div>
    </Providers>
  );
}
