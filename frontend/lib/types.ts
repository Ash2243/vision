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

/** Shape of the request body sent to POST /api/v1/chat. */
export interface ChatRequestBody {
  message: string;
}

/** Shape of a successful response from POST /api/v1/chat. */
export interface ChatResponseBody {
  response: string;
  message: string;
}
