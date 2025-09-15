import { Button } from "../../../ui/button";
import LaunchUI from "../../../logos/launch-ui";
import { TeamSwitcher } from "../../../ui/team-switcher";
import { Checkbox } from "../../../ui/checkbox";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * CalendarSidebar Component
 *
 * Displays account information, calendar lists, and filtering options.
 */
interface CalendarSidebarProps {
  eventsData: {
    accounts: Array<{
      id: string;
      name: string;
      email: string;
      calendars: Array<{
        id: string;
        name: string;
        color: string;
        events: any[];
      }>;
    }>;
  };
  selectedCalendars: Record<string, boolean>;
  onToggleCalendar: (calendarUniqueId: string) => void;
  onCloseSidebar?: () => void;
  isMobileView?: boolean;
}

function CalendarSidebar({
  eventsData,
  selectedCalendars,
  onToggleCalendar,
  onCloseSidebar,
  isMobileView,
}: CalendarSidebarProps) {
  // Helper function to get the color class
  const getColorClass = (color: string) => {
    const colorMap: Record<string, string> = {
      blue: " data-[state=checked]:border-blue-500 data-[state=checked]:bg-blue-500 dark:data-[state=checked]:bg-blue-500",
      indigo:
        " data-[state=checked]:border-indigo-500 data-[state=checked]:bg-indigo-500 dark:data-[state=checked]:bg-indigo-500",
      purple:
        " data-[state=checked]:border-purple-500 data-[state=checked]:bg-purple-500 dark:data-[state=checked]:bg-purple-500",
      pink: " data-[state=checked]:border-pink-500 data-[state=checked]:bg-pink-500 dark:data-[state=checked]:bg-pink-500",
      red: " data-[state=checked]:border-red-500 data-[state=checked]:bg-red-500 dark:data-[state=checked]:bg-red-500",
      orange:
        " data-[state=checked]:border-orange-500 data-[state=checked]:bg-orange-500 dark:data-[state=checked]:bg-orange-500",
      amber:
        " data-[state=checked]:border-amber-500 data-[state=checked]:bg-amber-500 dark:data-[state=checked]:bg-amber-500",
      yellow:
        " data-[state=checked]:border-yellow-500 data-[state=checked]:bg-yellow-500 dark:data-[state=checked]:bg-yellow-500",
      lime: " data-[state=checked]:border-lime-500 data-[state=checked]:bg-lime-500 dark:data-[state=checked]:bg-lime-500",
      green:
        " data-[state=checked]:border-green-500 data-[state=checked]:bg-green-500 dark:data-[state=checked]:bg-green-500",
      emerald:
        " data-[state=checked]:border-emerald-500 data-[state=checked]:bg-emerald-500 dark:data-[state=checked]:bg-emerald-500",
      teal: " data-[state=checked]:border-teal-500 data-[state=checked]:bg-teal-500 dark:data-[state=checked]:bg-teal-500",
      cyan: " data-[state=checked]:border-cyan-500 data-[state=checked]:bg-cyan-500 dark:data-[state=checked]:bg-cyan-500",
      sky: " data-[state=checked]:border-sky-500 data-[state=checked]:bg-sky-500 dark:data-[state=checked]:bg-sky-500",
      gray: " data-[state=checked]:border-gray-500 data-[state=checked]:bg-gray-500 dark:data-[state=checked]:bg-gray-500",
      rose: " data-[state=checked]:border-rose-500 data-[state=checked]:bg-rose-500 dark:data-[state=checked]:bg-rose-500",
    };

    return (
      colorMap[color] || "border-gray-500 data-[state=checked]:bg-gray-500"
    );
  };

  return (
    <div
      className={cn(
        "relative flex h-full flex-col p-3 pr-5 text-left",
        isMobileView &&
          "bg-muted border-border dark:border-border/20 rounded-lg border shadow-2xl",
      )}
    >
      <div className="flex items-center gap-4">
        <TeamSwitcher
          teams={[
            {
              name: "Launch UI",
              logo: LaunchUI,
              plan: "Enterprise",
            },
          ]}
        />
        {isMobileView && onCloseSidebar && (
          <Button
            variant="ghost"
            size="icon"
            className="shrink-0 md:hidden"
            onClick={onCloseSidebar}
            aria-label="Close sidebar"
          >
            <X className="text-muted-foreground h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Calendar lists */}
      <div className="mt-6 flex flex-1 flex-col gap-8 px-2">
        {/* Dynamic calendar lists grouped by account */}
        {eventsData.accounts.map((account) => (
          <div key={account.id} className="flex flex-col gap-2">
            {/* Account name as subheading */}
            <h3 className="text-muted-foreground text-xs font-medium">
              {account.name}
            </h3>

            {/* Calendars for this account */}
            {account.calendars.map((calendar) => {
              const calendarUniqueId = `${account.id}-${calendar.id}`;
              return (
                <div
                  key={calendarUniqueId}
                  className="flex items-center space-x-2"
                >
                  <Checkbox
                    id={calendarUniqueId}
                    checked={selectedCalendars[calendarUniqueId]}
                    onCheckedChange={() => onToggleCalendar(calendarUniqueId)}
                    className={getColorClass(calendar.color)}
                  />
                  <label
                    htmlFor={calendarUniqueId}
                    className="cursor-pointer text-sm"
                  >
                    {calendar.name}
                  </label>
                </div>
              );
            })}
          </div>
        ))}
      </div>

      {/* Additional controls */}
      <div className="mt-auto p-2">
        <Button variant="glow" className="w-full">
          Create Event
        </Button>
      </div>
    </div>
  );
}

export default CalendarSidebar;
