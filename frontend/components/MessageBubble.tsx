import { AlertCircle, RotateCcw } from "lucide-react";
import type { ChatMessage } from "@/lib/types";
import { VisionMark } from "./VisionMark";
import { MarkdownContent } from "./MarkdownContent";
import { CopyButton } from "./CopyButton";

interface MessageBubbleProps {
  message: ChatMessage;
  onRetry?: () => void;
}

export function MessageBubble({ message, onRetry }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isError = message.status === "error";

  if (isUser) {
    return (
      <div className="flex justify-end px-1 py-2 message-enter">
        <div className="max-w-[80%] rounded-2xl rounded-tr-md bg-[var(--accent)] px-4 py-2.5 text-[15px] leading-relaxed text-white">
          {message.content}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-start gap-3 px-1 py-2 message-enter">
        <div className="mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-[var(--surface)]">
          <AlertCircle size={16} className="text-[var(--danger)]" />
        </div>
        <div className="max-w-[80%] rounded-2xl rounded-tl-md border border-[var(--danger)]/25 bg-[var(--danger)]/[0.06] px-4 py-2.5">
          <p className="text-[15px] leading-relaxed text-[var(--foreground)]">
            {message.content}
          </p>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="mt-2 flex items-center gap-1.5 rounded-md border border-[var(--border)] px-2.5 py-1 text-xs text-[var(--foreground)] transition-colors hover:bg-[var(--surface-hover)]"
            >
              <RotateCcw size={12} />
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3 px-1 py-2 message-enter">
      <div className="mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-[var(--surface)]">
        <VisionMark variant="avatar" size={18} />
      </div>
      <div className="max-w-[80%] rounded-2xl rounded-tl-md bg-[var(--surface)] px-4 py-2.5">
        <div className="text-[15px] leading-relaxed text-[var(--foreground)]">
          <MarkdownContent content={message.content} />
        </div>
        <div className="-ml-2 -mb-1 mt-1">
          <CopyButton text={message.content} />
        </div>
      </div>
    </div>
  );
}
