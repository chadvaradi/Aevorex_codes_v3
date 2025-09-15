import { ReactNode } from "react";
import { cn } from "@/lib/utils";

import { Section } from "@/launch-ui-pro-2.3.3/ui/section";
import RadarIllustration from "@/edited/illustrations-edited/radar";

interface FeatureIllustrationTopProps {
  title?: string;
  description?: string;
  visual?: ReactNode;
  className?: string;
}

export default function FeatureIllustrationTop({
  title = "Research a stock in seconds, not hours.",
  description = "AI-powered financial analysis designed for investors who move fast.",
  visual = <RadarIllustration />,
  className,
}: FeatureIllustrationTopProps) {
  return (
    <Section className={cn("relative w-full overflow-hidden", className)}>
      <div className="relative">
        <div className="max-w-container mx-auto flex flex-col gap-8 sm:gap-24">
          <div className="overflow-visable w-full">{visual}</div>
          <div className="flex flex-col items-center gap-4 text-center sm:gap-8">
            <h1 className="from-foreground to-foreground dark:to-muted-foreground inline-block max-w-[920px] bg-linear-to-r bg-clip-text text-3xl font-semibold text-balance text-transparent drop-shadow-2xl sm:text-5xl sm:leading-tight md:text-7xl md:leading-tight">
              {title}
            </h1>
            <p className="text-md text-muted-foreground max-w-[620px] font-medium text-balance sm:text-xl">
              {description}
            </p>
          </div>
        </div>
      </div>
    </Section>
  );
}
