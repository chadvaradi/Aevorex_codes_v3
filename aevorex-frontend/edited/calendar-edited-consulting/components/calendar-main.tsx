import DayView from "./views/day-view";
import WeekView from "./views/week-view";
import MonthView from "./views/month-view";

/**
 * CalendarMain Component
 *
 * Main content area of the calendar that displays events based on the selected view.
 * Supports day, week, and month views.
 */
interface CalendarMainProps {
  view: string;
  date: Date; // Required date prop
  events: any[]; // Events are now passed as props
  currentTime?: Date; // Current time for time indicator
}

function CalendarMain({ view, date, events, currentTime }: CalendarMainProps) {
  // Render the appropriate view based on the selected view type
  const renderView = () => {
    switch (view) {
      case "day":
        return (
          <DayView events={events} date={date} currentTime={currentTime} />
        );
      case "week":
        return (
          <WeekView events={events} date={date} currentTime={currentTime} />
        );
      case "month":
        return (
          <MonthView events={events} date={date} currentTime={currentTime} />
        );
      default:
        return (
          <WeekView events={events} date={date} currentTime={currentTime} />
        );
    }
  };

  return <div className="h-full w-full">{renderView()}</div>;
}

export default CalendarMain;
