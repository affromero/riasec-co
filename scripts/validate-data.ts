/**
 * validate-data.ts
 *
 * Validates canonical data files against their JSON schemas.
 * Also validates items and mapping JSON for structural correctness.
 *
 * Usage: npm run validate
 */

import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import Ajv from "ajv";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");
const DATA = resolve(ROOT, "data/canonical");
const SCHEMA = resolve(ROOT, "data/schema");

const RIASEC_TYPES = ["R", "I", "A", "S", "E", "C"] as const;
const ITEMS_PER_TYPE = 8;

let errors = 0;

function fail(msg: string) {
  console.error(`  FAIL: ${msg}`);
  errors++;
}

function pass(msg: string) {
  console.log(`  PASS: ${msg}`);
}

function validatePrograms() {
  console.log("\n--- Validating programs.csv ---");

  const csvPath = resolve(DATA, "programs.csv");
  if (!existsSync(csvPath)) {
    fail("programs.csv not found — run `npm run update-snies` first");
    return;
  }

  const schemaPath = resolve(SCHEMA, "programs.schema.json");
  const schema = JSON.parse(readFileSync(schemaPath, "utf-8"));

  const csv = readFileSync(csvPath, "utf-8");
  const lines = csv.trim().split("\n");
  const headers = parseCSVLine(lines[0]);

  pass(`${lines.length - 1} rows, ${headers.length} columns`);

  // Check required columns exist
  const required = schema.required as string[];
  for (const col of required) {
    if (headers.includes(col)) {
      pass(`Required column '${col}' present`);
    } else {
      fail(`Required column '${col}' missing`);
    }
  }

  // Validate a sample of rows with AJV
  const ajv = new Ajv({ allErrors: true, coerceTypes: true, validateSchema: false });
  const validate = ajv.compile(schema);

  let validCount = 0;
  let invalidCount = 0;
  const sampleSize = Math.min(100, lines.length - 1);
  const step = Math.max(1, Math.floor((lines.length - 1) / sampleSize));

  for (let i = 1; i < lines.length; i += step) {
    const values = parseCSVLine(lines[i]);
    const row: Record<string, unknown> = {};
    for (let j = 0; j < headers.length; j++) {
      const v = values[j] ?? "";
      if (v === "") {
        row[headers[j]] = null;
      } else if (!isNaN(Number(v)) && v.trim() !== "") {
        row[headers[j]] = Number(v);
      } else {
        row[headers[j]] = v;
      }
    }

    if (validate(row)) {
      validCount++;
    } else {
      invalidCount++;
      if (invalidCount <= 3) {
        fail(
          `Row ${i}: ${validate.errors?.map((e) => `${e.instancePath} ${e.message}`).join("; ")}`
        );
      }
    }
  }

  if (invalidCount === 0) {
    pass(`All ${validCount} sampled rows pass schema validation`);
  } else {
    fail(`${invalidCount}/${validCount + invalidCount} sampled rows failed`);
  }

  // Check active count
  const estadoIdx = headers.indexOf("estado");
  if (estadoIdx >= 0) {
    let active = 0;
    for (let i = 1; i < lines.length; i++) {
      const vals = parseCSVLine(lines[i]);
      if (vals[estadoIdx] === "Activo") active++;
    }
    console.log(`  INFO: ${active} active programs`);
    if (active < 10000) {
      fail(`Expected 10000+ active programs, got ${active}`);
    } else {
      pass(`Active program count (${active}) looks reasonable`);
    }
  }
}

function validateItems(lang: "en" | "es") {
  console.log(`\n--- Validating items_${lang}.json ---`);

  const path = resolve(DATA, `items_${lang}.json`);
  if (!existsSync(path)) {
    fail(`items_${lang}.json not found`);
    return;
  }

  const data = JSON.parse(readFileSync(path, "utf-8"));

  if (!data.meta) fail("Missing 'meta' field");
  else pass("Has 'meta' field");

  if (!Array.isArray(data.items)) {
    fail("'items' is not an array");
    return;
  }

  const items = data.items;
  pass(`${items.length} items`);

  if (items.length !== RIASEC_TYPES.length * ITEMS_PER_TYPE) {
    fail(
      `Expected ${RIASEC_TYPES.length * ITEMS_PER_TYPE} items, got ${items.length}`
    );
  } else {
    pass("Correct item count (48)");
  }

  // Check each type has correct number of items
  for (const type of RIASEC_TYPES) {
    const typeItems = items.filter(
      (i: { type: string }) => i.type === type
    );
    if (typeItems.length !== ITEMS_PER_TYPE) {
      fail(`Type ${type}: expected ${ITEMS_PER_TYPE} items, got ${typeItems.length}`);
    }
  }
  pass("All RIASEC types have 8 items each");

  // Check item structure
  const ids = new Set<string>();
  for (const item of items) {
    if (!item.id || !item.type || !item.text || !item.keyed) {
      fail(`Item missing required fields: ${JSON.stringify(item)}`);
    }
    if (ids.has(item.id)) {
      fail(`Duplicate item ID: ${item.id}`);
    }
    ids.add(item.id);
  }
  if (ids.size === items.length) {
    pass("All item IDs are unique");
  }
}

function validateMapping() {
  console.log("\n--- Validating mapping.json ---");

  const path = resolve(DATA, "mapping.json");
  if (!existsSync(path)) {
    fail("mapping.json not found");
    return;
  }

  const data = JSON.parse(readFileSync(path, "utf-8"));

  if (!data.mapping) {
    fail("Missing 'mapping' field");
    return;
  }

  for (const type of RIASEC_TYPES) {
    const entry = data.mapping[type];
    if (!entry) {
      fail(`Missing mapping for type ${type}`);
      continue;
    }
    if (!entry.name || !entry.name_es) {
      fail(`Type ${type}: missing name or name_es`);
    }
    if (!Array.isArray(entry.fields) || entry.fields.length === 0) {
      fail(`Type ${type}: missing or empty fields array`);
    } else {
      for (const f of entry.fields) {
        if (!f.cine_amplio || typeof f.weight !== "number") {
          fail(
            `Type ${type}: field entry missing cine_amplio or weight: ${JSON.stringify(f)}`
          );
        }
        if (f.weight < 0 || f.weight > 1) {
          fail(`Type ${type}: weight out of range [0,1]: ${f.weight}`);
        }
      }
      pass(`Type ${type}: ${entry.fields.length} field mappings, weights valid`);
    }
  }
}

/** Simple CSV line parser handling quoted fields */
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
    } else {
      if (ch === '"') {
        inQuotes = true;
      } else if (ch === ",") {
        result.push(current);
        current = "";
      } else {
        current += ch;
      }
    }
  }
  result.push(current);
  return result;
}

function main() {
  console.log("=== riasec-co data validation ===");

  validateItems("en");
  validateItems("es");
  validateMapping();
  validatePrograms();

  console.log(`\n=== Result: ${errors === 0 ? "ALL PASSED" : `${errors} ERRORS`} ===`);
  process.exit(errors > 0 ? 1 : 0);
}

main();
