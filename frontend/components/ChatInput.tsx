"use client";

import { useRef, useState } from "react";
import { ArrowUp } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function handleSubmit() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    // Enter sends; Shift+Enter inserts a newline, per the Sprint 5 spec.
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function handleInput(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setValue(e.target.value);
    // Auto-grow the textarea up to a reasonable cap, then scroll.
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  return (
    <div className="sticky bottom-0 border-t border-[var(--border)] bg-[var(--background)]/85 backdrop-blur-md">
      <div className="mx-auto max-w-[850px] px-4 py-4">
        <div className="flex items-end gap-2 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-2 pl-4 shadow-[0_2px_16px_rgba(0,0,0,0.25)] focus-within:border-[var(--accent)]/50">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            rows={1}
            placeholder="Ask Vision anything or request website navigation..."
            className="max-h-40 flex-1 resize-none bg-transparent py-2 text-[15px] text-[var(--foreground)] placeholder:text-[var(--muted)] focus:outline-none disabled:opacity-60"
          />
          <button
            type="button"
            onClick={handleSubmit}
            disabled={disabled || !value.trim()}
            aria-label="Send message"
            className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-[var(--accent)] text-white transition-opacity disabled:opacity-30 disabled:cursor-not-allowed hover:opacity-90"
          >
            <ArrowUp size={17} />
          </button>
        </div>
        <p className="mt-2 text-center font-mono text-[11px] text-[var(--muted)]">
          Vision can make mistakes. Verify important information.
        </p>
      </div>
    </div>
  );
}
