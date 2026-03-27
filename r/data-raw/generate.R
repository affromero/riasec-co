## Generate .rda data files from canonical CSV/JSON
## Run from repo root: Rscript r/data-raw/generate.R

library(jsonlite)

canonical_dir <- file.path("data", "canonical")

# --- Programs ---
cat("Loading programs.csv...\n")
programs <- read.csv(
  file.path(canonical_dir, "programs.csv"),
  stringsAsFactors = FALSE,
  na.strings = ""
)
cat(sprintf("Programs: %d rows, %d columns\n", nrow(programs), ncol(programs)))
cat(sprintf("Active: %d\n", sum(programs$estado == "Activo", na.rm = TRUE)))

# --- Items (English) ---
cat("Loading items_en.json...\n")
raw_en <- fromJSON(file.path(canonical_dir, "items_en.json"))
items_en <- as.data.frame(raw_en$items, stringsAsFactors = FALSE)
cat(sprintf("Items (en): %d\n", nrow(items_en)))

# --- Items (Spanish) ---
cat("Loading items_es.json...\n")
raw_es <- fromJSON(file.path(canonical_dir, "items_es.json"))
items_es <- as.data.frame(raw_es$items, stringsAsFactors = FALSE)
cat(sprintf("Items (es): %d\n", nrow(items_es)))

# --- Mapping ---
cat("Loading mapping.json...\n")
raw_map <- fromJSON(file.path(canonical_dir, "mapping.json"))
mapping_list <- raw_map$mapping

rows <- list()
for (type in names(mapping_list)) {
  entry <- mapping_list[[type]]
  for (i in seq_len(nrow(entry$fields))) {
    rows <- c(rows, list(data.frame(
      riasec_type = type,
      name = entry$name,
      name_es = entry$name_es,
      cine_amplio = entry$fields$cine_amplio[i],
      weight = entry$fields$weight[i],
      stringsAsFactors = FALSE
    )))
  }
}
riasec_mapping <- do.call(rbind, rows)
cat(sprintf("Mapping: %d rows\n", nrow(riasec_mapping)))

# --- Save .rda files ---
data_dir <- file.path("r", "data")
dir.create(data_dir, showWarnings = FALSE, recursive = TRUE)

save(programs, file = file.path(data_dir, "programs.rda"), compress = "xz")
save(items_en, file = file.path(data_dir, "items_en.rda"), compress = "xz")
save(items_es, file = file.path(data_dir, "items_es.rda"), compress = "xz")
save(riasec_mapping, file = file.path(data_dir, "riasec_mapping.rda"), compress = "xz")

# Check sizes
for (f in list.files(data_dir, pattern = "\\.rda$", full.names = TRUE)) {
  size_kb <- file.info(f)$size / 1024
  cat(sprintf("  %s: %.1f KB\n", basename(f), size_kb))
}

# --- Copy JSON files to inst/extdata ---
extdata_dir <- file.path("r", "inst", "extdata")
dir.create(extdata_dir, showWarnings = FALSE, recursive = TRUE)
file.copy(file.path(canonical_dir, "items_en.json"), extdata_dir, overwrite = TRUE)
file.copy(file.path(canonical_dir, "items_es.json"), extdata_dir, overwrite = TRUE)
file.copy(file.path(canonical_dir, "mapping.json"), extdata_dir, overwrite = TRUE)

cat("Done!\n")
