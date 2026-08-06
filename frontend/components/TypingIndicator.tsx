import { VisionMark } from "./VisionMark";

/**
 * "Vision is typing..." indicator.
 *
 * Built as its own component (not inline in MessageBubble) so that
 * swapping this for a real token-by-token streaming render later is
 * a one-component change — the rest of the message list doesn't
 * need to know the difference.
 */
export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 px-1 py-2">
      <div className="mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-[var(--surface)]">
        <VisionMark variant="pulse" size={18} />
      </div>
      <div className="flex items-center gap-1.5 pt-1.5 font-mono text-xs text-[var(--muted)]">
        Vision is typing
        <span className="typing-dots">
          <span>.</span>
          <span>.</span>
          <span>.</span>
        </span>
      </div>
    </div>
  );
}
