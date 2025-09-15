import React from "react";
import { SidebarTrigger } from "../../../launch-ui-pro-2.3.3/ui/sidebar";
import { Chat } from "../data/chats";

interface ChatHeaderProps {
  activeChat: Chat | null;
}

const ChatHeader: React.FC<ChatHeaderProps> = ({ activeChat }) => {
  return (
    <header className="bg-background/50 absolute left-0 z-10 ml-2 flex h-16 w-full shrink-0 items-center gap-2 px-4 backdrop-blur-lg dark:bg-transparent">
      <SidebarTrigger className="-ml-1" />
      <h2 className="truncate font-semibold dark:drop-shadow">
        {activeChat ? activeChat.title : "New chat"}
      </h2>
    </header>
  );
};

export default ChatHeader;
