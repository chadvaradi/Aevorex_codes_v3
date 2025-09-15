export interface Chat {
  id: string;
  title: string;
  previewText: string;
  createdAt: string;
  updatedAt: string;
  isActive?: boolean;
}

export const chats: Chat[] = [
  {
    id: "chat1",
    title: "Website Development",
    previewText: "I need help building a responsive website for my business...",
    createdAt: "2025-03-17T09:15:00Z",
    updatedAt: "2025-03-17T09:45:00Z",
  },
  {
    id: "chat2",
    title: "React Hooks",
    previewText: "Can you explain how useEffect works in React?",
    createdAt: "2025-03-16T14:22:00Z",
    updatedAt: "2025-03-16T14:40:00Z",
  },
  {
    id: "chat3",
    title: "SEO Optimization",
    previewText:
      "What are the best practices for optimizing a website for search engines?",
    createdAt: "2025-03-12T11:05:00Z",
    updatedAt: "2025-03-12T11:30:00Z",
  },
  {
    id: "chat4",
    title: "Tailwind CSS Tips",
    previewText:
      "I'm looking for some advanced Tailwind CSS techniques for my project",
    createdAt: "2025-03-11T16:45:00Z",
    updatedAt: "2025-03-11T17:10:00Z",
  },
  {
    id: "chat5",
    title: "Database Design",
    previewText:
      "How should I structure my database for a social media application?",
    createdAt: "2025-03-01T10:30:00Z",
    updatedAt: "2025-03-01T11:15:00Z",
  },
  {
    id: "chat6",
    title: "Authentication Systems",
    previewText: "What's the most secure way to implement user authentication?",
    createdAt: "2025-02-20T13:20:00Z",
    updatedAt: "2025-02-20T13:45:00Z",
  },
  {
    id: "chat7",
    title: "Performance Optimization",
    previewText: "My React app is slow. How can I improve its performance?",
    createdAt: "2025-01-15T15:10:00Z",
    updatedAt: "2025-01-15T15:35:00Z",
  },
];

// Create a method to get chats sorted by update date
export const getSortedChats = () => {
  return [...chats].sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
  );
};

// Get a chat by ID
export const getChatById = (id: string) => {
  return chats.find((chat) => chat.id === id);
};
