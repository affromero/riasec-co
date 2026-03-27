import { useMemo } from "react";
import { RIASEC_TYPES, type RIASECProfile, type RIASECType } from "riasec-co";

interface ChartPoint {
  type: RIASECType;
  x: number;
  y: number;
  labelX: number;
  labelY: number;
  gridX: number;
  gridY: number;
  value: number;
}

const COLORS: Record<RIASECType, string> = {
  R: "#e74c3c",
  I: "#3498db",
  A: "#9b59b6",
  S: "#2ecc71",
  E: "#f39c12",
  C: "#95a5a6",
};

const LABELS_ES: Record<RIASECType, string> = {
  R: "Realista",
  I: "Investigador",
  A: "Artístico",
  S: "Social",
  E: "Emprendedor",
  C: "Convencional",
};

const LABELS_EN: Record<RIASECType, string> = {
  R: "Realistic",
  I: "Investigative",
  A: "Artistic",
  S: "Social",
  E: "Enterprising",
  C: "Conventional",
};

export interface ProfileChartProps {
  /** RIASEC profile to display */
  profile: RIASECProfile;
  /** Language for labels */
  language?: "en" | "es";
  /** Chart size in pixels */
  size?: number;
  /** Additional CSS class name */
  className?: string;
}

/**
 * SVG radar chart showing a RIASEC profile.
 *
 * Pure SVG, no charting library dependency.
 */
export function ProfileChart({
  profile,
  language = "es",
  size = 300,
  className,
}: ProfileChartProps) {
  const labels = language === "es" ? LABELS_ES : LABELS_EN;
  const center = size / 2;
  const radius = size * 0.35;

  const points = useMemo((): ChartPoint[] => {
    const maxVal = Math.max(...Object.values(profile), 0.01);
    return RIASEC_TYPES.map((type: RIASECType, i: number) => {
      const angle = (Math.PI * 2 * i) / 6 - Math.PI / 2;
      const r = (profile[type] / maxVal) * radius;
      return {
        type,
        x: center + r * Math.cos(angle),
        y: center + r * Math.sin(angle),
        labelX: center + (radius + 25) * Math.cos(angle),
        labelY: center + (radius + 25) * Math.sin(angle),
        gridX: center + radius * Math.cos(angle),
        gridY: center + radius * Math.sin(angle),
        value: profile[type],
      };
    });
  }, [profile, center, radius]);

  const polygonPoints = points.map((p) => `${p.x},${p.y}`).join(" ");
  const gridPoints = points.map((p) => `${p.gridX},${p.gridY}`).join(" ");

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      className={className}
      role="img"
      aria-label={language === "es" ? "Perfil RIASEC" : "RIASEC Profile"}
    >
      {/* Grid lines */}
      {[0.25, 0.5, 0.75, 1].map((scale) => (
        <polygon
          key={scale}
          points={points
            .map((p) => {
              const angle = (Math.PI * 2 * RIASEC_TYPES.indexOf(p.type)) / 6 - Math.PI / 2;
              const r = radius * scale;
              return `${center + r * Math.cos(angle)},${center + r * Math.sin(angle)}`;
            })
            .join(" ")}
          fill="none"
          stroke="#e0e0e0"
          strokeWidth={1}
        />
      ))}

      {/* Axes */}
      {points.map((p) => (
        <line
          key={`axis-${p.type}`}
          x1={center}
          y1={center}
          x2={p.gridX}
          y2={p.gridY}
          stroke="#e0e0e0"
          strokeWidth={1}
        />
      ))}

      {/* Data polygon */}
      <polygon
        points={polygonPoints}
        fill="rgba(52, 152, 219, 0.25)"
        stroke="#3498db"
        strokeWidth={2}
      />

      {/* Data points */}
      {points.map((p) => (
        <circle
          key={`point-${p.type}`}
          cx={p.x}
          cy={p.y}
          r={4}
          fill={COLORS[p.type]}
        />
      ))}

      {/* Labels */}
      {points.map((p) => (
        <text
          key={`label-${p.type}`}
          x={p.labelX}
          y={p.labelY}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={11}
          fill="#333"
        >
          {labels[p.type]}
        </text>
      ))}

      {/* Values */}
      {points.map((p) => (
        <text
          key={`value-${p.type}`}
          x={p.labelX}
          y={p.labelY + 14}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={10}
          fill="#666"
        >
          {(p.value * 100).toFixed(0)}%
        </text>
      ))}
    </svg>
  );
}
