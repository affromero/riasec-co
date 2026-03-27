#' Load IPIP RIASEC items
#'
#' Loads the 48-item IPIP Basic Interest Markers in the specified language.
#'
#' @param language Character: "en" or "es". Default: "es"
#' @return Data frame with columns: id, type, text, keyed
#' @export
#' @importFrom jsonlite fromJSON
load_items <- function(language = "es") {
  filename <- paste0("items_", language, ".json")
  path <- system.file("extdata", filename, package = "riasecco")
  if (path == "") {
    # Fallback: try canonical data directory
    path <- file.path(
      system.file(package = "riasecco"),
      "..", "..", "data", "canonical", filename
    )
  }
  if (!file.exists(path)) stop("Item file not found: ", filename)

  raw <- fromJSON(path)
  as.data.frame(raw$items, stringsAsFactors = FALSE)
}

#' Load RIASEC to CINE field mapping
#'
#' @return Data frame with columns: riasec_type, name, name_es, cine_amplio, weight
#' @export
#' @importFrom jsonlite fromJSON
load_mapping <- function() {
  path <- system.file("extdata", "mapping.json", package = "riasecco")
  if (path == "") {
    path <- file.path(
      system.file(package = "riasecco"),
      "..", "..", "data", "canonical", "mapping.json"
    )
  }
  if (!file.exists(path)) stop("Mapping file not found")

  raw <- fromJSON(path)
  mapping <- raw$mapping

  rows <- list()
  for (type in names(mapping)) {
    entry <- mapping[[type]]
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

  do.call(rbind, rows)
}

#' Plot a RIASEC profile as a radar chart
#'
#' @param profile Named numeric vector: RIASEC profile
#' @param title Character: plot title. Default: "Perfil RIASEC"
#' @return A ggplot2 object (if ggplot2 is available), or base R plot
#' @export
#' @importFrom stats setNames
plot_profile <- function(profile, title = "Perfil RIASEC") {
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    # Base R fallback: bar chart
    barplot(profile[RIASEC_TYPES],
            main = title,
            col = c("#e74c3c", "#3498db", "#9b59b6",
                    "#2ecc71", "#f39c12", "#95a5a6"),
            ylim = c(0, max(profile) * 1.15))
    return(invisible(NULL))
  }

  df <- data.frame(
    type = factor(RIASEC_TYPES, levels = RIASEC_TYPES),
    value = as.numeric(profile[RIASEC_TYPES]),
    label = c("Realista", "Investigador", "Artístico",
              "Social", "Emprendedor", "Convencional")
  )

  ggplot2::ggplot(df, ggplot2::aes(x = df$type, y = df$value, fill = df$type)) +
    ggplot2::geom_col(show.legend = FALSE) +
    ggplot2::scale_fill_manual(values = c(
      R = "#e74c3c", I = "#3498db", A = "#9b59b6",
      S = "#2ecc71", E = "#f39c12", C = "#95a5a6"
    )) +
    ggplot2::scale_x_discrete(labels = df$label) +
    ggplot2::labs(x = NULL, y = "Probabilidad", title = title) +
    ggplot2::theme_minimal()
}
