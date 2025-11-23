"use client";

import { useState, useCallback } from "react";
import { useTranslations } from "next-intl";
import { Upload, FileSpreadsheet, CheckCircle2, AlertCircle, AlertTriangle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface CSVPreviewRow {
  row_number: number;
  title: string | null;
  author: string | null;
  publisher: string | null;
  genre: string | null;
  catalog_id: string | null;
  isbn: string | null;
  status: "valid" | "warning" | "error";
  errors: string[];
  warnings: string[];
}

interface CSVPreviewResponse {
  total_rows: number;
  valid_rows: number;
  warning_rows: number;
  error_rows: number;
  columns_detected: string[];
  has_author_column: boolean;
  has_publisher_column: boolean;
  rows: CSVPreviewRow[];
}

interface ImportResult {
  success_count: number;
  skipped_count: number;
  updated_count: number;
  error_count: number;
  errors: Array<{
    row_number: number;
    catalog_id: string | null;
    title: string | null;
    error: string;
  }>;
}

type DuplicateHandling = "skip" | "update" | "create";

export default function ImportPage() {
  const t = useTranslations("import");
  const tCommon = useTranslations("common");
  const tErrors = useTranslations("errors");

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<CSVPreviewResponse | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [duplicateHandling, setDuplicateHandling] = useState<DuplicateHandling>("skip");

  const handleFileSelect = useCallback(async (selectedFile: File) => {
    setFile(selectedFile);
    setPreview(null);
    setResult(null);
    setError(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const res = await fetch("/api/python/import/catalog/preview", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to preview file");
      }

      const data: CSVPreviewResponse = await res.json();
      setPreview(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : tErrors("anErrorOccurred"));
    } finally {
      setLoading(false);
    }
  }, [tErrors]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.name.endsWith(".csv")) {
      handleFileSelect(droppedFile);
    }
  }, [handleFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  }, [handleFileSelect]);

  const handleImport = useCallback(async () => {
    if (!file) return;

    setImporting(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const params = new URLSearchParams({
        duplicate_handling: duplicateHandling,
        default_language: "German",
      });

      const res = await fetch(`/api/python/import/catalog?${params}`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Import failed");
      }

      const data: ImportResult = await res.json();
      setResult(data);
      setPreview(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : tErrors("anErrorOccurred"));
    } finally {
      setImporting(false);
    }
  }, [file, duplicateHandling, tErrors]);

  const resetImport = useCallback(() => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  }, []);

  const getStatusIcon = (status: "valid" | "warning" | "error") => {
    switch (status) {
      case "valid":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t("title")}</h1>
        <p className="text-muted-foreground">{t("description")}</p>
      </div>

      {/* File Upload */}
      {!preview && !result && (
        <Card>
          <CardHeader>
            <CardTitle>{t("upload")}</CardTitle>
            <CardDescription>{t("uploadDescription")}</CardDescription>
          </CardHeader>
          <CardContent>
            <div
              className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:border-primary transition-colors"
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => document.getElementById("file-input")?.click()}
            >
              {loading ? (
                <div className="flex flex-col items-center gap-2">
                  <Loader2 className="h-10 w-10 text-muted-foreground animate-spin" />
                  <p className="text-sm text-muted-foreground">{t("processing")}</p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2">
                  <Upload className="h-10 w-10 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">{t("dropOrClick")}</p>
                  <p className="text-xs text-muted-foreground">{t("csvOnly")}</p>
                </div>
              )}
              <input
                id="file-input"
                type="file"
                accept=".csv"
                className="hidden"
                onChange={handleFileInput}
              />
            </div>
            {error && (
              <p className="mt-4 text-sm text-red-500">{error}</p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Preview */}
      {preview && !result && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileSpreadsheet className="h-5 w-5" />
                {file?.name}
              </CardTitle>
              <CardDescription>
                {t("previewDescription", { count: preview.total_rows })}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Summary */}
              <div className="flex gap-4 mb-4">
                <Badge variant="outline" className="gap-1">
                  <CheckCircle2 className="h-3 w-3 text-green-500" />
                  {t("validRows", { count: preview.valid_rows })}
                </Badge>
                {preview.warning_rows > 0 && (
                  <Badge variant="outline" className="gap-1">
                    <AlertTriangle className="h-3 w-3 text-yellow-500" />
                    {t("warningRows", { count: preview.warning_rows })}
                  </Badge>
                )}
                {preview.error_rows > 0 && (
                  <Badge variant="outline" className="gap-1">
                    <AlertCircle className="h-3 w-3 text-red-500" />
                    {t("errorRows", { count: preview.error_rows })}
                  </Badge>
                )}
              </div>

              {/* Columns detected */}
              <p className="text-sm text-muted-foreground mb-4">
                {t("columnsDetected")}: {preview.columns_detected.join(", ")}
              </p>

              {/* Preview Table */}
              <div className="border rounded-lg max-h-96 overflow-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">#</TableHead>
                      <TableHead className="w-12"></TableHead>
                      <TableHead>{t("inventoryNumber")}</TableHead>
                      <TableHead>{t("titleColumn")}</TableHead>
                      {preview.has_author_column && <TableHead>{t("author")}</TableHead>}
                      {preview.has_publisher_column && <TableHead>{t("publisher")}</TableHead>}
                      <TableHead>{t("genre")}</TableHead>
                      <TableHead>{t("isbn")}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {preview.rows.slice(0, 50).map((row) => (
                      <TableRow key={row.row_number} className={row.status === "error" ? "bg-red-50" : row.status === "warning" ? "bg-yellow-50" : ""}>
                        <TableCell className="text-muted-foreground">{row.row_number}</TableCell>
                        <TableCell>{getStatusIcon(row.status)}</TableCell>
                        <TableCell className="font-mono text-sm">{row.catalog_id || "-"}</TableCell>
                        <TableCell>{row.title || "-"}</TableCell>
                        {preview.has_author_column && <TableCell>{row.author || "-"}</TableCell>}
                        {preview.has_publisher_column && <TableCell>{row.publisher || "-"}</TableCell>}
                        <TableCell>{row.genre || "-"}</TableCell>
                        <TableCell className="font-mono text-sm">{row.isbn || "-"}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              {preview.rows.length > 50 && (
                <p className="text-sm text-muted-foreground mt-2">
                  {t("showingFirst", { shown: 50, total: preview.rows.length })}
                </p>
              )}
            </CardContent>
          </Card>

          {/* Import Options */}
          <Card>
            <CardHeader>
              <CardTitle>{t("options")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>{t("duplicateHandling")}</Label>
                <Select value={duplicateHandling} onValueChange={(v) => setDuplicateHandling(v as DuplicateHandling)}>
                  <SelectTrigger className="w-64">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="skip">{t("duplicates.skip")}</SelectItem>
                    <SelectItem value="update">{t("duplicates.update")}</SelectItem>
                    <SelectItem value="create">{t("duplicates.create")}</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">{t("duplicateDescription")}</p>
              </div>

              <div className="flex gap-2">
                <Button onClick={handleImport} disabled={importing || preview.error_rows === preview.total_rows}>
                  {importing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {t("importing")}
                    </>
                  ) : (
                    t("import")
                  )}
                </Button>
                <Button variant="outline" onClick={resetImport}>
                  {tCommon("cancel")}
                </Button>
              </div>

              {error && (
                <p className="text-sm text-red-500">{error}</p>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Result */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              {t("importComplete")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{result.success_count}</p>
                <p className="text-sm text-muted-foreground">{t("results.created")}</p>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">{result.updated_count}</p>
                <p className="text-sm text-muted-foreground">{t("results.updated")}</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-gray-600">{result.skipped_count}</p>
                <p className="text-sm text-muted-foreground">{t("results.skipped")}</p>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <p className="text-2xl font-bold text-red-600">{result.error_count}</p>
                <p className="text-sm text-muted-foreground">{t("results.errors")}</p>
              </div>
            </div>

            {result.errors.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-medium">{t("errorDetails")}</h4>
                <div className="border rounded-lg max-h-48 overflow-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-16">{t("row")}</TableHead>
                        <TableHead>{t("inventoryNumber")}</TableHead>
                        <TableHead>{t("titleColumn")}</TableHead>
                        <TableHead>{tCommon("error")}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {result.errors.map((err, idx) => (
                        <TableRow key={idx}>
                          <TableCell>{err.row_number}</TableCell>
                          <TableCell className="font-mono text-sm">{err.catalog_id || "-"}</TableCell>
                          <TableCell>{err.title || "-"}</TableCell>
                          <TableCell className="text-red-500">{err.error}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            )}

            <Button onClick={resetImport}>
              {t("importAnother")}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
