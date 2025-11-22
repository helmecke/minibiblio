"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Patron {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  membership_id: string;
  status: "active" | "inactive" | "suspended";
  borrowing_limit: number;
  current_borrowed_count: number;
  notes?: string;
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
  if (patrons.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-10">
          <p className="text-muted-foreground">No patrons found</p>
          <p className="text-sm text-muted-foreground">
            Add your first patron to get started
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>All Patrons ({patrons.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Member ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Phone</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Borrowed</TableHead>
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
                <TableCell>{patron.email}</TableCell>
                <TableCell>{patron.phone || "-"}</TableCell>
                <TableCell>
                  <Badge variant={getStatusBadgeVariant(patron.status)}>
                    {patron.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  {patron.current_borrowed_count} / {patron.borrowing_limit}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
