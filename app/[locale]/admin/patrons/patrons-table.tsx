"use client";

import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/navigation";
import { MoreHorizontal, Eye, Pencil, Trash2 } from "lucide-react";
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

interface Patron {
  id: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  address?: string;
  birthdate?: string;
  membership_id: string;
  status: "active" | "inactive" | "suspended";
  created_at: string;
  updated_at: string;
}

interface PatronsTableProps {
  patrons: Patron[];
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

export function PatronsTable({ patrons }: PatronsTableProps) {
  const router = useRouter();
  const t = useTranslations("patrons");
  const tCommon = useTranslations("common");

  const handleDelete = async (patronId: string) => {
    if (!confirm(t("confirmDelete"))) {
      return;
    }

    try {
      const res = await fetch(`/api/python/patrons/${patronId}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        throw new Error("Failed to delete patron");
      }

      router.refresh();
    } catch (error) {
      console.error("Error deleting patron:", error);
      alert(tCommon("error"));
    }
  };

  if (patrons.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <p className="text-muted-foreground">{t("noPatronsFound")}</p>
          <p className="text-sm text-muted-foreground">
            {t("addFirstPatron")}
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("allPatrons")} ({patrons.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("membershipId")}</TableHead>
              <TableHead>{t("name")}</TableHead>
              <TableHead>{t("email")}</TableHead>
              <TableHead>{t("phone")}</TableHead>
              <TableHead>{t("status")}</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {patrons.map((patron) => (
              <TableRow key={patron.id}>
                <TableCell className="font-mono text-sm">
                  {patron.membership_id}
                </TableCell>
                <TableCell className="font-medium">
                  {patron.first_name} {patron.last_name}
                </TableCell>
                <TableCell>{patron.email || "-"}</TableCell>
                <TableCell>{patron.phone || "-"}</TableCell>
                <TableCell>
                  <Badge variant={getStatusBadgeVariant(patron.status)}>
                    {t(`statuses.${patron.status}`)}
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
                          router.push(`/admin/patrons/${patron.id}`)
                        }
                      >
                        <Eye className="mr-2 h-4 w-4" />
                        {tCommon("details")}
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() =>
                          router.push(`/admin/patrons/${patron.id}/edit`)
                        }
                      >
                        <Pencil className="mr-2 h-4 w-4" />
                        {tCommon("edit")}
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={() => handleDelete(patron.id)}
                        className="text-destructive focus:text-destructive"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        {tCommon("delete")}
                      </DropdownMenuItem>
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
