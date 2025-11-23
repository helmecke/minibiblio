"use client";

import { useState, useEffect, useCallback } from "react";
import { useTranslations } from "next-intl";
import { BarChart3, Users, Book, Calendar, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface Patron {
  id: string;
  membership_id: string;
  name: string;
}

interface PatronLoanItem {
  loan_id: string;
  catalog_id: string;
  title: string;
  author: string | null;
  checkout_date: string;
  due_date: string;
  return_date: string | null;
  status: string;
}

interface PatronLoanHistory {
  patron_id: string;
  membership_id: string;
  patron_name: string;
  total_loans: number;
  active_loans: number;
  loans: PatronLoanItem[];
}

interface TopBorrowedBook {
  item_id: string;
  catalog_id: string;
  title: string;
  author: string | null;
  loan_count: number;
}

interface MonthlyLoanCount {
  month: number;
  count: number;
}

interface YearlyStatistics {
  year: number;
  total_loans: number;
  unique_books: number;
  unique_patrons: number;
  top_borrowed_books: TopBorrowedBook[];
  monthly_breakdown: MonthlyLoanCount[];
}

type TabType = "patron" | "yearly";

export default function ReportsPage() {
  const t = useTranslations("reports");
  const tCommon = useTranslations("common");

  const [activeTab, setActiveTab] = useState<TabType>("patron");
  const [loading, setLoading] = useState(false);

  // Patron history state
  const [patrons, setPatrons] = useState<Patron[]>([]);
  const [selectedPatronId, setSelectedPatronId] = useState<string>("");
  const [patronHistory, setPatronHistory] = useState<PatronLoanHistory | null>(null);

  // Yearly statistics state
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [yearlyStats, setYearlyStats] = useState<YearlyStatistics | null>(null);

  // Generate year options (last 5 years)
  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 5 }, (_, i) => currentYear - i);

  // Fetch patrons for dropdown
  useEffect(() => {
    fetch("/api/python/reports/patrons")
      .then((res) => res.json())
      .then((data) => setPatrons(data))
      .catch(console.error);
  }, []);

  // Fetch patron history when selected
  const fetchPatronHistory = useCallback(async (patronId: string) => {
    if (!patronId) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/python/reports/patron/${patronId}/loans`);
      if (res.ok) {
        const data = await res.json();
        setPatronHistory(data);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch yearly statistics
  const fetchYearlyStats = useCallback(async (year: number) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/python/reports/statistics/yearly?year=${year}`);
      if (res.ok) {
        const data = await res.json();
        setYearlyStats(data);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load yearly stats when tab changes or year changes
  useEffect(() => {
    if (activeTab === "yearly") {
      fetchYearlyStats(selectedYear);
    }
  }, [activeTab, selectedYear, fetchYearlyStats]);

  const handlePatronSelect = (patronId: string) => {
    setSelectedPatronId(patronId);
    fetchPatronHistory(patronId);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge variant="default">{t("status.active")}</Badge>;
      case "returned":
        return <Badge variant="secondary">{t("status.returned")}</Badge>;
      case "overdue":
        return <Badge variant="destructive">{t("status.overdue")}</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const monthNames = [
    t("months.jan"), t("months.feb"), t("months.mar"), t("months.apr"),
    t("months.may"), t("months.jun"), t("months.jul"), t("months.aug"),
    t("months.sep"), t("months.oct"), t("months.nov"), t("months.dec"),
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t("title")}</h1>
        <p className="text-muted-foreground">{t("description")}</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2">
        <Button
          variant={activeTab === "patron" ? "default" : "outline"}
          onClick={() => setActiveTab("patron")}
        >
          <Users className="mr-2 h-4 w-4" />
          {t("patronHistory.title")}
        </Button>
        <Button
          variant={activeTab === "yearly" ? "default" : "outline"}
          onClick={() => setActiveTab("yearly")}
        >
          <BarChart3 className="mr-2 h-4 w-4" />
          {t("yearlyStats.title")}
        </Button>
      </div>

      {/* Patron History Tab */}
      {activeTab === "patron" && (
        <Card>
          <CardHeader>
            <CardTitle>{t("patronHistory.title")}</CardTitle>
            <CardDescription>{t("patronHistory.description")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Patron Selector */}
            <div className="flex items-center gap-4">
              <Select value={selectedPatronId} onValueChange={handlePatronSelect}>
                <SelectTrigger className="w-80">
                  <SelectValue placeholder={t("patronHistory.selectPatron")} />
                </SelectTrigger>
                <SelectContent>
                  {patrons.map((patron) => (
                    <SelectItem key={patron.id} value={patron.id}>
                      {patron.name} ({patron.membership_id})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {loading && (
              <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            )}

            {patronHistory && !loading && (
              <>
                {/* Summary */}
                <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
                  <div className="p-4 bg-muted rounded-lg text-center">
                    <p className="text-2xl font-bold">{patronHistory.total_loans}</p>
                    <p className="text-sm text-muted-foreground">{t("patronHistory.totalLoans")}</p>
                  </div>
                  <div className="p-4 bg-muted rounded-lg text-center">
                    <p className="text-2xl font-bold">{patronHistory.active_loans}</p>
                    <p className="text-sm text-muted-foreground">{t("patronHistory.activeLoans")}</p>
                  </div>
                </div>

                {/* Loans Table */}
                {patronHistory.loans.length > 0 ? (
                  <div className="border rounded-lg">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>{t("table.catalogId")}</TableHead>
                          <TableHead>{t("table.title")}</TableHead>
                          <TableHead>{t("table.author")}</TableHead>
                          <TableHead>{t("table.checkoutDate")}</TableHead>
                          <TableHead>{t("table.returnDate")}</TableHead>
                          <TableHead>{t("table.status")}</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {patronHistory.loans.map((loan) => (
                          <TableRow key={loan.loan_id}>
                            <TableCell className="font-mono">{loan.catalog_id}</TableCell>
                            <TableCell>{loan.title}</TableCell>
                            <TableCell>{loan.author || "-"}</TableCell>
                            <TableCell>{formatDate(loan.checkout_date)}</TableCell>
                            <TableCell>
                              {loan.return_date ? formatDate(loan.return_date) : "-"}
                            </TableCell>
                            <TableCell>{getStatusBadge(loan.status)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">
                    {t("patronHistory.noLoans")}
                  </p>
                )}
              </>
            )}

            {!patronHistory && !loading && selectedPatronId && (
              <p className="text-center text-muted-foreground py-8">
                {t("patronHistory.noLoans")}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Yearly Statistics Tab */}
      {activeTab === "yearly" && (
        <Card>
          <CardHeader>
            <CardTitle>{t("yearlyStats.title")}</CardTitle>
            <CardDescription>{t("yearlyStats.description")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Year Selector */}
            <div className="flex items-center gap-4">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <Select
                value={String(selectedYear)}
                onValueChange={(v) => setSelectedYear(parseInt(v))}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {yearOptions.map((year) => (
                    <SelectItem key={year} value={String(year)}>
                      {year}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {loading && (
              <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              </div>
            )}

            {yearlyStats && !loading && (
              <>
                {/* Summary Cards */}
                <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
                  <div className="p-4 bg-blue-50 rounded-lg text-center">
                    <p className="text-3xl font-bold text-blue-600">{yearlyStats.total_loans}</p>
                    <p className="text-sm text-muted-foreground">{t("yearlyStats.totalLoans")}</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg text-center">
                    <p className="text-3xl font-bold text-green-600">{yearlyStats.unique_books}</p>
                    <p className="text-sm text-muted-foreground">{t("yearlyStats.uniqueBooks")}</p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg text-center">
                    <p className="text-3xl font-bold text-purple-600">{yearlyStats.unique_patrons}</p>
                    <p className="text-sm text-muted-foreground">{t("yearlyStats.uniquePatrons")}</p>
                  </div>
                </div>

                {/* Monthly Breakdown */}
                <div>
                  <h4 className="font-medium mb-3">{t("yearlyStats.monthlyBreakdown")}</h4>
                  <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-12 gap-2">
                    {yearlyStats.monthly_breakdown.map((m) => (
                      <div key={m.month} className="text-center p-2 bg-muted rounded">
                        <p className="text-xs text-muted-foreground">{monthNames[m.month - 1]}</p>
                        <p className="font-bold">{m.count}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Top Borrowed Books */}
                {yearlyStats.top_borrowed_books.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-3">{t("yearlyStats.topBooks")}</h4>
                    <div className="border rounded-lg">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead className="w-12">#</TableHead>
                            <TableHead>{t("table.catalogId")}</TableHead>
                            <TableHead>{t("table.title")}</TableHead>
                            <TableHead>{t("table.author")}</TableHead>
                            <TableHead className="text-right">{t("table.loanCount")}</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {yearlyStats.top_borrowed_books.map((book, index) => (
                            <TableRow key={book.item_id}>
                              <TableCell className="font-bold">{index + 1}</TableCell>
                              <TableCell className="font-mono">{book.catalog_id}</TableCell>
                              <TableCell>{book.title}</TableCell>
                              <TableCell>{book.author || "-"}</TableCell>
                              <TableCell className="text-right font-bold">{book.loan_count}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                )}

                {yearlyStats.total_loans === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    {t("yearlyStats.noData")}
                  </p>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
