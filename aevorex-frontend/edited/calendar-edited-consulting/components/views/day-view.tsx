import { useMemo } from "react";
import CalendarEvent from "../calendar-event";

/**
 * DayView Component
 *
 * Displays a single day view with hourly slots and events.
 * Structured similarly to WeekView but with only one column.
 */
interface DayViewProps {
  date: Date; // Required date prop
  events?: any[];
  currentTime?: Date; // Current time for time indicator
}

// Helper function to format time (e.g., "09:00")
function formatTime(hour: number): string {
  return `${hour.toString().padStart(2, "0")}:00`;
}

// Helper function to check if two dates are the same day
function isSameDay(date1: Date, date2: Date): boolean {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
}

function DayView({ date, events = [], currentTime }: DayViewProps) {
  // Get the day of the week (e.g., "Wednesday")
  const dayOfWeek = date.toLocaleDateString("en-US", { weekday: "long" });

  // Generate hours for the time grid (7:00 to 00:00)
  const hours = useMemo(() => {
    return Array.from({ length: 11 }, (_, i) => i + 8);
  }, []);

  // Check if displayed date is the current date
  const isCurrentDay = useMemo(() => {
    if (!currentTime) return false;
    return isSameDay(date, currentTime);
  }, [date, currentTime]);

  // Calculate current time position if provided and if it's the current day
  const currentTimePosition = useMemo(() => {
    if (!currentTime || !isCurrentDay) return null;

    const hour = currentTime.getHours();
    const minutes = currentTime.getMinutes();
    const hourDecimal = hour + minutes / 60;

    // Only show time marker if it's within our displayed hours
    if (hourDecimal < hours[0] || hourDecimal > hours[hours.length - 1] + 1) {
      return null;
    }

    return {
      top: (hourDecimal - hours[0]) * 56, // 56px = 14px * 4 (height of hour cell)
      time: `${hour.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`,
    };
  }, [currentTime, hours, isCurrentDay]);

  // Process events for the day view
  const processedEvents = useMemo(() => {
    // Filter events for the selected day
    const dayEvents = events.filter((event) => {
      const eventDate = new Date(event.start);
      return isSameDay(eventDate, date);
    });

    // Check if events are all-day events
    const allDayEvents: any[] = [];
    const timeEvents: any[] = [];

    dayEvents.forEach((event) => {
      const startDate = new Date(event.start);
      const endDate = new Date(event.end);

      // Check if it's an all-day event (spans 24 hours or has specific all-day flag)
      const isAllDay =
        endDate.getTime() - startDate.getTime() >= 24 * 60 * 60 * 1000 ||
        (startDate.getHours() === 0 &&
          startDate.getMinutes() === 0 &&
          endDate.getHours() === 23 &&
          endDate.getMinutes() === 59);

      if (isAllDay) {
        allDayEvents.push({ ...event, isAllDay });
      } else {
        timeEvents.push({
          ...event,
          startHour: startDate.getHours() + startDate.getMinutes() / 60,
          endHour: endDate.getHours() + endDate.getMinutes() / 60,
        });
      }
    });

    // Sort events by start time
    timeEvents.sort((a, b) => a.startHour - b.startHour);

    // Process events to detect overlaps
    const processedTimeEvents = timeEvents.map((event, index, arr) => {
      // Check if this event overlaps with any previous events
      let leftMargin = 0;

      // Loop through previous events to check for overlaps
      for (let j = 0; j < index; j++) {
        const prevEvent = arr[j];
        // If the current event starts before the previous event ends, they overlap
        if (event.startHour < prevEvent.endHour) {
          leftMargin = 12; // Add a 12px left margin for overlapping events
          break;
        }
      }

      return {
        ...event,
        leftMargin,
      };
    });

    return { allDayEvents, timeEvents: processedTimeEvents };
  }, [events, date]);

  return (
    <div className="h-full w-full text-left">
      <div className="flex h-full flex-col">
        {/* Day header row */}
        <div className="flex">
          {/* Day name with date */}
          <div className="flex flex-1 min-w-0">
            <div className="border-border dark:border-border/15 text-muted-foreground flex-1 basis-0 min-w-0 border-b px-4 pb-4">
              {dayOfWeek}
            </div>
          </div>
        </div>

        {/* All-day events section */}
        <div className="border-border dark:border-border/15 border-b">
          <div className="flex">
            {/* Time gutter for all-day section */}
            <div className="border-border dark:border-border/15 text-muted-foreground w-16 flex-shrink-0 border-r p-2 text-xs">
              all-day
            </div>

            {/* All-day events grid */}
            <div className="w-full">
              <div className="border-border dark:border-border/15 min-h-[24px] flex-1 border-r">
                {processedEvents.allDayEvents.map((event) => (
                  <CalendarEvent
                    key={`all-day-event-${event.id}`}
                    event={event}
                    isAllDay={true}
                    className="min-h-[48px]"
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Time grid */}
        <div className="flex flex-1 min-w-0 overflow-auto">
          {/* Time gutter */}
          <div className="w-16 flex-shrink-0">
            <div className="border-border dark:border-border/15 h-7 border-r"></div>
            {hours.map((hour) => (
              <div
                key={`hour-${hour}`}
                className="border-border dark:border-border/15 text-muted-foreground h-14 border-r text-xs"
              >
                <div className="relative -top-7 flex h-14 items-center justify-end p-2">
                  {formatTime(hour)}
                </div>
              </div>
            ))}
          </div>

          {/* Day grid */}
          <div className="relative flex flex-1 min-w-0">
            <div className="border-border dark:border-border/15 flex-1 basis-0 min-w-0">
              {/* Hour cells with events */}
              <div className="border-border dark:border-border/15 h-7 border-r border-b"></div>
              <div className="relative">
                {hours.map((hour) => (
                  <div
                    key={`day-${hour}`}
                    className="border-border dark:border-border/15 h-14 border-r border-b"
                  />
                ))}

                {/* Render events for this day */}
                {processedEvents.timeEvents.map((event) => {
                  // Calculate position and height based on event time
                  const top = (event.startHour - hours[0]) * 56; // 56px = 14px * 4 (height of hour cell)
                  const height = Math.max(
                    (event.endHour - event.startHour) * 56,
                    28,
                  ); // Minimum height of 28px

                  return (
                    <div
                      key={`event-${event.id}`}
                      className="absolute right-0 left-0"
                      style={{
                        top: `${top}px`,
                        height: `${height}px`,
                        paddingLeft: event.leftMargin
                          ? `${event.leftMargin}px`
                          : "0",
                      }}
                    >
                      <CalendarEvent event={event} />
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Current time indicator - only shown if displayed date is the current date */}
            {currentTimePosition && (
              <div
                className="absolute right-0 left-0 z-10 flex items-center"
                style={{ top: `${currentTimePosition.top + 28}px` }}
              >
                <div className="bg-brand-foreground absolute -left-1 h-2 w-2 rounded-sm text-xs font-medium" />
                <div className="border-brand-foreground flex-1 border-t"></div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DayView;
