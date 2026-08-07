/**
 * API layer.
 *
 * The only file that knows how to talk to the backend. Components and
 * hooks never call fetch() directly — they call sendChatMessage(). This
 * means swapping to a streaming endpoint later (SSE / ReadableStream)
 * only touches this file, not the UI or state layer.
 */

import type { ChatMessage, ChatRequestBody, ChatResponseBody } from "./types";

/**
 * Base URL for the Vision backend.
 *
 * Read from an environment variable rather than hardcoded, so local
 * dev, staging, and production can point at different backends
 * without a code change. See .env.local.example.
 */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export class ChatApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ChatApiError";
  }
}

/**
 * Send the conversation so far to Vision's backend and return the
 * new response text.
 *
 * Sprint 6: takes the full conversation (not just the latest
 * message) so the backend — which holds no state of its own — can
 * give the AI provider the context it needs for follow-up questions.
 *
 * Messages with status "error" (failed-send bubbles shown in the UI)
 * are filtered out here rather than sent as real conversation turns
 * — they were never a real assistant reply, and including them would
 * feed the AI provider a false turn instead of just history it never
 * actually produced.
 *
 * Throws ChatApiError for any failure — validation errors (422),
 * upstream AI provider failures (502), or the backend being
 * unreachable at all (network error). Callers only need one catch
 * block; they don't need to distinguish HTTP status codes themselves.
 */
export async function sendChatMessage(conversation: ChatMessage[]): Promise<string> {
  const body: ChatRequestBody = {
    messages: conversation
      .filter((m) => m.status !== "error")
      .map((m) => ({ role: m.role, content: m.content })),
  };

  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    // fetch() itself throws on network failure (backend down, no
    // connection) — distinct from the backend responding with an
    // error status, which is handled below.
    throw new ChatApiError(
      "Vision's backend isn't reachable. Make sure it's running and try again."
    );
  }

  if (!res.ok) {
    if (res.status === 422) {
      throw new ChatApiError("That message couldn't be sent. Please try rephrasing it.");
    }
    if (res.status === 502) {
      throw new ChatApiError("Vision's AI provider didn't respond. Please try again.");
    }
    throw new ChatApiError("Something went wrong on Vision's end. Please try again.");
  }

  const data = (await res.json()) as ChatResponseBody;
  return data.response;
}
