"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { useLocale } from "next-intl";
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

interface LoanPeriodSettings {
  default_period: number;
  available_periods: number[];
  extension_period: number;
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

function isOverdue(dueDate: string, status: string) {
  if (status !== "active") return false;
  return new Date(dueDate) < new Date();
}

export function LoansTable({ loans }: LoansTableProps) {
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations("circulation");
  const tCommon = useTranslations("common");
  const [extensionDays, setExtensionDays] = useState(7);

  useEffect(() => {
    // Fetch loan period settings
    fetch("/api/python/settings/loan-periods/config")
      .then((res) => res.json())
      .then((data: LoanPeriodSettings) => {
        setExtensionDays(data.extension_period);
      })
      .catch((err) => console.error("Error fetching loan settings:", err));
  }, []);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString(locale === "de" ? "de-DE" : "en-US");
  };

  const handleReturn = async (loanId: string) => {
    if (!confirm(t("confirmReturn"))) {
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
      alert(tCommon("error"));
    }
  };

  const handleExtend = async (loanId: string) => {
    if (!confirm(t("confirmExtend", { days: extensionDays }))) {
      return;
    }

    try {
      const res = await fetch(`/api/python/loans/${loanId}/extend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ additional_days: extensionDays }),
      });

      if (!res.ok) {
        throw new Error("Failed to extend loan");
      }

      router.refresh();
    } catch (error) {
      console.error("Error extending loan:", error);
      alert(tCommon("error"));
    }
  };

  if (loans.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <p className="text-muted-foreground">{t("noLoansFound")}</p>
          <p className="text-sm text-muted-foreground">
            {t("checkoutFirstItem")}
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("allLoans")} ({loans.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("loanId")}</TableHead>
              <TableHead>{t("item")}</TableHead>
              <TableHead>{t("patron")}</TableHead>
              <TableHead>{t("checkoutDate")}</TableHead>
              <TableHead>{t("dueDate")}</TableHead>
              <TableHead>{t("statuses.active").split(" ")[0]}</TableHead>
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
                      ? t("statuses.overdue")
                      : t(`statuses.${loan.status}`)}
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
                          router.push(`/admin/circulation/${loan.id}`)
                        }
                      >
                        <Eye className="mr-2 h-4 w-4" />
                        {tCommon("details")}
                      </DropdownMenuItem>
                      {loan.status === "active" && (
                        <>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem onClick={() => handleExtend(loan.id)}>
                            <CalendarPlus className="mr-2 h-4 w-4" />
                            {t("extendDays", { days: extensionDays })}
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleReturn(loan.id)}>
                            <RotateCcw className="mr-2 h-4 w-4" />
                            {t("return")}
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
