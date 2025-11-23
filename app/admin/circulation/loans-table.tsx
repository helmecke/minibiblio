"use client";

import { useRouter } from "next/navigation";
import { MoreHorizontal, Eye, RotateCcw, CalendarPlus } from "lucide-react";
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

interface LoansTableProps {
  loans: Loan[];
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

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString();
}

function isOverdue(dueDate: string, status: string) {
  if (status !== "active") return false;
  return new Date(dueDate) < new Date();
}

export function LoansTable({ loans }: LoansTableProps) {
  const router = useRouter();

  const handleReturn = async (loanId: string) => {
    if (!confirm("Mark this item as returned?")) {
      return;
    }

    try {
      const res = await fetch(`/api/python/loans/${loanId}/return`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });

      if (!res.ok) {
        throw new Error("Failed to return item");
      }

      router.refresh();
    } catch (error) {
      console.error("Error returning item:", error);
      alert("Failed to return item");
    }
  };

  const handleExtend = async (loanId: string) => {
    if (!confirm("Extend this loan by 7 days?")) {
      return;
    }

    try {
      const res = await fetch(`/api/python/loans/${loanId}/extend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ additional_days: 7 }),
      });

      if (!res.ok) {
        throw new Error("Failed to extend loan");
      }

      router.refresh();
    } catch (error) {
      console.error("Error extending loan:", error);
      alert("Failed to extend loan");
    }
  };

  if (loans.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <p className="text-muted-foreground">No loans found</p>
          <p className="text-sm text-muted-foreground">
            Check out an item to a patron to get started
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>All Loans ({loans.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Loan ID</TableHead>
              <TableHead>Item</TableHead>
              <TableHead>Patron</TableHead>
              <TableHead>Checkout</TableHead>
              <TableHead>Due Date</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loans.map((loan) => (
              <TableRow key={loan.id}>
                <TableCell className="font-mono text-sm">
                  {loan.loan_id}
                </TableCell>
                <TableCell className="max-w-[200px]">
                  <div className="truncate font-medium">
                    {loan.catalog_item.title}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {loan.catalog_item.catalog_id}
                  </div>
                </TableCell>
                <TableCell>
                  <div>
                    {loan.patron.first_name} {loan.patron.last_name}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {loan.patron.membership_id}
                  </div>
                </TableCell>
                <TableCell>{formatDate(loan.checkout_date)}</TableCell>
                <TableCell
                  className={
                    isOverdue(loan.due_date, loan.status)
                      ? "text-destructive font-medium"
                      : ""
                  }
                >
                  {formatDate(loan.due_date)}
                </TableCell>
                <TableCell>
                  <Badge
                    variant={
                      isOverdue(loan.due_date, loan.status)
                        ? "destructive"
                        : getStatusBadgeVariant(loan.status)
                    }
                  >
                    {isOverdue(loan.due_date, loan.status)
                      ? "overdue"
                      : loan.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreHorizontal className="h-4 w-4" />
                        <span className="sr-only">Open menu</span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={() =>
                          router.push(`/admin/circulation/${loan.id}`)
                        }
                      >
                        <Eye className="mr-2 h-4 w-4" />
                        Details
                      </DropdownMenuItem>
                      {loan.status === "active" && (
                        <>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem onClick={() => handleExtend(loan.id)}>
                            <CalendarPlus className="mr-2 h-4 w-4" />
                            Extend (7 days)
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleReturn(loan.id)}>
                            <RotateCcw className="mr-2 h-4 w-4" />
                            Return
                          </DropdownMenuItem>
                        </>
                      )}
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
