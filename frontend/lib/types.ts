/**
 * Shared types for the chat interface.
 *
 * Kept separate from components and API logic so both can import the
 * same shapes without circular dependencies.
 */

export type MessageRole = "user" | "assistant";

export type MessageStatus = "idle" | "error";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  status?: MessageStatus;
}

/**
 * The wire shape of a single conversation turn sent to the backend —
 * deliberately just { role, content }, without the frontend-only `id`
 * and `status` fields ChatMessage carries for UI purposes.
 */
export interface ChatApiMessage {
  role: MessageRole;
  content: string;
}

/** Shape of the request body sent to POST /api/v1/chat (Sprint 6: full conversation, not one message). */
export interface ChatRequestBody {
  messages: ChatApiMessage[];
}

/** Shape of a successful response from POST /api/v1/chat. */
export interface ChatResponseBody {
  response: string;
}
