import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoanActions } from "./loan-actions";

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
  created_at: string;
  updated_at: string;
}

async function getLoan(id: string): Promise<Loan | null> {
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/python/loans/${id}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

function getStatusBadgeVariant(status: Loan["status"]) {
  switch (status) {
    case "active":
      return "default";
    case "returned":
      return "success";
    case "overdue":
      return "destructive";
    case "lost":
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
  });
}

function formatDateTime(dateString: string) {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function isOverdue(dueDate: string, status: string) {
  if (status !== "active") return false;
  return new Date(dueDate) < new Date();
}

export default async function LoanDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const loan = await getLoan(id);

  if (!loan) {
    notFound();
  }

  const overdue = isOverdue(loan.due_date, loan.status);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/admin/circulation">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Loan Details</h1>
            <p className="text-muted-foreground font-mono">{loan.loan_id}</p>
          </div>
        </div>
        {loan.status === "active" && <LoanActions loanId={loan.id} />}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Loan Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Badge variant={overdue ? "destructive" : getStatusBadgeVariant(loan.status)}>
                {overdue ? "overdue" : loan.status}
              </Badge>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Checkout Date
              </p>
              <p className="text-sm">{formatDate(loan.checkout_date)}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Due Date
              </p>
              <p className={`text-sm ${overdue ? "text-destructive font-medium" : ""}`}>
                {formatDate(loan.due_date)}
              </p>
            </div>
            {loan.return_date && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Return Date
                </p>
                <p className="text-sm">{formatDate(loan.return_date)}</p>
              </div>
            )}
            {loan.notes && (
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Notes
                </p>
                <p className="text-sm whitespace-pre-wrap">{loan.notes}</p>
              </div>
            )}
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Created
              </p>
              <p className="text-sm">{formatDateTime(loan.created_at)}</p>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Item</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Title
                </p>
                <p className="text-sm font-medium">{loan.catalog_item.title}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Catalog ID
                </p>
                <p className="text-sm font-mono">{loan.catalog_item.catalog_id}</p>
              </div>
              {loan.catalog_item.author && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Author
                  </p>
                  <p className="text-sm">{loan.catalog_item.author}</p>
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-muted-foreground">Type</p>
                <p className="text-sm capitalize">{loan.catalog_item.type}</p>
              </div>
              <Button variant="outline" size="sm" asChild>
                <Link href={`/admin/catalog/${loan.catalog_item.id}`}>
                  View Item Details
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Patron</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Name</p>
                <p className="text-sm">
                  {loan.patron.first_name} {loan.patron.last_name}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Membership ID
                </p>
                <p className="text-sm font-mono">{loan.patron.membership_id}</p>
              </div>
              <Button variant="outline" size="sm" asChild>
                <Link href={`/admin/patrons/${loan.patron.id}`}>
                  View Patron Details
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
