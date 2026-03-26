/**
 * update-snies.ts
 *
 * Parses the SNIES HECAA Excel export (.data-raw/programas-export.xlsx)
 * and outputs canonical CSV to data/canonical/programs.csv.
 *
 * Usage: npm run update-snies
 */

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import * as XLSX from "xlsx";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");
const INPUT = resolve(ROOT, ".data-raw/programas-export.xlsx");
const OUTPUT = resolve(ROOT, "data/canonical/programs.csv");

// Column mapping: Excel header → canonical CSV column
const COLUMN_MAP: Record<string, string> = {
  CÓDIGO_SNIES_DEL_PROGRAMA: "codigo_snies",
  NOMBRE_DEL_PROGRAMA: "nombre_programa",
  CÓDIGO_INSTITUCIÓN: "codigo_institucion",
  NOMBRE_INSTITUCIÓN: "nombre_institucion",
  ESTADO_PROGRAMA: "estado",
  ESTADO_INSTITUCIÓN: "estado_institucion",
  CARÁCTER_ACADÉMICO: "caracter_academico",
  SECTOR: "sector",
  NIVEL_ACADÉMICO: "nivel_academico",
  NIVEL_DE_FORMACIÓN: "nivel_formacion",
  MODALIDAD: "modalidad",
  TITULO_OTORGADO: "titulo_otorgado",
  CINE_F_2013_AC_CAMPO_AMPLIO: "cine_amplio",
  CINE_F_2013_AC_CAMPO_ESPECÍFIC: "cine_especifico",
  CINE_F_2013_AC_CAMPO_DETALLADO: "cine_detallado",
  ÁREA_DE_CONOCIMIENTO: "area_conocimiento",
  NÚCLEO_BÁSICO_DEL_CONOCIMIENTO: "nucleo_conocimiento",
  DEPARTAMENTO_OFERTA_PROGRAMA: "departamento",
  MUNICIPIO_OFERTA_PROGRAMA: "municipio",
  NÚMERO_CRÉDITOS: "creditos",
  NÚMERO_PERIODOS_DE_DURACIÓN: "periodos_duracion",
  PERIODICIDAD: "periodicidad",
  COSTO_MATRÍCULA_ESTUD_NUEVOS: "costo_matricula",
  PROGRAMA_EN_CONVENIO: "en_convenio",
};

const CANONICAL_COLUMNS = Object.values(COLUMN_MAP);

function escapeCSV(value: string): string {
  if (value.includes(",") || value.includes('"') || value.includes("\n")) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

function cleanString(v: unknown): string {
  if (v === null || v === undefined) return "";
  return String(v).trim();
}

function cleanNumber(v: unknown): string {
  if (v === null || v === undefined || v === "") return "";
  const n = Number(v);
  return Number.isNaN(n) ? "" : String(n);
}

function cleanInteger(v: unknown): string {
  if (v === null || v === undefined || v === "") return "";
  const n = Number(v);
  return Number.isNaN(n) ? "" : String(Math.round(n));
}

const NUMERIC_COLUMNS = new Set([
  "codigo_snies",
  "creditos",
  "periodos_duracion",
  "costo_matricula",
]);
const INTEGER_COLUMNS = new Set([
  "codigo_snies",
  "creditos",
  "periodos_duracion",
]);

function main() {
  console.log(`Reading ${INPUT}...`);
  const buf = readFileSync(INPUT);
  const wb = XLSX.read(buf, { type: "buffer" });

  const sheetName = wb.SheetNames[0]; // "Programas"
  console.log(`Parsing sheet: ${sheetName}`);
  const sheet = wb.Sheets[sheetName];

  const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, {
    defval: null,
  });
  console.log(`Raw rows: ${rows.length}`);

  // Get original headers to build the mapping
  const headers = Object.keys(rows[0] ?? {});
  console.log(`Columns found: ${headers.length}`);

  // Map headers — some may be truncated in Excel, try prefix matching
  const headerToCanonical = new Map<string, string>();
  for (const h of headers) {
    if (COLUMN_MAP[h]) {
      headerToCanonical.set(h, COLUMN_MAP[h]);
    } else {
      // Try prefix match for truncated headers
      for (const [excelCol, canonical] of Object.entries(COLUMN_MAP)) {
        if (excelCol.startsWith(h) || h.startsWith(excelCol)) {
          headerToCanonical.set(h, canonical);
          break;
        }
      }
    }
  }

  const unmapped = headers.filter((h) => !headerToCanonical.has(h));
  if (unmapped.length > 0) {
    console.log(`Skipping unmapped columns: ${unmapped.join(", ")}`);
  }

  // Transform rows
  const canonical: Record<string, string>[] = [];
  let skipped = 0;

  for (const row of rows) {
    const out: Record<string, string> = {};

    for (const [header, value] of Object.entries(row)) {
      const col = headerToCanonical.get(header);
      if (!col) continue;

      if (INTEGER_COLUMNS.has(col)) {
        out[col] = cleanInteger(value);
      } else if (NUMERIC_COLUMNS.has(col)) {
        out[col] = cleanNumber(value);
      } else {
        out[col] = cleanString(value);
      }
    }

    // Skip rows with no SNIES code (header/footer artifacts)
    if (!out.codigo_snies) {
      skipped++;
      continue;
    }

    canonical.push(out);
  }

  console.log(`Canonical rows: ${canonical.length} (skipped ${skipped})`);

  // Count active programs
  const active = canonical.filter((r) => r.estado === "Activo").length;
  const inactive = canonical.filter((r) => r.estado === "Inactivo").length;
  console.log(`Active: ${active}, Inactive: ${inactive}`);

  // Count by CINE broad field
  const cineCounts = new Map<string, number>();
  for (const row of canonical) {
    const field = row.cine_amplio || "(vacío)";
    cineCounts.set(field, (cineCounts.get(field) ?? 0) + 1);
  }
  console.log("\nCINE broad field distribution:");
  for (const [field, count] of [...cineCounts.entries()].sort(
    (a, b) => b[1] - a[1]
  )) {
    console.log(`  ${count.toString().padStart(6)} ${field}`);
  }

  // Count by department
  const deptCounts = new Map<string, number>();
  for (const row of canonical.filter((r) => r.estado === "Activo")) {
    const dept = row.departamento || "(vacío)";
    deptCounts.set(dept, (deptCounts.get(dept) ?? 0) + 1);
  }
  console.log("\nActive programs by department (top 10):");
  for (const [dept, count] of [...deptCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)) {
    console.log(`  ${count.toString().padStart(6)} ${dept}`);
  }

  // Write CSV
  mkdirSync(dirname(OUTPUT), { recursive: true });

  const csvHeader = CANONICAL_COLUMNS.join(",");
  const csvRows = canonical.map((row) =>
    CANONICAL_COLUMNS.map((col) => escapeCSV(row[col] ?? "")).join(",")
  );

  const csv = [csvHeader, ...csvRows].join("\n") + "\n";
  writeFileSync(OUTPUT, csv, "utf-8");

  const sizeMB = (Buffer.byteLength(csv) / 1024 / 1024).toFixed(1);
  console.log(`\nWrote ${OUTPUT} (${sizeMB} MB, ${canonical.length} rows)`);
}

main();
