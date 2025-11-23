"use client";

import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
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
  const t = useTranslations("catalog");
  const tCommon = useTranslations("common");

  const handleDelete = async (itemId: string) => {
    if (!confirm(t("confirmDelete"))) {
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
      alert(tCommon("error"));
    }
  };

  if (items.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <p className="text-muted-foreground">{t("noItemsFound")}</p>
          <p className="text-sm text-muted-foreground">
            {t("addFirstItem")}
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("allItems")} ({items.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("catalogId")}</TableHead>
              <TableHead>{t("title_field")}</TableHead>
              <TableHead>{t("author")}</TableHead>
              <TableHead>{t("type")}</TableHead>
              <TableHead>{t("status")}</TableHead>
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
                    {t(`types.${item.type}`)}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge variant={getStatusBadgeVariant(item.status)}>
                    {t(`statuses.${item.status}`)}
                  </Badge>
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreHorizontal className="h-4 w-4" />
                        <span className="sr-only">{tCommon("actions")}</span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={() =>
                          router.push(`/admin/catalog/${item.id}`)
                        }
                      >
                        <Eye className="mr-2 h-4 w-4" />
                        {tCommon("details")}
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() =>
                          router.push(`/admin/catalog/${item.id}/edit`)
                        }
                      >
                        <Pencil className="mr-2 h-4 w-4" />
                        {tCommon("edit")}
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={() => handleDelete(item.id)}
                        className="text-destructive focus:text-destructive"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        {tCommon("delete")}
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
