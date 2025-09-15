/**
 * CalendarEvent Component
 *
 * Displays a single calendar event with title, time, and styling based on the calendar color.
 */

import { cn } from "@/lib/utils";

interface CalendarEventProps {
  event: {
    id: string;
    name: string;
    start: string;
    end: string;
    calendarColor: string;
    calendarName: string;
    accountName: string;
    url?: string;
  };
  isAllDay?: boolean;
  isCompact?: boolean;
  className?: string;
}

function CalendarEvent({
  event,
  isAllDay = false,
  isCompact = false,
  className,
}: CalendarEventProps) {
  // Format the event time (e.g., "10:00 - 11:30")
  const formatEventTime = () => {
    if (isAllDay) return "All day";

    const startDate = new Date(event.start);
    const endDate = new Date(event.end);

    const startHours = startDate.getHours().toString().padStart(2, "0");
    const startMinutes = startDate.getMinutes().toString().padStart(2, "0");
    const endHours = endDate.getHours().toString().padStart(2, "0");
    const endMinutes = endDate.getMinutes().toString().padStart(2, "0");

    return `${startHours}:${startMinutes} - ${endHours}:${endMinutes}`;
  };

  // Calculate event duration in minutes
  const getEventDurationMinutes = () => {
    if (isAllDay) return 24 * 60; // All day events are 24 hours

    const startDate = new Date(event.start);
    const endDate = new Date(event.end);

    return (endDate.getTime() - startDate.getTime()) / (1000 * 60);
  };

  // Check if event is shorter than 40 minutes
  const isShortEvent = getEventDurationMinutes() < 40;

  // Get theme classes based on calendar color
  const getEventTheme = () => {
    const colorMap: Record<string, string> = {
      blue: "bg-blue-500/20 text-blue-800 dark:text-blue-200 border-blue-500/20",
      green: "bg-green-500/20 text-green-800 dark:text-green-200 border-green-500/20",
      red: "bg-red-500/20 text-red-800 dark:text-red-200 border-red-500/20",
      yellow: "bg-yellow-500/20 text-yellow-800 dark:text-yellow-200 border-yellow-500/20",
      purple: "bg-purple-500/20 text-purple-800 dark:text-purple-200 border-purple-500/20",
      pink: "bg-pink-500/20 text-pink-800 dark:text-pink-200 border-pink-500/20",
      indigo: "bg-indigo-500/20 text-indigo-800 dark:text-indigo-200 border-indigo-500/20",
      orange: "bg-orange-500/20 text-orange-800 dark:text-orange-200 border-orange-500/20",
      teal: "bg-teal-500/20 text-teal-800 dark:text-teal-200 border-teal-500/20",
      cyan: "bg-cyan-500/20 text-cyan-800 dark:text-cyan-200 border-cyan-500/20",
    };

    return (
      colorMap[event.calendarColor] ||
      "bg-gray-500/20 text-gray-800 dark:text-gray-200 border-gray-500/20"
    );
  };

  // Get border color class
  const getBorderColorClass = () => {
    const colorMap: Record<string, string> = {
      blue: "border-blue-500",
      green: "border-green-500",
      red: "border-red-500",
      yellow: "border-yellow-500",
      purple: "border-purple-500",
      pink: "border-pink-500",
      indigo: "border-indigo-500",
      orange: "border-orange-500",
      teal: "border-teal-500",
      cyan: "border-cyan-500",
    };

    return colorMap[event.calendarColor] || "border-gray-500";
  };

  // For compact mode (month view), use a simplified layout
  if (isCompact) {
    return (
      <div
        title={event.name}
        className={cn(
          "relative flex h-full items-center gap-1 overflow-hidden rounded-[4px] px-1 py-[2px] text-[10px] leading-3 hover:brightness-110 cursor-pointer",
          getEventTheme(),
          className
        )}
      >
        <div className={`h-[10px] w-[2px] rounded-sm shrink-0 ${getBorderColorClass()}`} />
        <div className="min-w-0 truncate font-medium">{event.name}</div>

        {event.url && (
          <a
            href={event.url}
            target="_blank"
            rel="noopener noreferrer"
            className="absolute inset-0 z-10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
            aria-label={`Open ${event.name}`}
          />
        )}
      </div>
    );
  }

  return (
    <div
      className={cn(
        "relative flex gap-2 overflow-hidden rounded-md border p-1.5 pb-0 text-xs hover:brightness-110 cursor-pointer",
        getEventTheme(),
        className
      )}
      style={{
        width: "calc(100% - 7px)",
        margin: "3px",
        height: isAllDay ? "auto" : "calc(100% - 7px)",
      }}
    >
      <div className={`mb-1.5 w-0 border-r ${getBorderColorClass()}`} />
      <div
        className={cn(
          "flex flex-col gap-1 min-w-0 flex-1",
          isShortEvent && "justify-center"
        )}
      >
        <div className="font-medium truncate">{event.name}</div>
        {/* <div className="text-[10px] opacity-75">
          {(() => {
            const pad = (n: number) => n.toString().padStart(2, "0");
            const s = new Date(event.start);
            const e = new Date(event.end);
            return `${pad(s.getHours())}:${pad(s.getMinutes())} - ${pad(e.getHours())}:${pad(e.getMinutes())}`;
          })()}
        </div> */}
      </div>

      {event.url && (
        <a
          href={event.url}
          target="_blank"
          rel="noopener noreferrer"
          className="absolute inset-0 z-10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
          aria-label={`Open ${event.name}`}
        />
      )}
    </div>
  );
}

export default CalendarEvent;