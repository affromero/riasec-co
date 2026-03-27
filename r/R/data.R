#' SNIES Program Catalog
#'
#' Complete catalog of Colombian higher education programs from the
#' SNIES (Sistema Nacional de Información de la Educación Superior).
#' Contains 30,809 programs (17,230 active) across 33 departments.
#'
#' @format A data frame with 30,809 rows and 24 columns:
#' \describe{
#'   \item{codigo_snies}{SNIES program code (integer)}
#'   \item{nombre_programa}{Official program name}
#'   \item{codigo_institucion}{Institution code}
#'   \item{nombre_institucion}{Institution name}
#'   \item{estado}{Program status: "Activo" or "Inactivo"}
#'   \item{estado_institucion}{Institution status}
#'   \item{caracter_academico}{Academic character (e.g., Universidad)}
#'   \item{sector}{Sector: "Oficial" or "Privado"}
#'   \item{nivel_academico}{"Pregrado" or "Posgrado"}
#'   \item{nivel_formacion}{Education level (e.g., Universitario, Tecnológico)}
#'   \item{modalidad}{Modality (e.g., Presencial, Virtual, A distancia)}
#'   \item{titulo_otorgado}{Degree title awarded}
#'   \item{cine_amplio}{CINE F 2013 AC broad field}
#'   \item{cine_especifico}{CINE F 2013 AC specific field}
#'   \item{cine_detallado}{CINE F 2013 AC detailed field}
#'   \item{area_conocimiento}{Knowledge area (Colombian classification)}
#'   \item{nucleo_conocimiento}{Basic knowledge core}
#'   \item{departamento}{Department where program is offered}
#'   \item{municipio}{Municipality where program is offered}
#'   \item{creditos}{Number of credits (integer, may be NA)}
#'   \item{periodos_duracion}{Duration in periods (integer, may be NA)}
#'   \item{periodicidad}{Period type (e.g., Semestral)}
#'   \item{costo_matricula}{Tuition cost for new students in COP (may be NA)}
#'   \item{en_convenio}{Whether offered via agreement}
#' }
#' @source SNIES, Ministerio de Educación Nacional de Colombia.
#'   \url{https://hecaa.mineducacion.gov.co/consultaspublicas/programas}
"programs"

#' IPIP RIASEC Items (Spanish)
#'
#' 48 public-domain items (8 per RIASEC type) from the International
#' Personality Item Pool, adapted to Spanish.
#'
#' @format A data frame with 48 rows and 4 columns:
#' \describe{
#'   \item{id}{Item identifier (e.g., "R1", "I3")}
#'   \item{type}{RIASEC type: R, I, A, S, E, or C}
#'   \item{text}{Item text in Spanish}
#'   \item{keyed}{Keying direction: "+" or "-"}
#' }
#' @source International Personality Item Pool (\url{https://ipip.ori.org/}).
#'   Spanish adaptation: Armstrong, Allison & Rounds (2020).
"items_es"

#' IPIP RIASEC Items (English)
#'
#' 48 public-domain items (8 per RIASEC type) from the International
#' Personality Item Pool.
#'
#' @format A data frame with 48 rows and 4 columns:
#' \describe{
#'   \item{id}{Item identifier (e.g., "R1", "I3")}
#'   \item{type}{RIASEC type: R, I, A, S, E, or C}
#'   \item{text}{Item text in English}
#'   \item{keyed}{Keying direction: "+" or "-"}
#' }
#' @source International Personality Item Pool (\url{https://ipip.ori.org/}).
#'   Liao, Armstrong & Rounds (2008).
"items_en"

#' RIASEC to CINE Field Mapping
#'
#' Maps Holland RIASEC types to Colombian CINE F 2013 AC broad fields
#' with weights indicating strength of association.
#'
#' @format A data frame with rows for each type-field pair:
#' \describe{
#'   \item{riasec_type}{RIASEC type: R, I, A, S, E, or C}
#'   \item{name}{Type name in English}
#'   \item{name_es}{Type name in Spanish}
#'   \item{cine_amplio}{CINE broad field name}
#'   \item{weight}{Association weight (0 to 1)}
#' }
"riasec_mapping"
