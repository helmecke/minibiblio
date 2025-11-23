import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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
  created_at: string;
  updated_at: string;
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

function getTypeBadgeVariant(type: CatalogItem["type"]) {
  switch (type) {
    case "book":
      return "default";
    case "dvd":
      return "secondary";
    case "cd":
      return "outline";
    case "magazine":
      return "secondary";
    default:
      return "outline";
  }
}

function getStatusBadgeVariant(status: CatalogItem["status"]) {
  switch (status) {
    case "available":
      return "success";
    case "borrowed":
      return "warning";
    case "reserved":
      return "secondary";
    case "damaged":
      return "destructive";
    case "lost":
      return "destructive";
    default:
      return "outline";
  }
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default async function CatalogItemDetailsPage({
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
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/admin/catalog">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{item.title}</h1>
            <p className="text-muted-foreground font-mono">{item.catalog_id}</p>
          </div>
        </div>
        <Button asChild>
          <Link href={`/admin/catalog/${item.id}/edit`}>
            <Pencil className="mr-2 h-4 w-4" />
            Edit
          </Link>
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Item Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Badge variant={getTypeBadgeVariant(item.type)}>{item.type}</Badge>
              <Badge variant={getStatusBadgeVariant(item.status)}>
                {item.status}
              </Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Author</p>
              <p className="text-sm">{item.author || "-"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">ISBN</p>
              <p className="text-sm font-mono">{item.isbn || "-"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Publisher
              </p>
              <p className="text-sm">{item.publisher || "-"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Year</p>
              <p className="text-sm">{item.year || "-"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Genre</p>
              <p className="text-sm">{item.genre || "-"}</p>
            </div>
            {item.description && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Description
                </p>
                <p className="text-sm">{item.description}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Availability</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Language
              </p>
              <p className="text-sm">{item.language}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Location
              </p>
              <p className="text-sm">{item.location || "-"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Added
              </p>
              <p className="text-sm">{formatDate(item.created_at)}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Last Updated
              </p>
              <p className="text-sm">{formatDate(item.updated_at)}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
