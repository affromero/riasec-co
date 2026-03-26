import type { Recommendation, RIASECType } from "@riasec-co/core";

const TYPE_LABELS_ES: Record<RIASECType, string> = {
  R: "Realista",
  I: "Investigador",
  A: "Artístico",
  S: "Social",
  E: "Emprendedor",
  C: "Convencional",
};

const TYPE_COLORS: Record<RIASECType, string> = {
  R: "#e74c3c",
  I: "#3498db",
  A: "#9b59b6",
  S: "#2ecc71",
  E: "#f39c12",
  C: "#95a5a6",
};

export interface ProgramCardsProps {
  /** Recommendations from the recommend() function */
  recommendations: Recommendation[];
  /** Language for labels */
  language?: "en" | "es";
  /** Additional CSS class name */
  className?: string;
}

/**
 * Displays program recommendations as cards.
 *
 * Shows program name, institution, department, modality,
 * CINE field, match score, and matching RIASEC types.
 */
export function ProgramCards({
  recommendations,
  language = "es",
  className,
}: ProgramCardsProps) {
  if (recommendations.length === 0) {
    return (
      <div className={className}>
        <p>
          {language === "es"
            ? "No se encontraron programas que coincidan."
            : "No matching programs found."}
        </p>
      </div>
    );
  }

  return (
    <div className={className} data-testid="program-cards">
      {recommendations.map((rec, idx) => (
        <article key={rec.program.codigo_snies} data-testid="program-card">
          {/* Rank badge */}
          <span aria-label={`Rank ${idx + 1}`}>
            #{idx + 1}
          </span>

          {/* Program info */}
          <h3>{rec.program.nombre_programa}</h3>
          <p>{rec.program.nombre_institucion}</p>

          {/* Details */}
          <dl>
            <dt>{language === "es" ? "Departamento" : "Department"}</dt>
            <dd>{rec.program.departamento}</dd>

            <dt>{language === "es" ? "Modalidad" : "Modality"}</dt>
            <dd>{rec.program.modalidad}</dd>

            <dt>{language === "es" ? "Nivel" : "Level"}</dt>
            <dd>{rec.program.nivel_formacion}</dd>

            <dt>{language === "es" ? "Campo" : "Field"}</dt>
            <dd>{rec.program.cine_amplio}</dd>

            {rec.program.costo_matricula != null && (
              <>
                <dt>{language === "es" ? "Matrícula" : "Tuition"}</dt>
                <dd>
                  ${rec.program.costo_matricula.toLocaleString("es-CO")} COP
                </dd>
              </>
            )}
          </dl>

          {/* Match score */}
          <div aria-label={`Match score: ${Math.round(rec.score * 100)}%`}>
            <div style={{ width: `${Math.min(rec.score * 100, 100)}%` }} />
            <span>{Math.round(rec.score * 100)}%</span>
          </div>

          {/* Matching types */}
          <div>
            {rec.matchDetails.matchingTypes.map((type: RIASECType) => (
              <span
                key={type}
                style={{ backgroundColor: TYPE_COLORS[type], color: "white" }}
              >
                {language === "es" ? TYPE_LABELS_ES[type] : type}
              </span>
            ))}
          </div>
        </article>
      ))}
    </div>
  );
}
