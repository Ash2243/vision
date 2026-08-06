import { ChevronDown, Clock, Moon, Settings } from "lucide-react";
import { VisionMark } from "./VisionMark";

/**
 * Fixed header.
 *
 * Includes disabled placeholder controls for features that don't
 * exist yet (website selector, model selector, history, settings) —
 * per the Sprint 5 brief, these reserve their spot in the layout
 * without being wired up to anything.
 */
export function Header() {
  return (
    <header className="sticky top-0 z-10 border-b border-[var(--border)] bg-[var(--background)]/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-[850px] items-center justify-between px-4">
        <div className="flex items-center gap-2.5">
          <VisionMark variant="logo" size={26} />
          <div className="leading-tight">
            <div className="text-[15px] font-medium text-[var(--foreground)]">
              Vision
            </div>
            <div className="font-mono text-[11px] tracking-wide text-[var(--muted)]">
              universal website intelligence
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <PlaceholderPill label="Website" />
          <PlaceholderPill label="Model" />
          <PlaceholderIconButton title="Conversation history (coming soon)">
            <Clock size={16} />
          </PlaceholderIconButton>
          <PlaceholderIconButton title="Settings (coming soon)">
            <Settings size={16} />
          </PlaceholderIconButton>
          <PlaceholderIconButton title="Theme (coming soon)">
            <Moon size={16} />
          </PlaceholderIconButton>
        </div>
      </div>
    </header>
  );
}

/** A disabled dropdown-shaped placeholder — reserves space, does nothing yet. */
function PlaceholderPill({ label }: { label: string }) {
  return (
    <button
      type="button"
      disabled
      title={`${label} selection (coming soon)`}
      className="hidden items-center gap-1 rounded-full border border-[var(--border)] px-3 py-1.5 text-xs text-[var(--muted)] opacity-60 sm:flex"
    >
      {label}
      <ChevronDown size={12} />
    </button>
  );
}

function PlaceholderIconButton({
  children,
  title,
}: {
  children: React.ReactNode;
  title: string;
}) {
  return (
    <button
      type="button"
      disabled
      title={title}
      className="flex h-8 w-8 items-center justify-center rounded-full text-[var(--muted)] opacity-60"
    >
      {children}
    </button>
  );
}
