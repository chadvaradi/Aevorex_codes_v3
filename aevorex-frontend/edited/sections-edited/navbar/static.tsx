import { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Menu } from "lucide-react";

import { Button, type ButtonProps } from "@/launch-ui-pro-2.3.3/ui/button";
import {
  Navbar as NavbarComponent,
  NavbarLeft,
  NavbarRight,
} from "@/launch-ui-pro-2.3.3/ui/navbar";
import { Sheet, SheetContent, SheetTrigger } from "@/launch-ui-pro-2.3.3/ui/sheet";
import Aevorex from "@/launch-ui-pro-2.3.3/logos/aevorex";

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
  logo = <Aevorex />,
  name = "Aevorex",
  homeUrl = "https://aevorex.com/",
  mobileLinks = [
    { text: "Home", href: "https://aevorex.com/" },
    { text: "Features", href: "https://aevorex.com/" },
    { text: "Docs", href: "https://aevorex.com/" },
  ],
  actions = [
    { text: "Log in", href: "https://aevorex.com/", isButton: false },
    {
      text: "Get Access",
      href: "https://aevorex.com/",
      isButton: true,
      variant: "default",
    },
  ],
  className,
}: NavbarProps) {
  return (
    <header className={cn("w-full px-4", className)}>
      <div className="max-w-container mx-auto">
        <NavbarComponent>
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
            <Sheet>
              <SheetTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="shrink-0 md:hidden"
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
          </NavbarRight>
        </NavbarComponent>
      </div>
    </header>
  );
}
