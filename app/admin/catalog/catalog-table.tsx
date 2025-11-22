"use client";

import { useRouter } from "next/navigation";
import { MoreHorizontal, Eye, Pencil, Trash2 } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface CatalogItem {
  id: string;
  catalog_id: string;
  type: "book" | "dvd" | "cd" | "magazine" | "other";
  title: string;
  author?: string;
  isbn?: string;
  status: "available" | "borrowed" | "reserved" | "damaged" | "lost";
  created_at: string;
  updated_at: string;
}

interface CatalogTableProps {
  items: CatalogItem[];
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

export function CatalogTable({ items }: CatalogTableProps) {
  const router = useRouter();

  const handleDelete = async (itemId: string) => {
    if (!confirm("Are you sure you want to delete this item?")) {
      return;
    }

    try {
      const res = await fetch(`/api/python/catalog/${itemId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        throw new Error("Failed to delete item");
      }

      router.refresh();
    } catch (error) {
      console.error("Error deleting item:", error);
      alert("Failed to delete item");
    }
  };

  if (items.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <p className="text-muted-foreground">No items found</p>
          <p className="text-sm text-muted-foreground">
            Add your first book or media item to get started
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>All Items ({items.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Catalog ID</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Author</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.id}>
                <TableCell className="font-mono text-sm">
                  {item.catalog_id}
                </TableCell>
                <TableCell className="font-medium max-w-[300px] truncate">
                  {item.title}
                </TableCell>
                <TableCell>{item.author || "-"}</TableCell>
                <TableCell>
                  <Badge variant={getTypeBadgeVariant(item.type)}>
                    {item.type}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge variant={getStatusBadgeVariant(item.status)}>
                    {item.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreHorizontal className="h-4 w-4" />
                        <span className="sr-only">Open menu</span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={() =>
                          router.push(`/admin/catalog/${item.id}`)
                        }
                      >
                        <Eye className="mr-2 h-4 w-4" />
                        Details
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() =>
                          router.push(`/admin/catalog/${item.id}/edit`)
                        }
                      >
                        <Pencil className="mr-2 h-4 w-4" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={() => handleDelete(item.id)}
                        className="text-destructive focus:text-destructive"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
