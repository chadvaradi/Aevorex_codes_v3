"use client";

import { useState, useEffect, useCallback } from "react";
import CalendarSidebar from "./components/calendar-sidebar";
import CalendarNavbar from "./components/calendar-navbar";
import CalendarMain from "./components/calendar-main";
import eventsData from "./data/events.json";
import { cn } from "@/lib/utils";

/**
 * Calendar App Component
 *
 * A responsive calendar application with multiple views (day, week, month)
 * and a sidebar for navigation and filtering.
 */

type CalendarProps = {
  defaultView?: "day" | "week" | "month";
};

function Calendar({ defaultView = "week" }: CalendarProps) {
  // State to track the current view (day, week, month)
  const [currentView, setCurrentView] = useState(defaultView);
  // State to store processed events
  const [events, setEvents] = useState<any[]>([]);
  // State to track selected calendars
  const [selectedCalendars, setSelectedCalendars] = useState<
    Record<string, boolean>
  >({});
  // State to track sidebar visibility
  const [sidebarVisible, setSidebarVisible] = useState(true);
  // State to track if it's mobile view
  const [isMobileView, setIsMobileView] = useState(false);

  // Reference date - fixed to January 17, 2024
  // We use January 17 (Monday) to ensure we see the start of the week
  const currentDate = new Date(2024, 0, 17);

  // State to track the displayed date (which changes when navigating)
  const [displayedDate, setDisplayedDate] = useState(new Date(currentDate));

  // Fixed current time - 9:30 AM
  const currentTime = new Date(2024, 0, 17);
  currentTime.setHours(9, 30, 0);

  // Add effect to handle window resize for responsive behavior
  useEffect(() => {
    // Check initial window width
    const checkIsMobile = () => {
      setIsMobileView(window.innerWidth < 768);
      // Hide sidebar by default on mobile
      if (window.innerWidth < 768) {
        setSidebarVisible(false);
      }
    };

    // Set initial state
    checkIsMobile();

    // Add resize listener
    window.addEventListener("resize", checkIsMobile);

    // Cleanup
    return () => window.removeEventListener("resize", checkIsMobile);
  }, []);

  // Process events from the JSON data
  useEffect(() => {
    // For now, we'll just use all events from all accounts and calendars
    const allEvents: any[] = [];
    const calendarSelections: Record<string, boolean> = {};

    eventsData.accounts.forEach((account) => {
      account.calendars.forEach((calendar) => {
        // Create a unique ID for each calendar
        const calendarUniqueId = `${account.id}-${calendar.id}`;
        // Set all calendars as selected by default
        calendarSelections[calendarUniqueId] = true;

        // Add calendar info to each event
        const eventsWithMeta = calendar.events.map((event) => ({
          ...event,
          calendarId: calendar.id,
          calendarName: calendar.name,
          calendarColor: calendar.color,
          accountId: account.id,
          accountName: account.name,
          accountEmail: account.email,
          calendarUniqueId,
        }));

        allEvents.push(...eventsWithMeta);
      });
    });

    setEvents(allEvents);
    setSelectedCalendars(calendarSelections);
  }, []);

  // Filter events based on selected calendars
  const filteredEvents = events.filter(
    (event) => selectedCalendars[event.calendarUniqueId],
  );

  // Handle calendar selection toggle
  const toggleCalendar = (calendarUniqueId: string) => {
    setSelectedCalendars((prev) => ({
      ...prev,
      [calendarUniqueId]: !prev[calendarUniqueId],
    }));
  };

  // Handle date change
  const handleDateChange = (newDate: Date) => {
    setDisplayedDate(newDate);
  };

  // Handle sidebar toggle
  const toggleSidebar = useCallback(() => {
    setSidebarVisible((prev) => !prev);
  }, []);

  return (
    <div className="glass-3 relative flex h-[900px] w-full overflow-hidden rounded-xl p-2">
      {/* Sidebar - contains account information, calendars, etc. */}
      <div
        className={cn(
          "absolute top-0 bottom-0 left-0 z-10 h-full overflow-hidden transition-all duration-300 ease-in-out md:static md:translate-x-0",
          sidebarVisible
            ? "translate-x-0 p-2 opacity-100 md:w-64 md:p-0"
            : "-translate-x-full opacity-0 md:w-0 md:opacity-0",
        )}
      >
        <CalendarSidebar
          eventsData={eventsData}
          selectedCalendars={selectedCalendars}
          onToggleCalendar={toggleCalendar}
          onCloseSidebar={toggleSidebar}
          isMobileView={isMobileView}
        />
      </div>

      {/* Main content area */}
      <div className="glass-3 flex flex-1 flex-col overflow-hidden rounded-lg shadow-lg shadow-black/5">
        {/* Navbar - contains view selector and other controls */}
        <CalendarNavbar
          currentView={currentView}
          onViewChange={(view) => setCurrentView(view as typeof defaultView)}
          date={displayedDate}
          onDateChange={handleDateChange}
          onToggleSidebar={toggleSidebar}
          sidebarVisible={sidebarVisible}
        />

        {/* Calendar main content - displays events based on selected view */}
        <div className="flex-1 overflow-auto">
          <CalendarMain
            view={currentView}
            date={displayedDate}
            events={filteredEvents}
            currentTime={currentTime}
          />
        </div>
      </div>
    </div>
  );
}

export default Calendar;
