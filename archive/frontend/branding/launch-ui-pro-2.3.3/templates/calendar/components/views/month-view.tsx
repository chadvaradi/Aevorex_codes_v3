import { useMemo } from "react";
import CalendarEvent from "../calendar-event";
import { cn } from "@/lib/utils";

/**
 * MonthView Component
 *
 * Displays a month view with days as cells and events within each day.
 */
interface MonthViewProps {
  date: Date; // Required date prop
  events?: any[];
  currentTime?: Date; // Current time for time indicator and highlighting today
}

// Helper function to check if two dates are the same day
function isSameDay(date1: Date, date2: Date): boolean {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
}

// Helper function to check if two dates are in the same month
function isSameMonth(date1: Date, date2: Date): boolean {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth()
  );
}

// Helper function to get the first day of the month
function getFirstDayOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

// Helper function to get the last day of the month
function getLastDayOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0);
}

// Helper function to get days for the month grid (including days from prev/next months to fill the grid)
function getMonthDays(date: Date): Date[] {
  const firstDay = getFirstDayOfMonth(date);
  const lastDay = getLastDayOfMonth(date);

  // Get the day of the week for the first day (0 = Sunday, 1 = Monday, etc.)
  let firstDayOfWeek = firstDay.getDay();
  // Adjust for Monday as first day of week (0 = Monday, 6 = Sunday)
  firstDayOfWeek = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1;

  const daysInMonth = lastDay.getDate();
  const days: Date[] = [];

  // Add days from previous month to fill the first row
  const prevMonthLastDay = new Date(
    date.getFullYear(),
    date.getMonth(),
    0,
  ).getDate();
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const day = new Date(
      date.getFullYear(),
      date.getMonth() - 1,
      prevMonthLastDay - i,
    );
    days.push(day);
  }

  // Add days from current month
  for (let i = 1; i <= daysInMonth; i++) {
    const day = new Date(date.getFullYear(), date.getMonth(), i);
    days.push(day);
  }

  // Add days from next month to complete the grid (6 rows x 7 days = 42 cells)
  const remainingDays = 42 - days.length;
  for (let i = 1; i <= remainingDays; i++) {
    const day = new Date(date.getFullYear(), date.getMonth() + 1, i);
    days.push(day);
  }

  return days;
}

function MonthView({ date, events = [], currentTime }: MonthViewProps) {
  // Get all days for the month grid
  const monthDays = useMemo(() => getMonthDays(date), [date]);

  // Get day names for the header
  const dayNames = useMemo(() => {
    return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  }, []);

  // Process events for the month view
  const processedEvents = useMemo(() => {
    // Group events by day
    const eventsByDay: Record<string, any[]> = {};

    // Initialize arrays for each day
    monthDays.forEach((day) => {
      const dayKey = day.toISOString().split("T")[0];
      eventsByDay[dayKey] = [];
    });

    // Add events to their respective days
    events.forEach((event) => {
      const startDate = new Date(event.start);
      const dayKey = startDate.toISOString().split("T")[0];

      // Only add if the day is in our grid
      if (eventsByDay[dayKey]) {
        eventsByDay[dayKey].push(event);
      }
    });

    // Sort events for each day
    Object.keys(eventsByDay).forEach((dayKey) => {
      eventsByDay[dayKey].sort((a, b) => {
        const aStart = new Date(a.start).getTime();
        const bStart = new Date(b.start).getTime();
        return aStart - bStart;
      });
    });

    return eventsByDay;
  }, [events, monthDays]);

  // Check if a day is today
  const isToday = (day: Date): boolean => {
    if (!currentTime) return false;
    return isSameDay(day, currentTime);
  };

  // Check if a day is in the current month
  const isCurrentMonth = (day: Date): boolean => {
    return isSameMonth(day, date);
  };

  return (
    <div className="h-full w-full text-left">
      <div className="flex h-full flex-col">
        {/* Days header row */}
        <div className="border-border dark:border-border/15 flex border-b">
          {dayNames.map((day, index) => (
            <div key={`day-header-${index}`} className="flex-1 p-2 text-center">
              <span className="text-sm font-medium">{day}</span>
            </div>
          ))}
        </div>

        {/* Month grid */}
        <div className="grid flex-1 grid-cols-7 grid-rows-6 overflow-auto">
          {monthDays.map((day, index) => {
            const dayKey = day.toISOString().split("T")[0];
            const dayEvents = processedEvents[dayKey] || [];
            const dayNumber = day.getDate();

            return (
              <div
                key={`day-${index}`}
                className={`border-border dark:border-border/15 relative flex flex-col border-r border-b p-1 ${
                  !isCurrentMonth(day) ? "bg-muted/20" : ""
                }`}
              >
                {/* Day number */}
                <div className="mb-1 flex justify-end">
                  <span
                    className={cn(
                      "flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium",
                      isToday(day) &&
                        "bg-brand-foreground text-primary-foreground",
                      !isCurrentMonth(day) &&
                        "text-muted-foreground opacity-50",
                    )}
                  >
                    {dayNumber}
                  </span>
                </div>

                {/* Events for this day */}
                <div className="flex flex-1 flex-col gap-1 overflow-hidden">
                  {dayEvents.slice(0, 3).map((event, eventIndex) => (
                    <div
                      key={`event-${event.id}-${eventIndex}`}
                      className="h-5 overflow-hidden text-ellipsis whitespace-nowrap"
                    >
                      <CalendarEvent event={event} isCompact={true} />
                    </div>
                  ))}

                  {/* Show more indicator if there are more events */}
                  {dayEvents.length > 3 && (
                    <div className="text-muted-foreground text-xs">
                      +{dayEvents.length - 3} more
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default MonthView;
