import { useMemo } from "react";
import CalendarEvent from "../calendar-event";

/**
 * WeekView Component
 *
 * Displays a week view with days as columns and hours as rows.
 * Shows events positioned according to their time and duration.
 */
interface WeekViewProps {
  date: Date; // Required date prop
  events?: any[];
  currentTime?: Date; // Current time for time indicator
}

// Helper function to format time (e.g., "09:00")
function formatTime(hour: number): string {
  return `${hour.toString().padStart(2, "0")}:00`;
}

// Helper function to get the Monday of the week containing the given date
function getMonday(date: Date): Date {
  const day = date.getDay();
  const diff = date.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
  return new Date(date.getFullYear(), date.getMonth(), diff);
}

// Helper function to get day names and dates for the week
function getWeekDays(
  date: Date,
): { name: string; date: number; fullDate: Date }[] {
  const monday = getMonday(date);
  const weekDays = [];

  const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  for (let i = 0; i < 7; i++) {
    const currentDate = new Date(monday);
    currentDate.setDate(monday.getDate() + i);

    weekDays.push({
      name: dayNames[i],
      date: currentDate.getDate(),
      fullDate: new Date(currentDate), // Store the full date for comparison
    });
  }

  return weekDays;
}

// Helper function to check if two dates are the same day
function isSameDay(date1: Date, date2: Date): boolean {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
}

function WeekView({ date, events = [], currentTime }: WeekViewProps) {
  // Generate hours for the time grid (7:00 to 00:00)
  const hours = useMemo(() => {
    return Array.from({ length: 11 }, (_, i) => i + 8);
  }, []);

  // Get day names and dates for the week
  const weekDays = useMemo(() => getWeekDays(date), [date]);

  // Calculate current time position if provided
  const currentTimePosition = useMemo(() => {
    if (!currentTime) return null;

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
  }, [currentTime, hours]);

  // Process events for the week view
  const processedEvents = useMemo(() => {
    // Group events by day and determine if they're all-day events
    const eventsByDay: Record<number, any[]> = {};
    const allDayEvents: Record<number, any[]> = {};

    // Initialize arrays for each day
    for (let i = 0; i < 7; i++) {
      eventsByDay[i] = [];
      allDayEvents[i] = [];
    }

    events.forEach((event) => {
      const startDate = new Date(event.start);

      // Find the day index by comparing with the weekDays dates
      const dayIndex = weekDays.findIndex((day) =>
        isSameDay(day.fullDate, startDate),
      );

      // Skip events that don't fall within the current week
      if (dayIndex === -1) return;

      const endDate = new Date(event.end);

      // Check if it's an all-day event (spans 24 hours or has specific all-day flag)
      const isAllDay =
        endDate.getTime() - startDate.getTime() >= 24 * 60 * 60 * 1000 ||
        (startDate.getHours() === 0 &&
          startDate.getMinutes() === 0 &&
          endDate.getHours() === 23 &&
          endDate.getMinutes() === 59);

      if (isAllDay) {
        allDayEvents[dayIndex].push({ ...event, isAllDay });
      } else {
        eventsByDay[dayIndex].push({
          ...event,
          startHour: startDate.getHours() + startDate.getMinutes() / 60,
          endHour: endDate.getHours() + endDate.getMinutes() / 60,
          dayIndex,
        });
      }
    });

    // Sort events by start time for each day
    for (let i = 0; i < 7; i++) {
      eventsByDay[i].sort((a, b) => a.startHour - b.startHour);

      // Process events to detect overlaps
      eventsByDay[i] = eventsByDay[i].map((event, index, arr) => {
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
    }

    return { eventsByDay, allDayEvents };
  }, [events, weekDays]);

  return (
    <div className="h-full w-full text-left">
      <div className="flex h-full flex-col">
        {/* Days header row (same min width as grid) */}
        <div className="flex overflow-x-auto">
          {/* Empty corner cell */}
          <div className="border-border dark:border-border/15 w-16 flex-shrink-0 border-b">
            {/* Empty corner cell */}
          </div>

          {/* Day names with dates */}
          <div className="flex flex-1 min-w-[680px]">
            {weekDays.map((day, index) => {
              // Check if this is the current day
              const isCurrentDay = currentTime
                ? isSameDay(day.fullDate, currentTime)
                : false;

              return (
                <div
                  key={`day-header-${index}`}
                  className={`border-border dark:border-border/15 flex-1 border-b p-2 text-center text-sm font-medium ${
                    isCurrentDay ? "relative" : ""
                  }`}
                >
                  <span className={`${day.name}`}>{day.name}</span>{" "}
                  <span
                    className={`inline-flex items-center justify-center rounded-full ${
                      isCurrentDay
                        ? "bg-brand-foreground text-primary-foreground h-6 w-6"
                        : ""
                    }`}
                  >
                    {day.date}
                  </span>
                </div>
              );
            })}
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
            <div className="grid w-full grid-cols-7">
              {weekDays.map((day, index) => (
                <div
                  key={`all-day-${index}`}
                  className="border-border dark:border-border/15 min-h-[24px] flex-1 not-last:border-r"
                >
                  {processedEvents.allDayEvents[index]?.map((event) => (
                    <CalendarEvent
                      key={`all-day-event-${event.id}`}
                      event={event}
                      isAllDay={true}
                      className="min-h-[48px]"
                    />
                  ))}
                </div>
              ))}
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

          {/* Days grid */}
          <div className="relative flex flex-1 min-w-0 overflow-x-auto sm:overflow-x-visible">
            <div className="flex flex-1 min-w-[680px]">
              {weekDays.map((day, dayIndex) => (
                <div key={`day-${dayIndex}`} className="group flex-1 basis-0 min-w-0">
                  {/* Hour cells with events */}
                  <div className="border-border dark:border-border/15 h-7 border-r group-last:border-r-0"></div>
                  <div className="relative">
                    {hours.map((hour) => (
                      <div
                        key={`${day.name}-${hour}`}
                        className="border-border dark:border-border/15 h-14 border-t border-r group-last:border-r-0"
                      />
                    ))}

                    {/* Render events for this day */}
                    {processedEvents.eventsByDay[dayIndex]?.map((event) => {
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
              ))}
            </div>

            {/* Current time indicator */}
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

export default WeekView;
