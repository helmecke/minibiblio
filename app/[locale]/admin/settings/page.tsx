"use client";

import { useState, useEffect, useCallback } from "react";
import { useTranslations } from "next-intl";
import { Save, RotateCcw, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface CatalogIdSettings {
  format: string;
  last_number: number;
  last_year: number;
}

interface CatalogIdPreview {
  next_id: string;
  current_number: number;
  current_year: number;
}

const FORMAT_PRESETS = [
  { value: "{number}/{year}", label: "number/year", example: "255/24" },
  { value: "{year}/{number}", label: "year/number", example: "24/255" },
  { value: "{year}-{number}", label: "year-number", example: "24-255" },
  { value: "CAT-{number}", label: "CAT-number", example: "CAT-255" },
];

export default function SettingsPage() {
  const t = useTranslations("settings");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");

  const [settings, setSettings] = useState<CatalogIdSettings | null>(null);
  const [preview, setPreview] = useState<CatalogIdPreview | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Form state
  const [format, setFormat] = useState("{number}/{year}");
  const [lastNumber, setLastNumber] = useState(0);

  const fetchSettings = useCallback(async () => {
    try {
      const [configRes, previewRes] = await Promise.all([
        fetch("/api/python/settings/catalog-id/config"),
        fetch("/api/python/settings/catalog-id/preview"),
      ]);

      if (configRes.ok) {
        const config: CatalogIdSettings = await configRes.json();
        setSettings(config);
        setFormat(config.format);
        setLastNumber(config.last_number);
      }

      if (previewRes.ok) {
        const previewData: CatalogIdPreview = await previewRes.json();
        setPreview(previewData);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : tErrors("anErrorOccurred"));
    } finally {
      setLoading(false);
    }
  }, [tErrors]);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  // Update preview when format or lastNumber changes
  useEffect(() => {
    if (!settings) return;

    const currentYear = new Date().getFullYear() % 100;
    const nextNumber = settings.last_year !== currentYear ? 1 : lastNumber + 1;

    try {
      const nextId = format
        .replace("{number}", String(nextNumber))
        .replace("{year}", String(currentYear));

      setPreview({
        next_id: nextId,
        current_number: nextNumber,
        current_year: currentYear,
      });
    } catch {
      // Invalid format, keep previous preview
    }
  }, [format, lastNumber, settings]);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      const res = await fetch("/api/python/settings/catalog-id/config", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          format,
          last_number: lastNumber,
          last_year: settings?.last_year || new Date().getFullYear() % 100,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to save settings");
      }

      setSuccess(true);
      await fetchSettings();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (e) {
      setError(e instanceof Error ? e.message : tErrors("anErrorOccurred"));
    } finally {
      setSaving(false);
    }
  };

  const handleResetCounter = async () => {
    setLastNumber(0);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t("title")}</h1>
        <p className="text-muted-foreground">{t("description")}</p>
      </div>

      {/* Catalog ID Settings */}
      <Card>
        <CardHeader>
          <CardTitle>{t("catalogId.title")}</CardTitle>
          <CardDescription>{t("catalogId.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Format Selection */}
          <div className="space-y-2">
            <Label>{t("catalogId.format")}</Label>
            <Select value={format} onValueChange={setFormat}>
              <SelectTrigger className="w-64">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {FORMAT_PRESETS.map((preset) => (
                  <SelectItem key={preset.value} value={preset.value}>
                    {preset.label} ({preset.example})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              {t("catalogId.formatHelp")}
            </p>
          </div>

          {/* Current Counter */}
          <div className="space-y-2">
            <Label>{t("catalogId.currentNumber")}</Label>
            <div className="flex items-center gap-2">
              <Input
                type="number"
                min="0"
                value={lastNumber}
                onChange={(e) => setLastNumber(parseInt(e.target.value) || 0)}
                className="w-32"
              />
              <Button variant="outline" size="sm" onClick={handleResetCounter}>
                <RotateCcw className="h-4 w-4 mr-1" />
                {t("catalogId.reset")}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              {t("catalogId.counterHelp")}
            </p>
          </div>

          {/* Preview */}
          {preview && (
            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground mb-1">{t("catalogId.preview")}</p>
              <p className="text-2xl font-mono font-bold">{preview.next_id}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {t("catalogId.yearInfo", { year: preview.current_year })}
              </p>
            </div>
          )}

          {/* Save Button */}
          <div className="flex items-center gap-4">
            <Button onClick={handleSave} disabled={saving}>
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {t("saving")}
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  {tCommon("save")}
                </>
              )}
            </Button>
            {success && (
              <p className="text-sm text-green-600">{t("saved")}</p>
            )}
            {error && (
              <p className="text-sm text-red-500">{error}</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
