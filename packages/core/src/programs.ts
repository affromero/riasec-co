/**
 * programs.ts — SNIES program data loader
 *
 * Loads the canonical programs.csv into typed Program objects.
 */

import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import type { Program, TypeMapping, RIASECType } from "./types.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

const DATA_DIR = resolve(__dirname, "../../data/canonical");
const DATA_DIR_ALT = resolve(__dirname, "../../../data/canonical");

function findDataDir(): string {
  try {
    readFileSync(resolve(DATA_DIR, "programs.csv"), { encoding: "utf-8", flag: "r" });
    return DATA_DIR;
  } catch {
    return DATA_DIR_ALT;
  }
}

let cachedPrograms: Program[] | null = null;
let cachedMapping: Record<RIASECType, TypeMapping> | null = null;

/** Parse a CSV line handling quoted fields */
function parseCSVLine(line: string): string[] {
  const result: string[] = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"') {
        if (i + 1 < line.length && line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        current += ch;
      }
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === ",") {
      result.push(current);
      current = "";
    } else {
      current += ch;
    }
  }
  result.push(current);
  return result;
}

/** Load all programs from canonical CSV */
export function loadPrograms(): Program[] {
  if (cachedPrograms) return cachedPrograms;

  const dataDir = findDataDir();
  const csv = readFileSync(resolve(dataDir, "programs.csv"), "utf-8");
  const lines = csv.trim().split("\n");
  const headers = parseCSVLine(lines[0]);

  const programs: Program[] = [];
  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i]);
    const row: Record<string, string> = {};
    for (let j = 0; j < headers.length; j++) {
      row[headers[j]] = values[j] ?? "";
    }

    programs.push({
      codigo_institucion_padre: row.codigo_institucion_padre,
      codigo_snies: parseInt(row.codigo_snies, 10),
      nombre_programa: row.nombre_programa,
      codigo_institucion: row.codigo_institucion,
      nombre_institucion: row.nombre_institucion,
      estado: row.estado as "Activo" | "Inactivo",
      estado_institucion: row.estado_institucion,
      caracter_academico: row.caracter_academico,
      sector: row.sector,
      nivel_academico: row.nivel_academico,
      nivel_formacion: row.nivel_formacion,
      modalidad: row.modalidad,
      titulo_otorgado: row.titulo_otorgado,
      reconocimiento: row.reconocimiento || null,
      cine_amplio: row.cine_amplio,
      cine_especifico: row.cine_especifico,
      cine_detallado: row.cine_detallado,
      area_conocimiento: row.area_conocimiento,
      nucleo_conocimiento: row.nucleo_conocimiento,
      departamento: row.departamento,
      municipio: row.municipio,
      creditos: row.creditos ? parseInt(row.creditos, 10) : null,
      periodos_duracion: row.periodos_duracion ? parseInt(row.periodos_duracion, 10) : null,
      periodicidad: row.periodicidad || null,
      periodicidad_admisiones: row.periodicidad_admisiones || null,
      costo_matricula: row.costo_matricula ? parseFloat(row.costo_matricula) : null,
      en_convenio: row.en_convenio || null,
      vigencia_anos: row.vigencia_anos || null,
      ciclos_propedeuticos: row.ciclos_propedeuticos || null,
      fecha_registro_snies: row.fecha_registro_snies || null,
    });
  }

  cachedPrograms = programs;
  return programs;
}

/** Load the RIASEC → CINE field mapping */
export function loadMapping(): Record<RIASECType, TypeMapping> {
  if (cachedMapping) return cachedMapping;

  const dataDir = findDataDir();
  const raw = readFileSync(resolve(dataDir, "mapping.json"), "utf-8");
  const data = JSON.parse(raw);
  cachedMapping = data.mapping as Record<RIASECType, TypeMapping>;
  return cachedMapping;
}

/** Get unique CINE broad fields from programs */
export function getCINEFields(programs: Program[]): string[] {
  return [...new Set(programs.map((p) => p.cine_amplio))].filter(Boolean).sort();
}

/** Get unique departments from programs */
export function getDepartments(programs: Program[]): string[] {
  return [...new Set(programs.map((p) => p.departamento))].filter(Boolean).sort();
}
