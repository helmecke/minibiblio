"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { MoreHorizontal, Eye, Pencil, Trash2, BookUp } from "lucide-react";
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
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

interface Patron {
  id: string;
  membership_id: string;
  first_name: string;
  last_name: string;
  status: string;
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
  const tCirculation = useTranslations("circulation");
  const tErrors = useTranslations("errors");

  // Checkout dialog state
  const [checkoutItem, setCheckoutItem] = useState<CatalogItem | null>(null);
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);
  const [patrons, setPatrons] = useState<Patron[]>([]);
  const [checkoutForm, setCheckoutForm] = useState({
    patron_id: "",
    due_days: "14",
    notes: "",
  });

  useEffect(() => {
    if (checkoutOpen) {
      fetch("/api/python/patrons?status=active")
        .then((res) => res.json())
        .then((data) => setPatrons(data))
        .catch((err) => console.error("Error fetching patrons:", err));
    }
  }, [checkoutOpen]);

  const handleCheckoutClick = (item: CatalogItem) => {
    setCheckoutItem(item);
    setCheckoutError(null);
    setCheckoutForm({ patron_id: "", due_days: "14", notes: "" });
    setCheckoutOpen(true);
  };

  const handleCheckoutSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!checkoutItem) return;

    setCheckoutLoading(true);
    setCheckoutError(null);

    try {
      const payload = {
        patron_id: checkoutForm.patron_id,
        catalog_item_id: checkoutItem.id,
        due_days: parseInt(checkoutForm.due_days),
        notes: checkoutForm.notes || null,
      };

      const res = await fetch("/api/python/loans/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || tErrors("failedToCreate", { resource: tCirculation("title") }));
      }

      setCheckoutOpen(false);
      setCheckoutItem(null);
      router.refresh();
    } catch (err) {
      setCheckoutError(err instanceof Error ? err.message : tErrors("anErrorOccurred"));
    } finally {
      setCheckoutLoading(false);
    }
  };

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
                      {item.status === "available" && (
                        <DropdownMenuItem
                          onClick={() => handleCheckoutClick(item)}
                        >
                          <BookUp className="mr-2 h-4 w-4" />
                          {tCirculation("checkout")}
                        </DropdownMenuItem>
                      )}
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

      {/* Checkout Dialog */}
      <Dialog open={checkoutOpen} onOpenChange={setCheckoutOpen}>
        <DialogContent className="sm:max-w-[525px]">
          <form onSubmit={handleCheckoutSubmit}>
            <DialogHeader>
              <DialogTitle>{tCirculation("checkoutItem")}</DialogTitle>
              <DialogDescription>
                {tCirculation("checkoutDescription")}
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              {checkoutError && (
                <div className="text-sm text-destructive bg-destructive/10 p-2 rounded">
                  {checkoutError}
                </div>
              )}

              {/* Show selected item (read-only) */}
              <div className="grid grid-cols-4 items-center gap-4">
                <Label className="text-right">
                  {tCirculation("item")}
                </Label>
                <div className="col-span-3 p-2 bg-muted rounded text-sm">
                  {checkoutItem?.title}{" "}
                  <span className="text-muted-foreground">({checkoutItem?.catalog_id})</span>
                </div>
              </div>

              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="patron" className="text-right">
                  {tCirculation("patron")}
                </Label>
                <Select
                  value={checkoutForm.patron_id}
                  onValueChange={(value) =>
                    setCheckoutForm({ ...checkoutForm, patron_id: value })
                  }
                  required
                >
                  <SelectTrigger className="col-span-3">
                    <SelectValue placeholder={tCirculation("selectPatron")} />
                  </SelectTrigger>
                  <SelectContent>
                    {patrons.map((patron) => (
                      <SelectItem key={patron.id} value={patron.id}>
                        {patron.first_name} {patron.last_name} ({patron.membership_id})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="due_days" className="text-right">
                  {tCirculation("loanPeriod")}
                </Label>
                <Select
                  value={checkoutForm.due_days}
                  onValueChange={(value) =>
                    setCheckoutForm({ ...checkoutForm, due_days: value })
                  }
                >
                  <SelectTrigger className="col-span-3">
                    <SelectValue placeholder={tCirculation("selectPeriod")} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="7">{tCirculation("days", { count: 7 })}</SelectItem>
                    <SelectItem value="14">{tCirculation("daysDefault", { count: 14 })}</SelectItem>
                    <SelectItem value="21">{tCirculation("days", { count: 21 })}</SelectItem>
                    <SelectItem value="28">{tCirculation("days", { count: 28 })}</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="notes" className="text-right">
                  {tCirculation("notes")}
                </Label>
                <Textarea
                  id="notes"
                  value={checkoutForm.notes}
                  onChange={(e) =>
                    setCheckoutForm({ ...checkoutForm, notes: e.target.value })
                  }
                  className="col-span-3"
                  placeholder={tCirculation("notesPlaceholder")}
                  rows={2}
                />
              </div>
            </div>
            <DialogFooter>
              <Button
                type="submit"
                disabled={checkoutLoading || !checkoutForm.patron_id}
              >
                {checkoutLoading ? tCirculation("processing") : tCirculation("checkout")}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
