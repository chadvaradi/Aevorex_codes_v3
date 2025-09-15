"use client";

import React, { useState } from "react";
import { AppSidebar } from "./components/chat-sidebar";
import ChatHeader from "./components/chat-header";
import ChatMain from "./components/chat-main";
import ChatInput from "./components/chat-input";
import { SidebarInset, SidebarProvider } from "../../ui/sidebar";
import { Chat, getChatById } from "./data/chats";
import {
  Message,
  getMessagesByChatId,
  addMessage,
  generateMockAiResponse,
} from "./data/messages";

// Helper function to create a message object without modifying global store
const createMessageObject = (
  chatId: string,
  content: string,
  sender: "user" | "ai",
): Message => {
  return {
    id: `msg-${Date.now()}-$1000`, // More unique ID
    chatId,
    content,
    sender,
    timestamp: new Date().toISOString(),
  };
};

// Helper function to generate mock AI response without modifying global store
const createMockAiResponse = (
  chatId: string,
  userMessage: string,
): Promise<Message> => {
  return new Promise((resolve) => {
    // Simulate API delay
    setTimeout(() => {
      // Simple responses based on user message content (copied from the original function)
      let response =
        "I'm not sure how to respond to that. Can you provide more details?";

      if (
        userMessage.toLowerCase().includes("hello") ||
        userMessage.toLowerCase().includes("hi")
      ) {
        response = "Hello! How can I assist you today?";
      } else if (userMessage.toLowerCase().includes("help")) {
        response =
          "I'd be happy to help! What specific information or assistance do you need?";
      } else if (userMessage.toLowerCase().includes("thank")) {
        response = "You're welcome! Is there anything else you'd like to know?";
      } else if (
        userMessage.toLowerCase().includes("code") ||
        userMessage.toLowerCase().includes("programming")
      ) {
        response =
          "I can help with programming questions. What language or framework are you working with?";
      } else if (userMessage.length < 10) {
        response = "Could you elaborate a bit more so I can better assist you?";
      }

      // Create the AI message object
      const aiMessage = createMessageObject(chatId, response, "ai");
      resolve(aiMessage);
    }, 1000);
  });
};

export default function ChatApp() {
  // State for active chat
  const [activeChat, setActiveChat] = useState<Chat | null>(null);
  // State for messages in current chat
  const [messages, setMessages] = useState<Message[]>([]);
  // State for loading indicator
  const [isLoading, setIsLoading] = useState(false);

  // Handler for selecting a chat
  const handleSelectChat = (chatId: string) => {
    if (chatId === "empty") {
      // Handle new chat creation
      setActiveChat({
        id: "empty",
        title: "New chat",
        previewText: "",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
      // Clear messages for new chat
      setMessages([]);
    } else {
      const chat = getChatById(chatId);
      if (chat) {
        setActiveChat(chat);
        const chatMessages = getMessagesByChatId(chatId);
        setMessages(chatMessages);
      }
    }
  };

  // Handler for sending a new message
  const handleSendMessage = async (content: string) => {
    // Create a chat ID if no active chat
    if (!activeChat) {
      // In a real app, we would create a new chat on the server
      // For simplicity in this mock, we'll use a predefined "empty" chat
      setActiveChat({
        id: "empty",
        title: "New chat",
        previewText: content,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
    }

    const chatId = activeChat?.id || "empty";

    // For new chats, we still use the global store
    if (chatId === "empty") {
      // Add user message to global store
      const userMessage = addMessage(chatId, content, "user");
      // Update state with the new message
      setMessages((prevMessages) => [...prevMessages, userMessage]);

      // Show loading indicator
      setIsLoading(true);

      // Generate AI response using global store
      try {
        const aiMessage = await generateMockAiResponse(chatId, content);
        // Update state with AI response
        setMessages((prevMessages) => [...prevMessages, aiMessage]);
      } catch (error) {
        console.error("Failed to generate AI response:", error);
      } finally {
        setIsLoading(false);
      }
    } else {
      // For existing chats, only use local state
      // Create user message in local state only
      const userMessage = createMessageObject(chatId, content, "user");
      // Update state with the new message
      setMessages((prevMessages) => [...prevMessages, userMessage]);

      // Show loading indicator
      setIsLoading(true);

      // Generate AI response in local state only
      try {
        const aiMessage = await createMockAiResponse(chatId, content);
        // Update state with AI response
        setMessages((prevMessages) => [...prevMessages, aiMessage]);
      } catch (error) {
        console.error("Failed to generate AI response:", error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  // Check if we should show the empty state
  const isEmptyChat = messages.length === 0 && !isLoading;

  return (
    <SidebarProvider
      className="glass-3 relative h-[900px] w-full overflow-hidden rounded-xl"
      style={
        {
          "--sidebar-width": "19rem",
        } as React.CSSProperties
      }
    >
      <AppSidebar onSelectChat={handleSelectChat} activeChat={activeChat} />
      <SidebarInset className="flex flex-col">
        <ChatHeader activeChat={activeChat} />
        <ChatMain
          messages={messages}
          loading={isLoading}
          isEmptyChat={isEmptyChat}
        />
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          isEmptyChat={isEmptyChat}
        />
      </SidebarInset>
    </SidebarProvider>
  );
}
