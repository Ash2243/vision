"use client";

/**
 * Chat state hook.
 *
 * All conversation state (messages, loading, errors) and the logic to
 * mutate it lives here — components only read state and call the
 * functions this hook returns.
 *
 * Sprint 6: the backend is stateless, so this hook is now also
 * responsible for sending the right conversation history with every
 * request. `messagesRef` mirrors the `messages` state and is updated
 * synchronously alongside it — send()/retry() need the exact
 * conversation array at the moment of the call (not a value that
 * might be stale until the next render), and reading messages out of
 * a React state closure can't guarantee that.
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
  const [messages, setMessagesState] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);

  const messagesRef = useRef<ChatMessage[]>([]);

  // The exact conversation (including the new user message) that was
  // sent on the last attempt — retry() resends this, rather than
  // reconstructing it, so a retry always matches what the user
  // actually saw get sent.
  const lastAttemptRef = useRef<ChatMessage[] | null>(null);

  /** Update both the state (for rendering) and the ref (for synchronous reads) together. */
  const commitMessages = useCallback((next: ChatMessage[]) => {
    messagesRef.current = next;
    setMessagesState(next);
  }, []);

  /**
   * Ask the backend for a response to `conversation` and append the
   * result (success or error) to the message list.
   *
   * Deliberately does NOT touch the user's message bubble — send()
   * adds that once, up front; retry() re-runs only this function so
   * a failed request can be retried without duplicating what the
   * user already sees they sent.
   */
  const attemptResponse = useCallback(
    async (conversation: ChatMessage[]) => {
      setIsSending(true);
      try {
        const response = await sendChatMessage(conversation);
        commitMessages([
          ...messagesRef.current,
          { id: createId(), role: "assistant", content: response },
        ]);
      } catch (err) {
        const detail =
          err instanceof ChatApiError
            ? err.message
            : "Something went wrong. Please try again.";
        commitMessages([
          ...messagesRef.current,
          { id: createId(), role: "assistant", content: detail, status: "error" },
        ]);
      } finally {
        setIsSending(false);
      }
    },
    [commitMessages]
  );

  const send = useCallback(
    async (rawMessage: string) => {
      const trimmed = rawMessage.trim();
      if (!trimmed || isSending) return;

      const userMessage: ChatMessage = {
        id: createId(),
        role: "user",
        content: trimmed,
      };
      const conversation = [...messagesRef.current, userMessage];

      commitMessages(conversation);
      lastAttemptRef.current = conversation;

      await attemptResponse(conversation);
      // isSending is checked, not depended on, at the top of this
      // function via closure — omitting it from deps keeps `send`
      // stable across renders while still guarding duplicate sends.
      // eslint-disable-next-line react-hooks/exhaustive-deps
    },
    [attemptResponse, commitMessages]
  );

  const retry = useCallback(() => {
    if (!lastAttemptRef.current || isSending) return;

    // Drop the trailing error bubble before retrying, so the retry
    // doesn't stack a second error message under the first — the
    // user's message bubble (already part of lastAttemptRef.current)
    // is left untouched, so nothing gets duplicated.
    const current = messagesRef.current;
    const last = current[current.length - 1];
    if (last?.status === "error") {
      commitMessages(current.slice(0, -1));
    }

    void attemptResponse(lastAttemptRef.current);
  }, [isSending, attemptResponse, commitMessages]);

  return { messages, isSending, send, retry };
}
