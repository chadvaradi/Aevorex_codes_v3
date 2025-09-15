import React, { ReactNode, useState, useEffect } from "react";
import { Message } from "../data/messages";
import { FadeInText } from "./fade-in-text";
import Image from "next/image";
import ImageSkeleton from "./image-skeleton";

interface MessageBubbleProps {
  message: Message;
  isLatestMessage?: boolean; // Add property to track if this is the latest message
}

// Type for processed message content fragments
type MessageFragment = {
  type: "text" | "bold" | "link" | "codeBlock" | "inlineCode" | "lineBreak";
  content: string;
  url?: string;
  language?: string;
};

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isLatestMessage = false, // Default to false
}) => {
  const isUser = message.sender === "user";
  // Should animate only if: AI message + latest message
  const shouldAnimate = !isUser && isLatestMessage;

  // Add state to control visibility of AI messages
  const [isVisible, setIsVisible] = useState(isUser); // User messages are always immediately visible
  // Add state for image loading
  const [isImageLoading, setIsImageLoading] = useState(true);
  // Add state to control visibility of text when there's an image
  const [showText, setShowText] = useState(!message.imageSrc);

  // For AI messages, delay visibility slightly to avoid flash before animation
  useEffect(() => {
    if (!isUser) {
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, 50); // Short delay to prevent flash

      return () => clearTimeout(timer);
    }
  }, [isUser]);

  // Simulate image generation delay
  useEffect(() => {
    if (message.imageSrc) {
      // Set text to initially hidden when we have an image
      setShowText(false);

      const timer = setTimeout(() => {
        setIsImageLoading(false);

        // Show text after image has loaded with a small delay for better UX
        setTimeout(() => {
          setShowText(true);
        }, 500);
      }, 6000); // Show skeleton for 3 seconds to simulate generation

      return () => clearTimeout(timer);
    } else {
      // No image, always show text
      setShowText(true);
    }
  }, [message.imageSrc]);

  // Check for code blocks first to handle them separately
  const hasCodeBlocks = message.content.includes("```");
  let fragments: MessageFragment[] = [];

  if (hasCodeBlocks) {
    fragments = processMessageWithCodeBlocks(message.content);
  } else {
    fragments = parseMessageContent(message.content);
  }

  return (
    <div
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"} ${
        isVisible ? "opacity-100" : "opacity-0"
      }`}
    >
      <div
        className={`max-w-[min(720px,85%)] px-4 py-2.5 ${isUser ? "glass-4 rounded-2xl shadow-md" : ""}`}
      >
        <div className="break-words whitespace-pre-wrap">
          {/* Render image or skeleton first, if available */}
          {message.imageSrc && (
            <div className="mb-3 h-[300px] w-[300px]">
              {isImageLoading ? (
                <ImageSkeleton />
              ) : (
                <div className="glass-4 rounded-lg border-0">
                  <Image
                    src={message.imageSrc}
                    alt="AI generated image"
                    width={500}
                    height={300}
                    className="animate-reveal relative size-full h-full w-full rounded-lg shadow-lg"
                  />
                </div>
              )}
            </div>
          )}

          {/* Render text only after image has loaded or if there's no image */}
          {showText && (
            <div
              className={`${!isImageLoading && message.imageSrc ? "animate-appear" : ""}`}
            >
              {renderMessageFragments(fragments, shouldAnimate)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Process messages with complex code blocks
const processMessageWithCodeBlocks = (content: string): MessageFragment[] => {
  const fragments: MessageFragment[] = [];

  // First, split the content by code block delimiters
  // This regex matches the code block start (```) with optional language specifier
  // and the end delimiter (```)
  const pattern = /(```\w*[\s\S]*?```)/g;
  const parts = content.split(pattern);

  for (let i = 0; i < parts.length; i++) {
    const part = parts[i];

    // Skip empty parts
    if (!part.trim()) continue;

    // Check if this part is a code block
    if (part.startsWith("```") && part.endsWith("```")) {
      // Extract the language and code content
      const firstLineEnd = part.indexOf("\n");
      const languageLine = part.substring(3, firstLineEnd).trim();
      const codeContent = part
        .substring(firstLineEnd + 1, part.length - 3)
        .trim();

      fragments.push({
        type: "codeBlock",
        content: codeContent,
        language: languageLine,
      });
    } else {
      // This is regular text, parse it for other formatting
      const parsedFragments = parseMessageContent(part);
      fragments.push(...parsedFragments);
    }
  }

  return fragments;
};

// Parse message content into fragments
const parseMessageContent = (content: string): MessageFragment[] => {
  const fragments: MessageFragment[] = [];

  // Split the content by line breaks first to handle them properly
  const lines = content.split("\n");

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    let currentIndex = 0;

    // Process the line to find formatting patterns
    while (currentIndex < line.length) {
      // Bold text (**text**)
      const boldMatch = line.slice(currentIndex).match(/^\*\*(.*?)\*\*/);
      if (boldMatch && boldMatch[1]) {
        fragments.push({
          type: "bold",
          content: boldMatch[1],
        });
        currentIndex += boldMatch[0].length;
        continue;
      }

      // Link with text [text](url)
      const linkMatch = line
        .slice(currentIndex)
        .match(/^\[(.*?)\]\((https?:\/\/[^\s]+)\)/);
      if (linkMatch && linkMatch[1] && linkMatch[2]) {
        fragments.push({
          type: "link",
          content: linkMatch[1],
          url: linkMatch[2],
        });
        currentIndex += linkMatch[0].length;
        continue;
      }

      // Plain URL
      const urlMatch = line.slice(currentIndex).match(/^(https?:\/\/[^\s]+)/);
      if (urlMatch && urlMatch[1]) {
        fragments.push({
          type: "link",
          content: urlMatch[1],
          url: urlMatch[1],
        });
        currentIndex += urlMatch[0].length;
        continue;
      }

      // Inline code (`code`)
      const inlineCodeMatch = line.slice(currentIndex).match(/^`([^`]+)`/);
      if (inlineCodeMatch && inlineCodeMatch[1]) {
        fragments.push({
          type: "inlineCode",
          content: inlineCodeMatch[1],
        });
        currentIndex += inlineCodeMatch[0].length;
        continue;
      }

      // If no pattern matches, collect regular text until a pattern is found
      let textEnd = line.length;
      const patterns = ["\\*\\*", "\\[", "https?://", "`"];

      for (const pattern of patterns) {
        const match = line.slice(currentIndex).match(new RegExp(`${pattern}`));
        if (match && match.index !== undefined) {
          const possibleEnd = currentIndex + match.index;
          textEnd = Math.min(textEnd, possibleEnd);
        }
      }

      if (textEnd > currentIndex) {
        fragments.push({
          type: "text",
          content: line.slice(currentIndex, textEnd),
        });
        currentIndex = textEnd;
      } else {
        // No pattern found, add the remaining text
        fragments.push({
          type: "text",
          content: line.slice(currentIndex),
        });
        break;
      }
    }

    // Add line break if not the last line
    if (i < lines.length - 1) {
      fragments.push({ type: "lineBreak", content: "" });
    }
  }

  return fragments;
};

// Helper function to escape HTML special characters
const escapeHTML = (text: string): string => {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
};

// Wrap content in FadeInText if animation is enabled
const maybeAnimateContent = (
  content: string,
  shouldAnimate: boolean,
): React.ReactNode => {
  if (!shouldAnimate) return content;

  return (
    <FadeInText
      animation="blurIn"
      as="span"
      by="word"
      duration={content.length * 0.02}
      startOnView={false}
    >
      {content}
    </FadeInText>
  );
};

// Render message fragments to React components
const renderMessageFragments = (
  fragments: MessageFragment[],
  shouldAnimate: boolean,
): ReactNode[] => {
  return fragments.map((fragment, index) => {
    switch (fragment.type) {
      case "bold":
        return (
          <strong key={index}>
            {maybeAnimateContent(fragment.content, shouldAnimate)}
          </strong>
        );
      case "link":
        return (
          <a
            key={index}
            href={fragment.url}
            target="_blank"
            rel="noopener noreferrer"
            className="underline"
          >
            {maybeAnimateContent(fragment.content, shouldAnimate)}
          </a>
        );

      case "codeBlock":
        // Code blocks don't use animation
        return (
          <pre
            key={index}
            className="glass-3 text-muted-foreground my-2 overflow-x-auto rounded-lg px-2 font-mono text-sm"
          >
            <code
              dangerouslySetInnerHTML={{ __html: escapeHTML(fragment.content) }}
            />
          </pre>
        );

      case "inlineCode":
        // Inline code doesn't use animation
        return (
          <code
            key={index}
            className="glass-3 text-muted-foreground rounded px-1 font-mono text-sm"
            dangerouslySetInnerHTML={{ __html: escapeHTML(fragment.content) }}
          />
        );

      case "lineBreak":
        return <br key={index} />;

      case "text":
      default:
        return (
          <React.Fragment key={index}>
            {maybeAnimateContent(fragment.content, shouldAnimate)}
          </React.Fragment>
        );
    }
  });
};

export default MessageBubble;
