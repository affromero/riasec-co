/**
 * items.ts — IPIP RIASEC item bank loader
 *
 * Loads the 48-item IPIP Basic Interest Markers from bundled JSON.
 */

import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import type { Item, ItemBank } from "./types.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

// When installed from npm: dist/ and data/ are siblings in the package root
// When running from source: data/canonical/ is at the monorepo root
const PATHS = [
  resolve(__dirname, "../data"),
  resolve(__dirname, "../../data/canonical"),
  resolve(__dirname, "../../../data/canonical"),
];

function findDataDir(): string {
  for (const dir of PATHS) {
    try {
      readFileSync(resolve(dir, "items_en.json"));
      return dir;
    } catch { /* try next */ }
  }
  throw new Error("riasec-co: Could not find data files. Ensure the package is installed correctly.");
}

let cachedEn: ItemBank | null = null;
let cachedEs: ItemBank | null = null;

/** Load the IPIP RIASEC item bank */
export function loadItems(language: "en" | "es" = "en"): ItemBank {
  if (language === "en" && cachedEn) return cachedEn;
  if (language === "es" && cachedEs) return cachedEs;

  const dataDir = findDataDir();
  const path = resolve(dataDir, `items_${language}.json`);
  const raw = readFileSync(path, "utf-8");
  const bank = JSON.parse(raw) as ItemBank;

  if (language === "en") cachedEn = bank;
  else cachedEs = bank;

  return bank;
}

/** Get all items for a specific RIASEC type */
export function getItemsByType(items: Item[], type: string): Item[] {
  return items.filter((i) => i.type === type);
}
