"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage } from "@/lib/types";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import { VisionMark } from "./VisionMark";

interface ChatContainerProps {
  messages: ChatMessage[];
  isSending: boolean;
  onRetry: () => void;
}

export function ChatContainer({ messages, isSending, onRetry }: ChatContainerProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, isSending]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center px-4 text-center">
        <VisionMark variant="logo" size={40} className="mb-4 opacity-80" />
        <h1 className="text-lg font-medium text-[var(--foreground)]">
          Ask Vision anything
        </h1>
        <p className="mt-1.5 max-w-sm font-mono text-sm text-[var(--muted)]">
          AI that understands websites.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="mx-auto max-w-[850px] px-4 py-6">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onRetry={message.status === "error" ? onRetry : undefined}
          />
        ))}
        {isSending && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
