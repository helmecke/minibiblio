import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EditPatronForm } from "./edit-patron-form";

interface Patron {
  id: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  membership_id: string;
  status: "active" | "inactive" | "suspended";
  created_at: string;
  updated_at: string;
}

async function getPatron(id: string): Promise<Patron | null> {
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/python/patrons/${id}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function EditPatronPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const patron = await getPatron(id);

  if (!patron) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href={`/admin/patrons/${patron.id}`}>
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Edit Patron</h1>
          <p className="text-muted-foreground font-mono">
            {patron.membership_id}
          </p>
        </div>
      </div>

      <EditPatronForm patron={patron} />
    </div>
  );
}
