import React, { useRef, useEffect, useState } from "react";
import { Message } from "../data/messages";
import MessageBubble from "./message-bubble";
import { cn } from "@/lib/utils";
interface ChatMainProps {
  messages: Message[];
  loading?: boolean;
  isEmptyChat?: boolean;
}

const ChatMain: React.FC<ChatMainProps> = ({
  messages,
  loading = false,
  isEmptyChat = false,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const previousMessagesLengthRef = useRef<number>(0);
  const previousChatIdRef = useRef<string | null>(null);
  const [latestAiMessageId, setLatestAiMessageId] = useState<string | null>(
    null,
  );

  // Helper function to scroll to bottom
  const scrollToBottom = () => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  };

  // When messages change, identify if a new AI message was added
  useEffect(() => {
    // Check if this is a chat switch by comparing the first message's chatId
    const currentChatId = messages.length > 0 ? messages[0]?.chatId : null;
    const isChatSwitch =
      currentChatId !== previousChatIdRef.current && currentChatId !== null;

    // Update the previous chat ID reference
    previousChatIdRef.current = currentChatId;

    // Only look for new messages if the message count increased
    if (messages.length > previousMessagesLengthRef.current) {
      // New messages were added
      const newMessages = messages.slice(previousMessagesLengthRef.current);
      // Check if any of the new messages are from AI
      const newAiMessage = newMessages.find((msg) => msg.sender === "ai");

      if (newAiMessage) {
        // We found a new AI message - mark it for animation
        setLatestAiMessageId(newAiMessage.id);
      }
    } else if (messages.length === 0) {
      // Reset when messages are cleared (like when switching chats)
      setLatestAiMessageId(null);
    } else if (
      messages.length !== previousMessagesLengthRef.current ||
      isChatSwitch
    ) {
      // If the message count changed but didn't increase (e.g., switched to a different chat)
      // Find the last AI message in the current list, but don't animate it
      setLatestAiMessageId(null);
    }

    // Update the reference for next comparison
    previousMessagesLengthRef.current = messages.length;

    // If we've switched chats or messages have changed at all, scroll to bottom
    // Using requestAnimationFrame ensures this happens after the DOM updates
    if (isChatSwitch || messages.length > 0) {
      // Use requestAnimationFrame to ensure DOM is updated before scrolling
      requestAnimationFrame(() => {
        scrollToBottom();
      });
    }
  }, [messages]);

  // Auto-scroll to bottom when messages change, but only within the chat container
  useEffect(() => {
    // Initial scroll on mount
    scrollToBottom();

    // Also set up a small delay to handle any async rendering issues
    const timeoutId = setTimeout(() => {
      scrollToBottom();
    }, 100);

    return () => clearTimeout(timeoutId);
  }, []); // Empty dependency array means this runs once on mount

  return (
    <div
      ref={containerRef}
      className={cn(
        "w-full overflow-y-auto p-4 pt-16 text-left transition-all duration-700",
        !isEmptyChat && "flex-1",
      )}
    >
      <div className="mx-auto flex max-w-[960px] flex-col gap-4">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            isLatestMessage={message.id === latestAiMessageId && !loading}
          />
        ))}
        {loading && (
          <div className="mb-4 flex items-center justify-start px-3 pt-1">
            <span
              className={cn(
                "text-muted-foreground/70",

                // Shine effect
                "animate-shiny-text [background-size:200px_100%] bg-clip-text [background-position:0_0] bg-no-repeat [transition:background-position_1s_cubic-bezier(.6,.6,0,1)_infinite]",

                // Shine gradient
                "via-foreground bg-gradient-to-r from-transparent via-50% to-transparent",
              )}
            >
              Reasoning and preparing response...
            </span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatMain;
