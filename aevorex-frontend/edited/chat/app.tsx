"use client";

import React, { useEffect, useState } from "react";
import { AppSidebar } from "./components/chat-sidebar";
import ChatHeader from "./components/chat-header";
import ChatMain from "./components/chat-main";
import ChatInput from "./components/chat-input";
import { SidebarInset, SidebarProvider } from "../../launch-ui-pro-2.3.3/ui/sidebar";

import { Chat, getChatById } from "./data/chats";
import { Message, getMessagesByChatId } from "./data/messages";
import { chatStream, getModels } from "@/src/lib/chatApi";

// lokális üzenet objektum (nincs mock store módosítás)
const createMessageObject = (
  chatId: string,
  content: string,
  sender: "user" | "ai",
  extra?: Partial<Message>
): Message => ({
  id: `msg-${Date.now()}-${Math.random().toString(36).slice(2)}`,
  chatId,
  content,
  sender,
  timestamp: new Date().toISOString(),
  ...(extra || {}),
});

// triggerek: /image … | /img … | kép: … | kep: …
// elfogadja: /image | /img | image: | kép: | kep:  + BÁRMI utána, több soron is
const IMG_RE = /^\s*(?:\/image|\/img|image:|kép:|kep:)\s*([\s\S]+)$/i;

const getImagePrompt = (text: string) => {
  const m = text.match(IMG_RE);
  return m ? m[1].trim() : null;
};

// képgeneráló backend hívás
async function callImageApi(prompt: string): Promise<string> {
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  const endpoint = `${API_BASE}/api/image/generate`;

  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, model: "gemini-2.5-flash-image", n: 1 }),
  });

  const raw = await res.text();
  console.log("[callImageApi] status:", res.status, "raw:", raw);
  console.log("[callImageApi] response headers:", Object.fromEntries(res.headers.entries()));

  // hibás státusz → részletes hiba
  if (!res.ok) {
    try {
      const err = JSON.parse(raw);
      throw new Error(err?.detail || err?.error || `Image API error (${res.status})`);
    } catch {
      throw new Error(`Image API error (${res.status}): ${raw}`);
    }
  }

  // üres body?
  if (!raw || raw.trim() === "") {
    throw new Error("Image API returned empty body.");
  }

  let data: any;
  try {
    data = JSON.parse(raw);
  } catch {
    throw new Error("Invalid JSON from image API");
  }

  // -------------- SÉMA NORMALIZÁLÁS --------------
  // 1) preferált: { items: [{ url, b64, mime_type }] }
  const first = data?.items?.[0];
  if (first?.url) {
    console.log("[callImageApi] using URL from items[0]:", first.url);
    return absolutize(first.url, API_BASE);
  }
  if (first?.b64) {
    console.log("[callImageApi] using base64 from items[0]");
    return `data:${first?.mime_type || "image/png"};base64,${first.b64}`;
  }

  // 2) alternatívák, néha felső szinten jönnek
  if (data?.url) {
    console.log("[callImageApi] using URL from root:", data.url);
    return absolutize(data.url, API_BASE);
  }
  if (data?.image_url) {
    console.log("[callImageApi] using image_url from root:", data.image_url);
    return absolutize(data.image_url, API_BASE);
  }
  if (data?.path) {
    console.log("[callImageApi] using path from root:", data.path);
    return absolutizePath(data.path, API_BASE);
  }
  if (data?.filename) {
    console.log("[callImageApi] using filename from root:", data.filename);
    return absolutize(`/static/images/${data.filename}`, API_BASE);
  }

  // 3) fallback: ha egyetlen stringet kaptunk, és png/jpg-nek tűnik
  if (typeof data === "string" && /\.(png|jpg|jpeg|webp)(\?.*)?$/i.test(data)) {
    console.log("[callImageApi] using string as image path:", data);
    return absolutize(data, API_BASE);
  }

  console.error("[callImageApi] Unexpected response shape:", data);
  throw new Error("Image API returned no usable result.");

  // ---- helpers ----
  function absolutize(u: string, base: string) {
    if (!u) return u;
    if (u.startsWith("http://") || u.startsWith("https://") || u.startsWith("data:")) return u;
    if (u.startsWith("/")) return `${base}${u}`;
    return `${base}/${u}`;
  }
  function absolutizePath(p: string, base: string) {
    if (!p) return p;
    // ha már /static/... alak, hagyjuk meg és abszolutizáljuk
    if (p.startsWith("/")) return `${base}${p}`;
    // ha csak fájlnév jött
    if (!p.includes("/")) return `${base}/static/images/${p}`;
    // ha relatív 'static/images/...' jött
    return `${base}/${p}`;
  }
}

export default function ChatApp() {
  const [activeChat, setActiveChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // (opcionális) modellek a chatStream-hez
  const [availableModels, setAvailableModels] = useState<Record<string, string>>({});
  const [selectedModel, setSelectedModel] = useState<string>("deepseek-free");

  useEffect(() => {
    getModels()
      .then((data: any) => {
        if (data?.models) setAvailableModels(data.models);
        if (data?.default) setSelectedModel(data.default);
      })
      .catch(() => {});
  }, []);

  const handleSelectChat = (chatId: string) => {
    if (chatId === "empty") {
      setActiveChat({
        id: "empty",
        title: "New chat",
        previewText: "",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
      setMessages([]);
      return;
    }
    const chat = getChatById(chatId);
    if (chat) {
      setActiveChat(chat);
      setMessages(getMessagesByChatId(chatId));
    }
  };

  const handleSendMessage = async (content: string) => {
    const text = content.trim();
    if (!text) return;

    // biztosíts chatet
    if (!activeChat) {
      setActiveChat({
        id: "empty",
        title: "New chat",
        previewText: text,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
    }
    const chatId = activeChat?.id || "empty";

    // lokálisan add hozzá a user üzenetet
    const userMsg = createMessageObject(chatId, text, "user");
    setMessages((prev) => [...prev, userMsg]);

    const imgPrompt = getImagePrompt(text);
    console.log(imgPrompt ? "[UI] IMAGE mode" : "[UI] CHAT mode");

    setIsLoading(true);
    try {
      if (imgPrompt) {
        // IMAGE mód
        const url = await callImageApi(imgPrompt);
        const aiImg = createMessageObject(
          chatId,
          `Generated image for: "${imgPrompt}"`,
          "ai",
          { imageSrc: url }
        );
        setMessages((prev) => [...prev, aiImg]);
      } else {
        // CHAT mód — streamelve a saját backendről
        const apiMessages = [
          ...messages.map((m) => ({
            role: m.sender === "ai" ? ("assistant" as const) : ("user" as const),
            content: m.content,
          })),
          { role: "user" as const, content: text },
        ];

        let buffer = "";
        for await (const chunk of chatStream({ messages: apiMessages, model: selectedModel })) {
          buffer += chunk;
        }
        const finalText = buffer.trim() || "…";
        const aiMsg = createMessageObject(chatId, finalText, "ai");
        setMessages((prev) => [...prev, aiMsg]);

        const preview = finalText.length > 200 ? finalText.slice(0, 200) + "…" : finalText;
        setActiveChat((prev) =>
          prev ? { ...prev, previewText: preview, updatedAt: new Date().toISOString() } : prev
        );
      }
    } catch (e: any) {
      const errMsg = createMessageObject(chatId, `⚠️ ${e?.message || "Unexpected error."}`, "ai");
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const isEmptyChat = messages.length === 0 && !isLoading;

  return (
    <SidebarProvider
      className="glass-3 relative h-[900px] w-full overflow-hidden rounded-xl"
      style={{ "--sidebar-width": "19rem" } as React.CSSProperties}
    >
      <AppSidebar onSelectChat={handleSelectChat} activeChat={activeChat} />
      <SidebarInset className="flex flex-col">
        <ChatHeader activeChat={activeChat} />
        <ChatMain messages={messages} loading={isLoading} isEmptyChat={isEmptyChat} />
        <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} isEmptyChat={isEmptyChat} />
      </SidebarInset>
    </SidebarProvider>
  );
}