"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

interface Patron {
  id: string;
  membership_id: string;
  first_name: string;
  last_name: string;
  status: string;
}

interface CatalogItem {
  id: string;
  catalog_id: string;
  title: string;
  author?: string;
  status: string;
}

export function CheckoutDialog() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [patrons, setPatrons] = useState<Patron[]>([]);
  const [items, setItems] = useState<CatalogItem[]>([]);
  const [formData, setFormData] = useState({
    patron_id: "",
    catalog_item_id: "",
    due_days: "14",
    notes: "",
  });

  useEffect(() => {
    if (open) {
      // Fetch active patrons
      fetch("/api/python/patrons?status=active")
        .then((res) => res.json())
        .then((data) => setPatrons(data))
        .catch((err) => console.error("Error fetching patrons:", err));

      // Fetch available items
      fetch("/api/python/catalog?status=available")
        .then((res) => res.json())
        .then((data) => setItems(data))
        .catch((err) => console.error("Error fetching catalog items:", err));
    }
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        patron_id: formData.patron_id,
        catalog_item_id: formData.catalog_item_id,
        due_days: parseInt(formData.due_days),
        notes: formData.notes || null,
      };

      const res = await fetch("/api/python/loans/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to checkout item");
      }

      setOpen(false);
      setFormData({
        patron_id: "",
        catalog_item_id: "",
        due_days: "14",
        notes: "",
      });
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" className="h-8 gap-1">
          <PlusCircle className="h-3.5 w-3.5" />
          <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">
            Checkout
          </span>
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[525px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Checkout Item</DialogTitle>
            <DialogDescription>
              Check out an item to a patron.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            {error && (
              <div className="text-sm text-destructive bg-destructive/10 p-2 rounded">
                {error}
              </div>
            )}

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="patron" className="text-right">
                Patron
              </Label>
              <Select
                value={formData.patron_id}
                onValueChange={(value) =>
                  setFormData({ ...formData, patron_id: value })
                }
                required
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select patron" />
                </SelectTrigger>
                <SelectContent>
                  {patrons.map((patron) => (
                    <SelectItem key={patron.id} value={patron.id}>
                      {patron.first_name} {patron.last_name} ({patron.membership_id})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="item" className="text-right">
                Item
              </Label>
              <Select
                value={formData.catalog_item_id}
                onValueChange={(value) =>
                  setFormData({ ...formData, catalog_item_id: value })
                }
                required
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select item" />
                </SelectTrigger>
                <SelectContent>
                  {items.map((item) => (
                    <SelectItem key={item.id} value={item.id}>
                      {item.title} ({item.catalog_id})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="due_days" className="text-right">
                Loan Period
              </Label>
              <Select
                value={formData.due_days}
                onValueChange={(value) =>
                  setFormData({ ...formData, due_days: value })
                }
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select period" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">7 days</SelectItem>
                  <SelectItem value="14">14 days (default)</SelectItem>
                  <SelectItem value="21">21 days</SelectItem>
                  <SelectItem value="28">28 days</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="notes" className="text-right">
                Notes
              </Label>
              <Textarea
                id="notes"
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
                className="col-span-3"
                placeholder="Optional notes"
                rows={2}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="submit"
              disabled={loading || !formData.patron_id || !formData.catalog_item_id}
            >
              {loading ? "Processing..." : "Checkout"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
