"use client";

import { useState, useEffect, useCallback } from "react";
import { useTranslations } from "next-intl";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { CatalogTable } from "./catalog-table";
import { Card, CardContent } from "@/components/ui/card";

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

export function CatalogContent() {
  const t = useTranslations("catalog");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");

  const [items, setItems] = useState<CatalogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const fetchItems = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (debouncedSearch) {
        params.append("search", debouncedSearch);
      }
      const url = `/api/python/catalog${params.toString() ? `?${params}` : ""}`;
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) {
        throw new Error("Failed to fetch catalog items");
      }
      const data = await res.json();
      setItems(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : tErrors("failedToLoad", { resource: t("title") }));
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, t, tErrors]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  if (error) {
    return (
      <div className="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive">
        {error}. {tErrors("serverNotRunning")}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder={t("searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-9"
          />
          {search && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-1 top-1/2 h-7 w-7 -translate-y-1/2"
              onClick={() => setSearch("")}
            >
              <X className="h-4 w-4" />
              <span className="sr-only">{tCommon("clearSearch")}</span>
            </Button>
          )}
        </div>
      </div>

      {loading ? (
        <Card>
          <CardContent className="flex items-center justify-center py-10">
            <p className="text-muted-foreground">{tCommon("loading")}</p>
          </CardContent>
        </Card>
      ) : (
        <CatalogTable items={items} />
      )}
    </div>
  );
}
