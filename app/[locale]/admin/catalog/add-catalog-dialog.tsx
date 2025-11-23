"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { useTranslations } from "next-intl";
import { PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

interface FormData {
  type: string;
  title: string;
  author: string;
  isbn: string;
  publisher: string;
  year: string;
  genre: string;
  description: string;
  language: string;
  location: string;
  status: string;
}

export function AddCatalogDialog() {
  const router = useRouter();
  const t = useTranslations("catalog");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<FormData>({
    type: "book",
    title: "",
    author: "",
    isbn: "",
    publisher: "",
    year: "",
    genre: "",
    description: "",
    language: "English",
    location: "",
    status: "available",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        type: formData.type,
        title: formData.title,
        author: formData.author || null,
        isbn: formData.isbn || null,
        publisher: formData.publisher || null,
        year: formData.year ? parseInt(formData.year) : null,
        genre: formData.genre || null,
        description: formData.description || null,
        language: formData.language,
        location: formData.location || null,
        status: formData.status,
      };

      const res = await fetch("/api/python/catalog", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || tErrors("failedToCreate", { resource: t("title") }));
      }

      setOpen(false);
      setFormData({
        type: "book",
        title: "",
        author: "",
        isbn: "",
        publisher: "",
        year: "",
        genre: "",
        description: "",
        language: "English",
        location: "",
        status: "available",
      });
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : tErrors("anErrorOccurred"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" className="h-8 gap-1">
          <PlusCircle className="h-3.5 w-3.5" />
          <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
            {t("addItem")}
          </span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[525px] max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{t("addItem")}</DialogTitle>
            <DialogDescription>
              {t("addItemDescription")}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            {error && (
              <div className="text-sm text-destructive bg-destructive/10 p-2 rounded">
                {error}
              </div>
            )}

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="type" className="text-right">
                {t("type")}
              </Label>
              <Select
                value={formData.type}
                onValueChange={(value) =>
                  setFormData({ ...formData, type: value })
                }
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder={t("selectType")} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="book">{t("types.book")}</SelectItem>
                  <SelectItem value="dvd">{t("types.dvd")}</SelectItem>
                  <SelectItem value="cd">{t("types.cd")}</SelectItem>
                  <SelectItem value="magazine">{t("types.magazine")}</SelectItem>
                  <SelectItem value="other">{t("types.other")}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="title" className="text-right">
                {t("title_field")}
              </Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value })
                }
                className="col-span-3"
                required
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="author" className="text-right">
                {t("author")}
              </Label>
              <Input
                id="author"
                value={formData.author}
                onChange={(e) =>
                  setFormData({ ...formData, author: e.target.value })
                }
                className="col-span-3"
                placeholder={tCommon("optional")}
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="isbn" className="text-right">
                {t("isbn")}
              </Label>
              <Input
                id="isbn"
                value={formData.isbn}
                onChange={(e) =>
                  setFormData({ ...formData, isbn: e.target.value })
                }
                className="col-span-3"
                placeholder={tCommon("optional")}
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="publisher" className="text-right">
                {t("publisher")}
              </Label>
              <Input
                id="publisher"
                value={formData.publisher}
                onChange={(e) =>
                  setFormData({ ...formData, publisher: e.target.value })
                }
                className="col-span-3"
                placeholder={tCommon("optional")}
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="year" className="text-right">
                {t("year")}
              </Label>
              <Input
                id="year"
                type="number"
                value={formData.year}
                onChange={(e) =>
                  setFormData({ ...formData, year: e.target.value })
                }
                className="col-span-3"
                placeholder={tCommon("optional")}
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="genre" className="text-right">
                {t("genre")}
              </Label>
              <Input
                id="genre"
                value={formData.genre}
                onChange={(e) =>
                  setFormData({ ...formData, genre: e.target.value })
                }
                className="col-span-3"
                placeholder={tCommon("optional")}
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">
                {t("description_field")}
              </Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                className="col-span-3"
                placeholder={tCommon("optional")}
                rows={3}
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="location" className="text-right">
                {t("location")}
              </Label>
              <Input
                id="location"
                value={formData.location}
                onChange={(e) =>
                  setFormData({ ...formData, location: e.target.value })
                }
                className="col-span-3"
                placeholder={t("locationPlaceholder")}
              />
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="status" className="text-right">
                {t("status")}
              </Label>
              <Select
                value={formData.status}
                onValueChange={(value) =>
                  setFormData({ ...formData, status: value })
                }
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder={t("selectStatus")} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="available">{t("statuses.available")}</SelectItem>
                  <SelectItem value="borrowed">{t("statuses.borrowed")}</SelectItem>
                  <SelectItem value="reserved">{t("statuses.reserved")}</SelectItem>
                  <SelectItem value="damaged">{t("statuses.damaged")}</SelectItem>
                  <SelectItem value="lost">{t("statuses.lost")}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={loading}>
              {loading ? tCommon("loading") : t("createItem")}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
