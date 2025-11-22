"use client";

import { useRouter } from "next/navigation";
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

  const handleDelete = async (patronId: string) => {
    if (!confirm("Are you sure you want to delete this patron?")) {
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
      alert("Failed to delete patron");
    }
  };

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
                    {patron.status}
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
                          router.push(`/admin/patrons/${patron.id}`)
                        }
                      >
                        <Eye className="mr-2 h-4 w-4" />
                        Details
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() =>
                          router.push(`/admin/patrons/${patron.id}/edit`)
                        }
                      >
                        <Pencil className="mr-2 h-4 w-4" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={() => handleDelete(patron.id)}
                        className="text-destructive focus:text-destructive"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
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
