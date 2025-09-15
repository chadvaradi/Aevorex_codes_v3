import { ReactNode } from "react";

import {
  Tile,
  TileVisual,
  TileTitle,
  TileDescription,
  TileContent,
  TileLink,
} from "@/launch-ui-pro-2.3.3/ui/tile";
import { Section } from "@/launch-ui-pro-2.3.3/ui/section";
import GlobeIllustration from "@/edited/illustrations-edited/globe";
import GeminiCliIllustration from "@/edited/illustrations-edited/gemini-cli";
import MockupMobileIllustration from "@/edited/illustrations-edited/mockup-mobile";
import PipelineIllustration from "@/edited/illustrations-edited/pipeline";
import CodeEditorIllustration from "@/edited/illustrations-edited/code-editor";
import RadarSmallIllustration from "@/edited/illustrations-edited/radar-small";

interface TileProps {
  title: string;
  description: ReactNode;
  visual: ReactNode;
  size?: string;
  icon?: ReactNode;
}

interface BentoGridProps {
  title?: string;
  description?: string;
  tiles?: TileProps[] | false;
  className?: string;
}

export default function BentoGrid({
  title = "Meet the next era of financial research",
  description = "Combining real-time market data, company filings, and alternative sources with AI — so you can make faster, sharper investment decisions.",
  tiles = [
    {
      title: "Always with you",
      description: (
        <p>
          Dashboards and AI tools that are fast and practical on mobile — research anywhere, anytime.
        </p>
      ),
      visual: (
        <div className="min-h-[300px] w-full py-12">
          <MockupMobileIllustration />
        </div>
      ),
      size: "col-span-12 md:col-span-6 lg:col-span-5",
    },
    {
      title: "Reliable data sources",
      description: (
        <p className="max-w-[520px]">
          From EODHD market data to FRED economic indicators and Euribor rates — all integrated into one AI-powered research hub. Exportable and audit-friendly.
        </p>
      ),
      visual: (
        <div className="min-h-[160px] w-full grow items-center self-center">
          <PipelineIllustration />
        </div>
      ),
      size: "col-span-12 md:col-span-6 lg:col-span-7",
    },
    {
      title: "Your insights, your edge",
      description: (
        <p className="max-w-[460px]">
          No black-box outputs. Transparent analysis you can customize and adapt to your workflow.
        </p>
      ),
      visual: (
        <div className="min-h-[240px] w-full grow items-center self-center px-4 lg:px-12">
          <CodeEditorIllustration />
        </div>
      ),
      size: "col-span-12 md:col-span-6 lg:col-span-7",
    },
    {
      title: "Global market coverage",
      description:
        "Track stocks, sectors, and economies worldwide. From Wall Street to emerging markets.",
      visual: (
        <div className="-mb-[96px] sm:-mb-[186px] md:-mx-32">
          <GlobeIllustration className="[&_svg]:h-[100%] [&_svg]:w-[100%]" />
        </div>
      ),
      size: "col-span-12 md:col-span-6 lg:col-span-5",
    },
    {
      title: "On your radar",
      description: (
        <>
          <p>
            Watchlists powered by AI keep the companies you care about—like Apple and NVIDIA—on your radar.
          </p>
          <p>Never miss the signal again.</p>
        </>
      ),
      visual: (
        <div className="w-full sm:p-4 md:p-8">
          <GeminiCliIllustration />
        </div>
      ),
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
        <div className="mt-12 -mb-48 flex w-full grow items-center justify-center self-center">
          <RadarSmallIllustration className="max-w-[480px]" />
        </div>
      ),
      size: "col-span-12 md:col-span-6 lg:col-span-7",
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
            {tiles.map((tile, index) => (
              <Tile key={index} className={tile.size}>
                <TileLink />
                <TileContent>
                  {tile.icon && tile.icon}
                  <TileTitle>{tile.title}</TileTitle>
                  <TileDescription>{tile.description}</TileDescription>
                </TileContent>
                <TileVisual>{tile.visual}</TileVisual>
              </Tile>
            ))}
          </div>
        )}
      </div>
    </Section>
  );
}
