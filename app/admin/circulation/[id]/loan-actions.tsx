"use client";

import { useRouter } from "next/navigation";
import { RotateCcw, CalendarPlus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface LoanActionsProps {
  loanId: string;
}

export function LoanActions({ loanId }: LoanActionsProps) {
  const router = useRouter();

  const handleReturn = async () => {
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

  const handleExtend = async () => {
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

  return (
    <div className="flex gap-2">
      <Button variant="outline" onClick={handleExtend}>
        <CalendarPlus className="mr-2 h-4 w-4" />
        Extend (7 days)
      </Button>
      <Button onClick={handleReturn}>
        <RotateCcw className="mr-2 h-4 w-4" />
        Return
      </Button>
    </div>
  );
}
