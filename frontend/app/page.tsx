"use client";

import { Header } from "@/components/Header";
import { ChatContainer } from "@/components/ChatContainer";
import { ChatInput } from "@/components/ChatInput";
import { useChat } from "@/hooks/useChat";

export default function Home() {
  const { messages, isSending, send, retry } = useChat();

  return (
    <div className="flex h-dvh flex-col bg-[var(--background)]">
      <Header />
      <ChatContainer messages={messages} isSending={isSending} onRetry={retry} />
      <ChatInput onSend={send} disabled={isSending} />
    </div>
  );
}
