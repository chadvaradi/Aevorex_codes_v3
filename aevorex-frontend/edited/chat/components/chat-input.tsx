import React, { useState, FormEvent, KeyboardEvent } from "react";
import { Send, Mic, PenBox, Image, Plane } from "lucide-react";
import { Button } from "@/launch-ui-pro-2.3.3/ui/button";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  isEmptyChat?: boolean;
}

interface SuggestionCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick: () => void;
  tone?: "blue" | "indigo" | "purple" | "red" | "orange" | "amber" | "teal";
}

const getCardColorClass = (tone: string) => {
  const colorMap: Record<string, string> = {
    blue: "bg-blue-500/10 hover:bg-blue-500/15 border-blue-500/10 text-blue-800 dark:text-blue-200",
    indigo:
      "bg-indigo-500/10 hover:bg-indigo-500/15 border-indigo-500/10 text-indigo-800 dark:text-indigo-200",
    purple:
      "bg-purple-500/10 hover:bg-purple-500/15 border-purple-500/10 text-purple-800 dark:text-purple-200",
    red: "bg-red-500/10 hover:bg-red-500/15 border-red-500/10 text-red-800 dark:text-red-200",
    orange:
      "bg-orange-500/10 hover:bg-orange-500/15 border-orange-500/10 text-orange-800 dark:text-orange-200",
    amber:
      "bg-amber-500/10 hover:bg-amber-500/15 border-amber-500/10 text-amber-800 dark:text-amber-200",
    teal: "bg-teal-500/10 hover:bg-teal-500/15 border-teal-500/10 text-teal-800 dark:text-teal-200",
    gray: "bg-zinc-500/10 hover:bg-zinc-500/15 border-zinc-500/10 text-zinc-800 dark:text-zinc-200",
  };

  return (
    colorMap[tone] ||
    "bg-zinc-500/20 border-zinc-500/10 text-zinc-800 dark:text-zinc-200"
  );
};

const SuggestionCard: React.FC<SuggestionCardProps> = ({
  title,
  description,
  icon,
  onClick,
  tone = "gray",
}) => {
  return (
    <button
      className={cn(
        "flex cursor-pointer flex-col gap-2 rounded-xl border p-4 text-left transition-colors",
        getCardColorClass(tone),
      )}
      onClick={onClick}
    >
      <div className="flex items-center gap-2">
        {icon}
        <h3 className="font-semibold">{title}</h3>
      </div>
      <p className="text-sm opacity-50">{description}</p>
    </button>
  );
};

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  isEmptyChat = false,
}) => {
  const [message, setMessage] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleSuggestionClick = (suggestionText: string) => {
    onSendMessage(suggestionText);
  };

  return (
    <div
      className={cn(
        "mx-auto flex w-full max-w-[1400px] flex-col justify-center px-2 pb-2 transition-all duration-700",
        isEmptyChat && "max-w-3xl flex-1",
      )}
    >
      {isEmptyChat && (
        <div className="flex flex-col items-center justify-center pb-4 text-center">
          <h1 className="mb-6 text-3xl font-bold">What can I help with?</h1>

          <div className="grid w-full auto-rows-min gap-4 md:grid-cols-3">
            <SuggestionCard
              title="Write an invitation"
              description="Prepare an invitation for an event or a party"
              icon={<PenBox className="size-4" aria-label="Pen box icon" />}
              tone="indigo"
              onClick={() =>
                handleSuggestionClick(
                  "Write an invitation for a garden party at my house",
                )
              }
            />
            <SuggestionCard
              title="Create an image"
              description="Generate an image based on a prompt"
              icon={<Image className="size-4" aria-label="Image icon" />}
              tone="red"
              onClick={() =>
                handleSuggestionClick(
                  "Generate an abstract image of melting waves in pastel pearl colors",
                )
              }
            />
            <SuggestionCard
              title="Plan a trip"
              description="Find the best time to travel to Tokyo"
              icon={<Plane className="size-4" aria-label="Plane icon" />}
              tone="amber"
              onClick={() =>
                handleSuggestionClick("Help me plan my next trip to Tokyo")
              }
            />
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex items-end gap-2">
        <div className="relative flex flex-1">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything..."
            className="focus:ring-brand-foreground bg-accent/50 hover:bg-accent/60 border-border dark:border-border/10 w-full resize-none rounded-lg border p-3 pr-10 focus:ring-2 focus:outline-none"
            rows={1}
            style={{ minHeight: "100px", maxHeight: "200px" }}
            disabled={disabled}
          />
          {message ? (
            <Button
              size="icon"
              className="absolute right-2 bottom-2 rounded-full"
              type="submit"
            >
              <Send className="h-5 w-5" aria-label="Send message" />
            </Button>
          ) : (
            <Button
              size="icon"
              className="absolute right-2 bottom-2 rounded-full"
              onClick={() => {
                /* This would integrate voice input in a real app */
              }}
            >
              <Mic className="h-5 w-5" aria-label="Voice input" />
            </Button>
          )}
        </div>
      </form>
    </div>
  );
};

export default ChatInput;
