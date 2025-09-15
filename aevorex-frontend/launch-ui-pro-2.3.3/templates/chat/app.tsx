"use client";

import React, { useState, useEffect } from "react";
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
} from "./data/messages";
import { chatStream, getModels } from "@/src/lib/chatApi";

// Helper function to create a message object without modifying global store
const createMessageObject = (
  chatId: string,
  content: string,
  sender: "user" | "ai",
): Message => {
  return {
    id: `msg-${Date.now()}-${Math.random()}`,
    chatId,
    content,
    sender,
    timestamp: new Date().toISOString(),
  };
};

export default function ChatApp() {
  // State for active chat
  const [activeChat, setActiveChat] = useState<Chat | null>(null);
  // State for messages in current chat
  const [messages, setMessages] = useState<Message[]>([]);
  // State for loading indicator
  const [isLoading, setIsLoading] = useState(false);
  // State for streaming text
  const [streamingText, setStreamingText] = useState("");
  // State for available models and selected model
  const [availableModels, setAvailableModels] = useState<Record<string, string>>({});
  const [selectedModel, setSelectedModel] = useState<string>("deepseek-free");

  // Load available models on component mount
  useEffect(() => {
    getModels()
      .then((modelData: any) => {
        setAvailableModels(modelData.models);
        setSelectedModel(modelData.default);
      })
      .catch((err: any) => {
        console.error("Failed to load models:", err);
      });
  }, []);

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

  // Helper functions for message creation
  const mkUserMsg = (content: string) => {
    const chatId = activeChat?.id || "empty";
    return createMessageObject(chatId, content, "user");
  };

  const mkAiMsg = (content: string) => {
    const chatId = activeChat?.id || "empty";
    return createMessageObject(chatId, content, "ai");
  };

  // Handler for sending a new message
  const handleSendMessage = (content: string) => {
    // Create a chat ID if no active chat
    if (!activeChat) {
      setActiveChat({
        id: "empty",
        title: "New chat",
        previewText: content,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
    }

    // Add user message to local state
    setMessages((prev) => [...prev, mkUserMsg(content)]);
    setIsLoading(true);
    setStreamingText(""); // Clear streaming text at start
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
          streamingText={streamingText}
        />
        <ChatInput
          onSendMessage={handleSendMessage}
          onAIStreamChunk={(chunk) => setStreamingText((s) => s + chunk)}
          onAIStreamEnd={() => {
            setMessages((prev) => [...prev, mkAiMsg(streamingText)]);
            setStreamingText("");
            setIsLoading(false);
          }}
          onAIStreamError={(err) => {
            console.error(err);
            setStreamingText("");
            setIsLoading(false);
          }}
          model={selectedModel}
          disabled={isLoading}
          isEmptyChat={isEmptyChat}
        />
      </SidebarInset>
    </SidebarProvider>
  );
}