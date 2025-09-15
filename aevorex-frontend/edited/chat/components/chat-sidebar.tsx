import * as React from "react";
import { getSortedChats, Chat } from "../data/chats";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/launch-ui-pro-2.3.3/ui/sidebar";
import { Button } from "@/launch-ui-pro-2.3.3/ui/button";
import { TeamSwitcher } from "@/launch-ui-pro-2.3.3/ui/team-switcher";
import LaunchUI from "@/launch-ui-pro-2.3.3/logos/launch-ui";
// Extend AppSidebarProps to include onSelectChat and activeChat props
interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {
  onSelectChat?: (chatId: string) => void;
  activeChat: Chat | null;
}

export function AppSidebar({
  onSelectChat,
  activeChat,
  ...props
}: AppSidebarProps) {
  // Get chats sorted by updated date
  const sortedChats = getSortedChats();

  // Group chats by date
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const lastWeek = new Date(today);
  lastWeek.setDate(lastWeek.getDate() - 7);

  const lastMonth = new Date(today);
  lastMonth.setMonth(lastMonth.getMonth() - 1);

  // Function to determine which group a chat belongs to
  const getChatGroup = (chat: Chat) => {
    const chatDate = new Date(chat.updatedAt);
    chatDate.setHours(0, 0, 0, 0);

    if (chatDate.getTime() === today.getTime()) {
      return "Today";
    } else if (chatDate.getTime() === yesterday.getTime()) {
      return "Yesterday";
    } else if (chatDate >= lastWeek) {
      return "Previous 7 Days";
    } else {
      return "Older";
    }
  };

  // Group chats by time period
  const chatGroups: Record<string, Chat[]> = {
    Today: [],
    Yesterday: [],
    "Previous 7 Days": [],
    "Previous 30 Days": [],
    Older: [],
  };

  sortedChats.forEach((chat) => {
    const group = getChatGroup(chat);
    chatGroups[group].push(chat);
  });

  const handleChatClick = (chatId: string) => {
    if (onSelectChat) {
      onSelectChat(chatId);
    }
  };

  return (
    <Sidebar variant="floating" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <TeamSwitcher
            teams={[
              {
                name: "Launch UI",
                logo: LaunchUI,
                plan: "Enterprise",
              },
            ]}
          />
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup className="p-4">
          <Button
            variant="glow"
            className="w-full"
            onClick={() => handleChatClick("empty")}
            data-active={activeChat?.id === "empty"}
            aria-selected={activeChat?.id === "empty"}
          >
            New chat
          </Button>
        </SidebarGroup>
        {/* Render chat groups that have chats */}
        {Object.entries(chatGroups).map(([groupName, groupChats]) => {
          if (groupChats.length === 0) return null;

          return (
            <SidebarGroup key={groupName} className="px-4">
              <SidebarGroupLabel>{groupName}</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {groupChats.map((chat) => (
                    <SidebarMenuItem key={chat.id}>
                      <SidebarMenuButton
                        isActive={activeChat?.id === chat.id}
                        onClick={() => handleChatClick(chat.id)}
                        className="h-12"
                      >
                        <div className="flex w-full flex-col gap-1 text-left">
                          <span className="truncate font-medium">
                            {chat.title}
                          </span>
                          <span className="text-muted-foreground truncate text-xs">
                            {chat.previewText}
                          </span>
                        </div>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          );
        })}
      </SidebarContent>
    </Sidebar>
  );
}
