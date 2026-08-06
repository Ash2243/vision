"use client";

/**
 * Chat state hook.
 *
 * All conversation state (messages, loading, errors) and the logic to
 * mutate it lives here — components only read state and call the
 * functions this hook returns. This isolation is what lets future
 * sprints add conversation history, multi-session state, or streaming
 * without rewriting the UI components themselves.
 */

import { useCallback, useRef, useState } from "react";
import { sendChatMessage, ChatApiError } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

function createId(): string {
  // crypto.randomUUID is available in all modern browsers; this is a
  // small dependency-free way to get stable unique message keys.
  return typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);

  // Tracks the last user message so a failed send can be retried
  // without the user needing to retype it.
  const lastAttemptRef = useRef<string | null>(null);

  /**
   * Ask the backend for a response to `userText` and append the
   * result (success or error) to the message list.
   *
   * Deliberately does NOT touch the user's message bubble — send()
   * adds that once, up front; retry() re-runs only this function so
   * a failed request can be retried without duplicating what the
   * user already sees they sent.
   */
  const attemptResponse = useCallback(async (userText: string) => {
    setIsSending(true);
    try {
      const response = await sendChatMessage(userText);
      setMessages((prev) => [
        ...prev,
        { id: createId(), role: "assistant", content: response },
      ]);
    } catch (err) {
      const detail =
        err instanceof ChatApiError
          ? err.message
          : "Something went wrong. Please try again.";
      setMessages((prev) => [
        ...prev,
        { id: createId(), role: "assistant", content: detail, status: "error" },
      ]);
    } finally {
      setIsSending(false);
    }
  }, []);

  const send = useCallback(
    async (rawMessage: string) => {
      const trimmed = rawMessage.trim();
      if (!trimmed || isSending) return;

      lastAttemptRef.current = trimmed;

      setMessages((prev) => [
        ...prev,
        { id: createId(), role: "user", content: trimmed },
      ]);

      await attemptResponse(trimmed);
      // isSending is checked, not depended on, at the top of this
      // function via closure — omitting it from deps keeps `send`
      // stable across renders while still guarding duplicate sends.
      // eslint-disable-next-line react-hooks/exhaustive-deps
    },
    [attemptResponse]
  );

  const retry = useCallback(() => {
    if (!lastAttemptRef.current || isSending) return;
    // Drop the trailing error bubble before retrying, so the retry
    // doesn't stack a second error message under the first — but
    // the original user message bubble is left untouched.
    setMessages((prev) => {
      const last = prev[prev.length - 1];
      return last?.status === "error" ? prev.slice(0, -1) : prev;
    });
    void attemptResponse(lastAttemptRef.current);
  }, [isSending, attemptResponse]);

  return { messages, isSending, send, retry };
}
