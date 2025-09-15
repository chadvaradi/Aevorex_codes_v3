"use client";

import { useState, useEffect, useCallback } from "react";
import CalendarSidebar from "./components/calendar-sidebar";
import CalendarNavbar from "./components/calendar-navbar";
import CalendarMain from "./components/calendar-main";
import { cn } from "@/lib/utils";

type CalendarProps = {
  defaultView?: "day" | "week" | "month";
  heightClassName?: string;
};

type AvailabilitySlot = {
  start: string;
  end: string;
};

type LaunchUiEvent = {
  id: string;
  title: string;
  start: Date;
  end: Date;
  calendarId: string;
  calendarName: string;
  calendarColor: string;
  accountId: string;
  accountName: string;
  accountEmail?: string;
  url?: string;
  subtitle?: string;
  description?: string;
  allDay?: boolean;
  location?: string;
  attendees?: string[];
  badges?: string[];
  urlLabel?: string;
  external?: boolean;
  durationMin?: number;
};

type EventsMeta = {
  accounts: Array<{
    id: string;
    name: string;
    email: string;
    calendars: Array<{
      id: string;
      name: string;
      color: "indigo";
      events: any[];
    }>;
  }>;
};

function startOfNextWeek(base = new Date()) {
  const day = (base.getDay() + 6) % 7; // JS vasárnap=0 → ISO hétfő=0
  const mondayNextWeek = new Date(base);
  mondayNextWeek.setDate(base.getDate() - day + 7); // következő hétfő
  mondayNextWeek.setHours(0, 0, 0, 0);
  return mondayNextWeek;
}

function Calendar({ defaultView = "week", heightClassName }: CalendarProps) {
  const [currentView, setCurrentView] = useState(defaultView);
  const [events, setEvents] = useState<LaunchUiEvent[]>([]);
  const [selectedCalendars, setSelectedCalendars] = useState<Record<string, boolean>>({});
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [isMobileView, setIsMobileView] = useState(false);
  const [eventsMeta] = useState<EventsMeta>({
    accounts: [
      {
        id: "account-consulting",
        name: "Consulting",
        email: "consulting@example.com",
        calendars: [
          {
            id: "calendar-consulting",
            name: "Consulting slots",
            color: "indigo",
            events: [],
          },
        ],
      },
    ],
  });

  const [displayedDate, setDisplayedDate] = useState<Date>(() => startOfNextWeek());
  const currentTime = new Date();

  useEffect(() => {
    const checkIsMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobileView(mobile);
      if (mobile) setSidebarVisible(false);
    };
    checkIsMobile();
    window.addEventListener("resize", checkIsMobile);
    return () => window.removeEventListener("resize", checkIsMobile);
  }, []);

  useEffect(() => {
    let aborted = false;
    async function load() {
      try {
        // Calculate date range for the current view
        const start = new Date(displayedDate);
        const day = (start.getDay() + 6) % 7; // Convert to Monday-based week
        const monday = new Date(start);
        monday.setDate(start.getDate() - day);
        monday.setHours(0, 0, 0, 0);
        
        const sunday = new Date(monday);
        sunday.setDate(monday.getDate() + 6);
        sunday.setHours(23, 59, 59, 999);

        const qs = new URLSearchParams({
          start: monday.toISOString(),
          end: sunday.toISOString(),
        }).toString();

        const res = await fetch(`/api/calendar_consulting/availability?${qs}`, { cache: "no-store" });
        if (!res.ok) throw new Error(`Availability error: ${res.status}`);
        const data = (await res.json()) as {
          slots: AvailabilitySlot[];
          slotDurationMin: number;
          timezone: string;
        };

        const calendlyBase = "https://calendly.com/csanad-varadi/consultation"; // Hardcoded fix
        const mapped: LaunchUiEvent[] = (data.slots || []).map((s, idx) => {
          const start = new Date(s.start);
          const end = new Date(s.end);
          const durationMin =
            data.slotDurationMin ??
            Math.max(1, Math.round((end.getTime() - start.getTime()) / 60000));

          return {
            id: `slot-${start.toISOString()}-${idx}`,
            name: "Consultation",
            title: "Consultation",
            subtitle: `${durationMin} perc • ${data.timezone || "Europe/Budapest"}`,
            description: "Foglalható idősáv. A foglalás a Calendly oldalán fejeződik be.",
            start,
            end,
            allDay: false,
            location: "Online (Google Meet)",
            attendees: [],
            badges: [`${durationMin} perc`, "HU időzóna"],
            calendarId: "calendar-consulting",
            calendarName: "Consulting slots",
            calendarColor: "indigo",
            accountId: "account-consulting",
            accountName: "Consulting",
            url: calendlyBase || undefined,
            urlLabel: "Foglalás megnyitása",
            external: true,
            durationMin,
          };
        });

        if (!aborted) setEvents(mapped);
      } catch (e) {
        console.error(e);
        if (!aborted) setEvents([]);
      }
    }
    load();
    return () => {
      aborted = true;
    };
  }, [displayedDate]);

  const eventsWithUnique = events.map(ev => ({
    ...ev,
    calendarUniqueId: `${ev.accountId}-${ev.calendarId}`,
  }));

  const filteredEvents = eventsWithUnique.filter(
    ev => selectedCalendars[ev.calendarUniqueId] !== false,
  );

  const toggleCalendar = (calendarUniqueId: string) => {
    setSelectedCalendars(prev => ({
      ...prev,
      [calendarUniqueId]: !prev[calendarUniqueId],
    }));
  };

  return (
    <div
      className={cn(
        "glass-3 relative flex w-full overflow-hidden rounded-xl p-1 sm:p-2",
        heightClassName ?? "h-[480px] sm:h-[620px] md:h-[760px] lg:h-[900px]"
      )}
    >
      {/* Sidebar */}
      <div
        className={cn(
          "absolute top-0 bottom-0 left-0 z-10 h-full overflow-hidden transition-all duration-300 ease-in-out md:static md:translate-x-0",
          sidebarVisible
            ? "translate-x-0 p-2 opacity-100 md:w-64 md:p-0"
            : "-translate-x-full opacity-0 md:w-0 md:opacity-0",
        )}
      >
        <CalendarSidebar
          eventsData={eventsMeta}
          selectedCalendars={selectedCalendars}
          onToggleCalendar={toggleCalendar}
          onCloseSidebar={() => setSidebarVisible(false)}
          isMobileView={isMobileView}
        />
      </div>

      {/* Main */}
      <div className="glass-3 flex flex-1 flex-col overflow-hidden rounded-lg shadow-lg shadow-black/5">
        <CalendarNavbar
          currentView={currentView}
          onViewChange={(view) => setCurrentView(view as typeof defaultView)}
          date={displayedDate}
          onDateChange={setDisplayedDate}
          onToggleSidebar={() => setSidebarVisible(prev => !prev)}
          sidebarVisible={sidebarVisible}
        />
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
