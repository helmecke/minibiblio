import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EditCatalogForm } from "./edit-catalog-form";

interface CatalogItem {
  id: string;
  catalog_id: string;
  type: "book" | "dvd" | "cd" | "magazine" | "other";
  title: string;
  author?: string;
  isbn?: string;
  publisher?: string;
  year?: number;
  description?: string;
  genre?: string;
  language: string;
  location?: string;
  status: "available" | "borrowed" | "reserved" | "damaged" | "lost";
}

async function getCatalogItem(id: string): Promise<CatalogItem | null> {
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/python/catalog/${id}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function EditCatalogItemPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const item = await getCatalogItem(id);

  if (!item) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href={`/admin/catalog/${item.id}`}>
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Edit Item</h1>
          <p className="text-muted-foreground font-mono">{item.catalog_id}</p>
        </div>
      </div>

      <EditCatalogForm item={item} />
    </div>
  );
}
