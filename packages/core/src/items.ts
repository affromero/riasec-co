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

/** Path to the canonical data directory */
const DATA_DIR = resolve(__dirname, "../../data/canonical");

// Fallback: when running from packages/core/src, data is at repo root
const DATA_DIR_ALT = resolve(__dirname, "../../../data/canonical");

function findDataDir(): string {
  try {
    readFileSync(resolve(DATA_DIR, "items_en.json"));
    return DATA_DIR;
  } catch {
    return DATA_DIR_ALT;
  }
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
