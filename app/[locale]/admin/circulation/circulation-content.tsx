"use client";

import { useState, useEffect, useCallback } from "react";
import { useTranslations } from "next-intl";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { LoansTable } from "./loans-table";
import { Card, CardContent } from "@/components/ui/card";

interface Loan {
  id: string;
  loan_id: string;
  catalog_item: {
    id: string;
    catalog_id: string;
    title: string;
    author?: string;
    type: string;
  };
  patron: {
    id: string;
    membership_id: string;
    first_name: string;
    last_name: string;
  };
  checkout_date: string;
  due_date: string;
  return_date?: string;
  status: "active" | "returned" | "overdue" | "lost";
  notes?: string;
}

export function CirculationContent() {
  const t = useTranslations("circulation");
  const tErrors = useTranslations("errors");
  const tCommon = useTranslations("common");

  const [loans, setLoans] = useState<Loan[]>([]);
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

  const fetchLoans = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (debouncedSearch) {
        params.append("search", debouncedSearch);
      }
      const url = `/api/python/loans${params.toString() ? `?${params}` : ""}`;
      const res = await fetch(url, { cache: "no-store" });
      if (!res.ok) {
        throw new Error("Failed to fetch loans");
      }
      const data = await res.json();
      setLoans(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : tErrors("failedToLoad", { resource: t("title") }));
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, t, tErrors]);

  useEffect(() => {
    fetchLoans();
  }, [fetchLoans]);

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
        <LoansTable loans={loans} />
      )}
    </div>
  );
}
