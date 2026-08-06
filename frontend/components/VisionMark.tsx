/**
 * Vision's signature mark — three concentric arcs, evoking a lens
 * or aperture (seeing, navigating, understanding a website).
 *
 * Reused in three places so the brand identity is consistent rather
 * than three different icons doing three different jobs:
 *   - "logo" in the header
 *   - "avatar" next to assistant messages
 *   - "pulse" as the typing indicator, where the same arcs animate
 *     in sequence instead of a generic three-dot bounce.
 */

type VisionMarkVariant = "logo" | "avatar" | "pulse";

interface VisionMarkProps {
  variant?: VisionMarkVariant;
  size?: number;
  className?: string;
}

export function VisionMark({
  variant = "logo",
  size = 24,
  className,
}: VisionMarkProps) {
  const isPulsing = variant === "pulse";

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <circle
        cx="16"
        cy="16"
        r="14"
        stroke="var(--accent)"
        strokeOpacity="0.25"
        strokeWidth="1.5"
        className={isPulsing ? "vision-arc-1" : undefined}
      />
      <circle
        cx="16"
        cy="16"
        r="9.5"
        stroke="var(--accent)"
        strokeOpacity="0.55"
        strokeWidth="1.5"
        className={isPulsing ? "vision-arc-2" : undefined}
      />
      <circle
        cx="16"
        cy="16"
        r="4"
        fill="var(--accent)"
        className={isPulsing ? "vision-arc-3" : undefined}
      />
    </svg>
  );
}
