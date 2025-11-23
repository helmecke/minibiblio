import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Pencil } from "lucide-react";
import { getTranslations } from "next-intl/server";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

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

async function getPatron(id: string): Promise<Patron | null> {
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/python/patrons/${id}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

async function getPatronLoanHistory(id: string): Promise<PatronLoanHistory | null> {
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/python/reports/patron/${id}/loans`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

function getStatusBadgeVariant(status: Patron["status"]) {
  switch (status) {
    case "active":
      return "success";
    case "inactive":
      return "secondary";
    case "suspended":
      return "destructive";
    default:
      return "outline";
  }
}

function getLoanStatusBadgeVariant(status: string) {
  switch (status) {
    case "active":
      return "default";
    case "returned":
      return "secondary";
    case "overdue":
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

export default async function PatronDetailsPage({
  params,
}: {
  params: Promise<{ id: string; locale: string }>;
}) {
  const { id } = await params;
  const [patron, loanHistory, t, tReports] = await Promise.all([
    getPatron(id),
    getPatronLoanHistory(id),
    getTranslations("patrons"),
    getTranslations("reports"),
  ]);

  if (!patron) {
    notFound();
  }

  const formatLoanDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/admin/patrons">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {patron.first_name} {patron.last_name}
            </h1>
            <p className="text-muted-foreground font-mono">
              {patron.membership_id}
            </p>
          </div>
        </div>
        <Button asChild>
          <Link href={`/admin/patrons/${patron.id}/edit`}>
            <Pencil className="mr-2 h-4 w-4" />
            {t("editPatron")}
          </Link>
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t("contactInfo")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">{t("email")}</p>
              <p className="text-sm">{patron.email || "-"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">{t("phone")}</p>
              <p className="text-sm">{patron.phone || "-"}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("patronDetails")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                {t("status")}
              </p>
              <Badge variant={getStatusBadgeVariant(patron.status)}>
                {t(`statuses.${patron.status}`)}
              </Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                {t("created")}
              </p>
              <p className="text-sm">{formatDate(patron.created_at)}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                {t("updated")}
              </p>
              <p className="text-sm">{formatDate(patron.updated_at)}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Loan History */}
      <Card>
        <CardHeader>
          <CardTitle>{tReports("patronHistory.title")}</CardTitle>
          <CardDescription>
            {loanHistory && (
              <span className="flex gap-4">
                <span>{tReports("patronHistory.totalLoans")}: {loanHistory.total_loans}</span>
                <span>{tReports("patronHistory.activeLoans")}: {loanHistory.active_loans}</span>
              </span>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loanHistory && loanHistory.loans.length > 0 ? (
            <div className="border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{tReports("table.catalogId")}</TableHead>
                    <TableHead>{tReports("table.title")}</TableHead>
                    <TableHead>{tReports("table.author")}</TableHead>
                    <TableHead>{tReports("table.checkoutDate")}</TableHead>
                    <TableHead>{tReports("table.returnDate")}</TableHead>
                    <TableHead>{tReports("table.status")}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loanHistory.loans.map((loan) => (
                    <TableRow key={loan.loan_id}>
                      <TableCell className="font-mono">{loan.catalog_id}</TableCell>
                      <TableCell>{loan.title}</TableCell>
                      <TableCell>{loan.author || "-"}</TableCell>
                      <TableCell>{formatLoanDate(loan.checkout_date)}</TableCell>
                      <TableCell>
                        {loan.return_date ? formatLoanDate(loan.return_date) : "-"}
                      </TableCell>
                      <TableCell>
                        <Badge variant={getLoanStatusBadgeVariant(loan.status)}>
                          {tReports(`status.${loan.status}`)}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">
              {tReports("patronHistory.noLoans")}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
