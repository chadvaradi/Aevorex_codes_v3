"use client";

import { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { ArrowRightIcon } from "lucide-react";

import { Button, type ButtonProps } from "@/launch-ui-pro-2.3.3/ui/button";
import { Section } from "@/launch-ui-pro-2.3.3/ui/section";
import Glow from "@/launch-ui-pro-2.3.3/ui/glow";
import { Badge } from "@/launch-ui-pro-2.3.3/ui/badge";
import LinkedIn from "@/launch-ui-pro-2.3.3/logos/linkedin";
import Screenshot from "@/launch-ui-pro-2.3.3/ui/screenshot";

interface HeroButtonProps {
  href: string;
  text: string;
  variant?: ButtonProps["variant"];
  icon?: ReactNode;
  iconRight?: ReactNode;
}

interface HeroProps {
  title?: string;
  description?: string;
  badge?: ReactNode | false;
  buttons?: HeroButtonProps[] | false;
  mockup?: ReactNode | false;
  className?: string;
}

export default function Hero({
  title = "WHERE FINANCIAL DATA MEETS INTELLIGENCE",
  description = "Faster financial research, powered by reliable data and AI.",
  badge = (
    <Badge variant="outline" className="animate-appear">
      <span className="text-muted-foreground">
        Join the early access list
      </span>
      <a href="https://www.launchuicomponents.com/" className="flex items-center gap-1">
        Discover more
        <ArrowRightIcon className="size-3" />
      </a>
    </Badge>
  ),
  buttons = [
    {
      href: "https://www.launchuicomponents.com/",
      text: "Try for free",
      variant: "default",
    },
    {
      href: "https://www.linkedin.com/company/aevorex/about/",
      text: "LinkedIn",
      variant: "glow",
      icon: <LinkedIn className="mr-2 size-4" />,
    },
  ],
  className,
  mockup = (
    <Screenshot
      srcLight="/mobile-app-light.png"
      srcDark="/mobile-app-dark.png"
      alt="Aevorex preview"
      width={900}
      height={1840}
      className="relative z-10"
    />
  ),
}: HeroProps) {
  return (
    <Section className={cn("w-full overflow-hidden", className)}>
      <div className="max-w-container mx-auto flex flex-col items-center gap-12 sm:gap-24 md:flex-row">
        <div className="flex flex-col items-center justify-center gap-6 pb-0 text-center md:items-start md:gap-8 md:pb-8 md:text-left lg:gap-12 lg:pb-16">
          {badge !== false && badge}
          <h1 className="animate-appear from-foreground to-foreground dark:to-muted-foreground inline-block bg-linear-to-r bg-clip-text text-4xl leading-[1.2em] font-semibold text-transparent drop-shadow-2xl sm:text-5xl sm:leading-tight lg:text-7xl lg:leading-[1.2em]">
            {title}
          </h1>
          <p className="text-md animate-appear text-muted-foreground max-w-[550px] font-medium opacity-0 delay-100 lg:text-xl">
            {description}
          </p>
          {buttons !== false && buttons.length > 0 && (
            <div className="animate-appear relative z-10 flex justify-center gap-4 opacity-0 delay-300">
              {buttons.map((button, index) => (
                <Button
                  key={index}
                  variant={button.variant || "default"}
                  size="lg"
                  asChild
                >
                  <a href={button.href}>
                    {button.icon}
                    {button.text}
                    {button.iconRight}
                  </a>
                </Button>
              ))}
            </div>
          )}
        </div>
        {mockup !== false && (
          <div className="relative">
            <div className="animate-appear max-w-[320px] opacity-0 delay-700 md:max-w-[720px]">
              {mockup}
              <Glow
                variant="center"
                className="animate-appear-zoom opacity-0 delay-1000"
              />
            </div>
          </div>
        )}
      </div>
    </Section>
  );
}
