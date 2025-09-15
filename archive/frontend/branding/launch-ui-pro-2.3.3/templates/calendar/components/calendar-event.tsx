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

  // Get event theme color classes based on calendar color
  const getEventTheme = () => {
    const colorMap: Record<string, string> = {
      blue: "bg-blue-500/20 text-blue-800 dark:text-blue-200 border-blue-500/20",
      indigo:
        "bg-indigo-500/20 text-indigo-800 dark:text-indigo-200 border-indigo-500/20",
      purple:
        "bg-purple-500/20 text-purple-800 dark:text-purple-200 border-purple-500/20",
      pink: "bg-pink-500/20 text-pink-800 dark:text-pink-200 border-pink-500/20",
      red: "bg-red-500/20 text-red-800 dark:text-red-200 border-red-500/20",
      orange:
        "bg-orange-500/20 text-orange-800 dark:text-orange-200 border-orange-500/20",
      amber:
        "bg-amber-500/20 text-amber-800 dark:text-amber-200 border-amber-500/20",
      yellow:
        "bg-yellow-500/20 text-yellow-800 dark:text-yellow-200 border-yellow-500/20",
      lime: "bg-lime-500/20 text-lime-800 dark:text-lime-200 border-lime-500/20",
      green:
        "bg-green-500/20 text-green-800 dark:text-green-200 border-green-500/20",
      emerald:
        "bg-emerald-500/20 text-emerald-800 dark:text-emerald-200 border-emerald-500/20",
      teal: "bg-teal-500/20 text-teal-800 dark:text-teal-200 border-teal-500/20",
      cyan: "bg-cyan-500/20 text-cyan-800 dark:text-cyan-200 border-cyan-500/20",
      sky: "bg-sky-500/20 text-sky-800 dark:text-sky-200 border-sky-500/20",
      gray: "bg-gray-500/10 dark:bg-gray-500/20 text-gray-800 dark:text-gray-200 border-gray-500/20",
      rose: "bg-rose-500/20 text-rose-800 dark:text-rose-200 border-rose-500/20",
    };

    return (
      colorMap[event.calendarColor] ||
      "bg-gray-500/20 text-gray-800 dark:text-gray-200 border-gray-500/20"
    );
  };

  // Get border color class based on calendar color
  const getBorderColorClass = () => {
    const colorMap: Record<string, string> = {
      blue: "border-blue-500",
      indigo: "border-indigo-500",
      purple: "border-purple-500",
      pink: "border-pink-500",
      red: "border-red-500",
      orange: "border-orange-500",
      amber: "border-amber-500",
      yellow: "border-yellow-500",
      lime: "border-lime-500",
      green: "border-green-500",
      emerald: "border-emerald-500",
      teal: "border-teal-500",
      cyan: "border-cyan-500",
      sky: "border-sky-500",
      gray: "border-gray-500",
      rose: "border-rose-500",
    };

    return colorMap[event.calendarColor] || "border-l-gray-500";
  };

  // For compact mode (month view), use a simplified layout
  if (isCompact) {
    return (
      <div
        className={cn(
          "flex h-full items-center gap-1 overflow-hidden rounded-sm px-1 text-xs",
          getEventTheme(),
          className,
        )}
      >
        <div
          className={`h-2 rounded-full border-r-2 ${getBorderColorClass()}`}
        ></div>
        <div className="truncate font-medium">{event.name}</div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex gap-2 overflow-hidden rounded-md border p-1.5 pb-0 text-xs",
        getEventTheme(),
        className,
      )}
      style={{
        width: "calc(100% - 7px)",
        margin: "3px",
        height: isAllDay ? "auto" : "calc(100% - 7px)",
      }}
    >
      <div className={`mb-1.5 w-0 border-r ${getBorderColorClass()}`}></div>
      <div
        className="flex w-full flex-col gap-1 overflow-hidden"
        style={{
          marginTop: isShortEvent && !isAllDay ? "-4px" : "0",
        }}
      >
        <div className="shrink-0 truncate font-medium">{event.name}</div>
        <div className="truncate opacity-70">{formatEventTime()}</div>
      </div>
    </div>
  );
}

export default CalendarEvent;
