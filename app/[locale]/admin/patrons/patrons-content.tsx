"use client";

import { useState, useEffect, useCallback } from "react";
import { useTranslations } from "next-intl";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { PatronsTable } from "./patrons-table";
import { Card, CardContent } from "@/components/ui/card";

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

export function PatronsContent() {
  const t = useTranslations("patrons");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");

  const [patrons, setPatrons] = useState<Patron[]>([]);
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

  const fetchPatrons = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (debouncedSearch) {
        params.append("search", debouncedSearch);
      }
      const url = `/api/python/patrons${params.toString() ? `?${params}` : ""}`;
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) {
        throw new Error("Failed to fetch patrons");
      }
      const data = await res.json();
      setPatrons(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : tErrors("failedToLoad", { resource: t("title") }));
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, t, tErrors]);

  useEffect(() => {
    fetchPatrons();
  }, [fetchPatrons]);

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
        <PatronsTable patrons={patrons} />
      )}
    </div>
  );
}
