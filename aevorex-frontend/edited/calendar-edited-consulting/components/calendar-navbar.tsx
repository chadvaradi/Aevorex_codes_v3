import { Button } from "@/launch-ui-pro-2.3.3/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/launch-ui-pro-2.3.3/ui/select";
import { ChevronLeft, ChevronRight, PanelLeftIcon } from "lucide-react";

/**
 * CalendarNavbar Component
 *
 * Top navigation bar for the calendar app with view selector and other controls.
 */
interface CalendarNavbarProps {
  currentView: string;
  onViewChange: (view: string) => void;
  date: Date; // Required date prop
  onDateChange: (date: Date) => void; // Add handler for date changes
  onToggleSidebar?: () => void; // New prop for toggling sidebar
  sidebarVisible?: boolean; // New prop to track sidebar state
}

function CalendarNavbar({
  currentView,
  onViewChange,
  date,
  onDateChange,
  onToggleSidebar,
  sidebarVisible,
}: CalendarNavbarProps) {
  // Format the month and year
  const month = date.toLocaleString("default", { month: "long" });
  const year = date.getFullYear();

  // Handler for previous button (day, week, or month depending on view)
  const handlePrevious = () => {
    const newDate = new Date(date);
    if (currentView === "day") {
      // Move back one day
      newDate.setDate(date.getDate() - 1);
    } else if (currentView === "month") {
      // Move back one month
      newDate.setMonth(date.getMonth() - 1);
    } else {
      // Move back one week
      newDate.setDate(date.getDate() - 7);
    }
    onDateChange(newDate);
  };

  // Handler for next button (day, week, or month depending on view)
  const handleNext = () => {
    const newDate = new Date(date);
    if (currentView === "day") {
      // Move forward one day
      newDate.setDate(date.getDate() + 1);
    } else if (currentView === "month") {
      // Move forward one month
      newDate.setMonth(date.getMonth() + 1);
    } else {
      // Move forward one week
      newDate.setDate(date.getDate() + 7);
    }
    onDateChange(newDate);
  };

  // Handler for today button - returns to the reference date (Jan 17, 2024)
  const handleToday = () => {
    const now = new Date();
    // „stabil” nap-közepi időpont – elkerüli a DST/midnight anomáliákat
    now.setHours(12, 0, 0, 0);
    onDateChange(now);
  };

  // Get appropriate aria-label based on current view
  const getPreviousAriaLabel = () => {
    if (currentView === "day") return "Previous day";
    if (currentView === "month") return "Previous month";
    return "Previous week";
  };

  // Get appropriate aria-label based on current view
  const getNextAriaLabel = () => {
    if (currentView === "day") return "Next day";
    if (currentView === "month") return "Next month";
    return "Next week";
  };

  return (
    <div className="flex h-14 items-center justify-between pr-2.5 pl-4 min-w-0 overflow-x-auto sm:overflow-x-visible">
      <div className="flex items-center gap-2 flex-shrink-0">
        {onToggleSidebar && (
          <Button
            variant="ghost"
            size="icon"
            className="mr-1 h-8 w-8"
            onClick={onToggleSidebar}
            aria-label={sidebarVisible ? "Hide sidebar" : "Show sidebar"}
          >
            <PanelLeftIcon className="text-muted-foreground h-4 w-4" />
          </Button>
        )}
        <h1>
          <span className="text-lg font-bold">{month}</span>{" "}
          <span className="text-muted-foreground text-lg">{year}</span>
        </h1>
      </div>

      {/* View selector */}
      <div className="flex items-center gap-2.5 flex-shrink-0">
        <Select value={currentView} onValueChange={onViewChange}>
          <SelectTrigger className="border-border dark:border-border/20 hover:bg-accent h-9 w-[120px] bg-transparent">
            <SelectValue placeholder="View" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="day">Day</SelectItem>
            <SelectItem value="week">Week</SelectItem>
            <SelectItem value="month">Month</SelectItem>
          </SelectContent>
        </Select>
        <div className="border-border dark:border-border/20 flex h-9 items-center gap-0.5 rounded-lg border p-1">
          <Button
            variant="ghost"
            size="icon"
            aria-label={getPreviousAriaLabel()}
            className="h-7 w-7"
            onClick={handlePrevious}
          >
            <ChevronLeft className="text-muted-foreground size-3" />
          </Button>
          <Button variant="ghost" className="h-7" onClick={handleToday}>
            Today
          </Button>
          <Button
            variant="ghost"
            size="icon"
            aria-label={getNextAriaLabel()}
            className="h-7 w-7"
            onClick={handleNext}
          >
            <ChevronRight className="text-muted-foreground size-3" />
          </Button>
        </div>
      </div>
    </div>
  );
}

export default CalendarNavbar;
