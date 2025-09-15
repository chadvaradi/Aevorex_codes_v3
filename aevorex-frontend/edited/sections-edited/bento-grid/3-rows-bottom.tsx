import { ReactNode } from "react";
import { MousePointerClick, Shield, TextCursor, Wrench } from "lucide-react";

import {
  Tile,
  TileVisual,
  TileTitle,
  TileDescription,
  TileContent,
  TileLink,
} from "@/launch-ui-pro-2.3.3/ui/tile";
import { Section } from "@/launch-ui-pro-2.3.3/ui/section";
import RippleIllustration from "@/edited/illustrations-edited/ripple";
import ChatIllustration from "@/edited/illustrations-edited/chat";
import MockupBrowserIllustration from "@/edited/illustrations-edited/mockup-browser";
import MockupResponsiveBottomIllustration from "@/edited/illustrations-edited/mockup-responsive-bottom";
import RadarSmallIllustration from "@/edited/illustrations-edited/radar-small";

interface TileProps {
  title: string;
  description: ReactNode;
  visual: ReactNode;
  icon?: ReactNode;
  size?: string;
  contentClassName?: string;
}

interface BentoGridProps {
  title?: string;
  description?: string;
  tiles?: TileProps[] | false;
  className?: string;
}

export default function BentoGrid({
  title = "Meet the next era of financial research",
  description = "Combining real-time market data, company filings, and alternative sources with AI — so beginners can make faster, smarter decisions.",
  tiles = [
    {
      title: "Your insights, your edge",
      description: (
        <>
          <p className="max-w-[320px] lg:max-w-[460px]">
            No black-box outputs. Transparent analysis you can customize and adapt to your workflow.
          </p>
          <p>Never worry about hidden algorithms or locked-in solutions.</p>
        </>
      ),
      visual: (
        <div className="min-h-[240px] grow basis-0 sm:p-4 md:min-h-[320px] md:py-12 lg:min-h-[360px]">
          <MockupBrowserIllustration />
        </div>
      ),
      icon: <Wrench className="text-muted-foreground size-8 stroke-1" />,
      size: "col-span-12 md:flex-row",
      contentClassName: "grow basis-0 md:justify-end",
    },
    {
      title: "Reliable data sources",
      description: (
        <>
          <p>
            From EODHD market data to FRED economic indicators and Euribor rates — all integrated into one AI-powered research hub.
          </p>
          <p>Exportable and audit-friendly data.</p>
        </>
      ),
      visual: (
        <div className="w-full sm:p-4 md:p-8">
          <ChatIllustration />
        </div>
      ),
      icon: <TextCursor className="text-muted-foreground size-8 stroke-1" />,
      size: "col-span-12 md:col-span-6 lg:col-span-5",
    },
    {
      title: "Faster financial research",
      description: (
        <>
          <p className="max-w-[460px]">
            Combine multiple data sources with AI analysis to deliver actionable business intelligence.
          </p>
          <p>Transform scattered information into strategic decisions.</p>
        </>
      ),
      visual: (
        <div className="-mx-32 pt-8">
          <RippleIllustration />
        </div>
      ),
      icon: (
        <MousePointerClick className="text-muted-foreground size-8 stroke-1" />
      ),
      size: "col-span-12 md:col-span-6 lg:col-span-7",
    },
    {
      title: "Global market coverage",
      description:
        "Track stocks, sectors, and economies worldwide. From Wall Street to emerging markets.",
      visual: (
        <div className="h-full min-h-[240px] grow sm:p-4 md:min-h-[320px] lg:px-12">
          <MockupResponsiveBottomIllustration />
        </div>
      ),
      icon: <Wrench className="text-muted-foreground size-8 stroke-1" />,
      size: "col-span-12 md:col-span-6 lg:col-span-6",
    },
    {
      title: "On your radar",
      description: (
        <p className="max-w-[460px]">
          Watchlists powered by AI keep the companies you care about—like Apple and NVIDIA—on your radar so you never miss the signal.
        </p>
      ),
      visual: (
        <div className="relative min-h-[240px]">
          <RadarSmallIllustration className="absolute top-1/2 left-1/2 -mt-24 h-[512px] w-[512px] -translate-x-1/2 -translate-y-1/2" />
        </div>
      ),
      icon: <Shield className="text-muted-foreground size-8 stroke-1" />,
      size: "col-span-12 md:col-span-6 lg:col-span-6",
    },
  ],
  className,
}: BentoGridProps) {
  return (
    <Section className={className}>
      <div className="max-w-container mx-auto flex flex-col items-center gap-6 sm:gap-12">
        <h2 className="text-center text-3xl font-semibold text-balance sm:text-5xl">
          {title}
        </h2>
        <p className="text-md text-muted-foreground max-w-[840px] text-center font-medium text-balance sm:text-xl">
          {description}
        </p>
        {tiles !== false && tiles.length > 0 && (
          <div className="grid grid-cols-12 gap-4">
            {tiles.map((tile, index) => {
              // Determine the right order of elements based on the index/position
              if (index === 0) {
                return (
                  <Tile key={index} className={tile.size}>
                    <TileLink />
                    <TileContent className={tile.contentClassName}>
                      {tile.icon}
                      <TileTitle>{tile.title}</TileTitle>
                      <TileDescription>{tile.description}</TileDescription>
                    </TileContent>
                    <TileVisual>{tile.visual}</TileVisual>
                  </Tile>
                );
              } else if (index === 3) {
                return (
                  <Tile key={index} className={tile.size}>
                    <TileVisual>{tile.visual}</TileVisual>
                    <TileContent>
                      {tile.icon}
                      <TileTitle>{tile.title}</TileTitle>
                      <TileDescription>{tile.description}</TileDescription>
                    </TileContent>
                  </Tile>
                );
              } else {
                return (
                  <Tile key={index} className={tile.size}>
                    <TileLink />
                    <TileVisual>{tile.visual}</TileVisual>
                    <TileContent>
                      {tile.icon}
                      <TileTitle>{tile.title}</TileTitle>
                      <TileDescription>{tile.description}</TileDescription>
                    </TileContent>
                  </Tile>
                );
              }
            })}
          </div>
        )}
      </div>
    </Section>
  );
}
