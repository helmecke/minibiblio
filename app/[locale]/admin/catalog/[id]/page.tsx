import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Pencil } from "lucide-react";
import { getTranslations } from "next-intl/server";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { CheckoutItemDialog } from "./checkout-item-dialog";

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

interface BookLoanRecord {
  loan_id: string;
  patron_id: string;
  membership_id: string;
  patron_name: string;
  checkout_date: string;
  due_date: string;
  return_date: string | null;
  status: string;
}

interface BookLoanHistory {
  item_id: string;
  catalog_id: string;
  title: string;
  author: string | null;
  total_loans: number;
  loans: BookLoanRecord[];
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

async function getBookLoanHistory(id: string): Promise<BookLoanHistory | null> {
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/python/reports/book/${id}/loans`, {
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

export default async function CatalogItemDetailsPage({
  params,
}: {
  params: Promise<{ id: string; locale: string }>;
}) {
  const { id } = await params;
  const [item, loanHistory, t, tReports] = await Promise.all([
    getCatalogItem(id),
    getBookLoanHistory(id),
    getTranslations("catalog"),
    getTranslations("reports"),
  ]);

  if (!item) {
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
            <Link href="/admin/catalog">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{item.title}</h1>
            <p className="text-muted-foreground font-mono">{item.catalog_id}</p>
          </div>
        </div>
        <div className="flex gap-2">
          {item.status === "available" && (
            <CheckoutItemDialog
              itemId={item.id}
              itemTitle={item.title}
              catalogId={item.catalog_id}
            />
          )}
          <Button asChild>
            <Link href={`/admin/catalog/${item.id}/edit`}>
              <Pencil className="mr-2 h-4 w-4" />
              {t("editItem")}
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t("itemDetails")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Badge variant={getTypeBadgeVariant(item.type)}>{t(`types.${item.type}`)}</Badge>
              <Badge variant={getStatusBadgeVariant(item.status)}>
                {t(`statuses.${item.status}`)}
              </Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">{t("author")}</p>
              <p className="text-sm">{item.author || "-"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">{t("isbn")}</p>
              <p className="text-sm font-mono">{item.isbn || "-"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                {t("publisher")}
              </p>
              <p className="text-sm">{item.publisher || "-"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">{t("year")}</p>
              <p className="text-sm">{item.year || "-"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">{t("genre")}</p>
              <p className="text-sm">{item.genre || "-"}</p>
            </div>
            {item.description && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  {t("description_field")}
                </p>
                <p className="text-sm">{item.description}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("availability")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                {t("language")}
              </p>
              <p className="text-sm">{item.language}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                {t("location")}
              </p>
              <p className="text-sm">{item.location || "-"}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                {t("added")}
              </p>
              <p className="text-sm">{formatDate(item.created_at)}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Loan History */}
      <Card>
        <CardHeader>
          <CardTitle>{tReports("bookHistory.title")}</CardTitle>
          <CardDescription>
            {loanHistory && (
              <span>{tReports("bookHistory.totalLoans")}: {loanHistory.total_loans}</span>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loanHistory && loanHistory.loans.length > 0 ? (
            <div className="border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{tReports("table.patron")}</TableHead>
                    <TableHead>{tReports("table.checkoutDate")}</TableHead>
                    <TableHead>{tReports("table.returnDate")}</TableHead>
                    <TableHead>{tReports("table.status")}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loanHistory.loans.map((loan) => (
                    <TableRow key={loan.loan_id}>
                      <TableCell>
                        <Link
                          href={`/admin/patrons/${loan.patron_id}`}
                          className="hover:underline"
                        >
                          {loan.patron_name}
                        </Link>
                        <span className="text-muted-foreground text-xs ml-2">
                          ({loan.membership_id})
                        </span>
                      </TableCell>
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
              {tReports("bookHistory.noLoans")}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
