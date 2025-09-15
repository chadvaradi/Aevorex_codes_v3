"use client";

import { ReactNode, useState } from "react";
import { cn } from "@/lib/utils";
import { Menu } from "lucide-react";

import { Button, type ButtonProps } from "@/launch-ui-pro-2.3.3/ui/button";
import {
  Navbar as NavbarComponent,
  NavbarLeft,
  NavbarRight,
} from "@/launch-ui-pro-2.3.3/ui/navbar";
import { Sheet, SheetContent, SheetTrigger } from "@/launch-ui-pro-2.3.3/ui/sheet";
import LaunchUI from "@/launch-ui-pro-2.3.3/logos/launch-ui";

interface NavbarLink {
  text: string;
  href: string;
}

interface NavbarActionProps {
  text: string;
  href: string;
  variant?: ButtonProps["variant"];
  icon?: ReactNode;
  iconRight?: ReactNode;
  isButton?: boolean;
}

interface NavbarProps {
  logo?: ReactNode;
  name?: string;
  homeUrl?: string;
  mobileLinks?: NavbarLink[];
  actions?: NavbarActionProps[];
  className?: string;
}

export default function Navbar({
  logo = <LaunchUI />,
  name = "Launch UI",
  homeUrl = "#",
  mobileLinks = [
    { text: "Getting Started", href: "#" },
    { text: "Components", href: "#" },
    { text: "Documentation", href: "#" },
  ],
  actions = [
    {
      text: "Sign in",
      href: "#",
      isButton: false,
    },
    {
      text: "Get Started",
      href: "#",
      isButton: true,
      variant: "default",
    },
  ],
  className,
}: NavbarProps) {
  const [open, setOpen] = useState(false);

  return (
    <header className={cn("sticky top-0 z-50 w-full p-2", className)} data-nav>
      <div className="max-w-container mx-auto">
        <NavbarComponent className="bg-background/30 border-border dark:border-border/15 rounded-2xl border p-2 backdrop-blur-lg">
          <NavbarLeft>
            <a
              href={homeUrl}
              className="flex items-center gap-2 text-xl font-bold"
            >
              {logo}
              {name}
            </a>
          </NavbarLeft>
          <NavbarRight>
            {actions.map((action, index) =>
              action.isButton ? (
                <Button
                  key={index}
                  variant={action.variant || "default"}
                  asChild
                >
                  <a href={action.href}>
                    {action.icon}
                    {action.text}
                    {action.iconRight}
                  </a>
                </Button>
              ) : (
                <a
                  key={index}
                  href={action.href}
                  className="hidden text-sm md:block"
                >
                  {action.text}
                </a>
              ),
            )}
            
            {/* Desktop hamburger menu */}
            <div className="hidden md:block">
              <Sheet open={open} onOpenChange={setOpen}>
                <SheetTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="shrink-0"
                  >
                    <Menu className="size-5" />
                    <span className="sr-only">Toggle navigation menu</span>
                  </Button>
                </SheetTrigger>
                <SheetContent side="right">
                  <nav className="grid gap-6 text-lg font-medium">
                    <a
                      href={homeUrl}
                      className="flex items-center gap-2 text-xl font-bold"
                    >
                      <span>{name}</span>
                    </a>
                    {mobileLinks.map((link, index) => (
                      <a
                        key={index}
                        href={link.href}
                        className="text-muted-foreground hover:text-foreground"
                      >
                        {link.text}
                      </a>
                    ))}
                  </nav>
                </SheetContent>
              </Sheet>
            </div>

            {/* Mobile language switcher */}
            <div className="flex md:hidden items-center gap-3">
              {actions
                .filter(action => !action.isButton && action.text !== "Book a consultation") // Csak a nyelvváltó linkeket
                .map((action, index) => (
                  <a
                    key={index}
                    href={action.href}
                    className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {action.text}
                  </a>
                ))}
            </div>
          </NavbarRight>
        </NavbarComponent>
      </div>
    </header>
  );
}