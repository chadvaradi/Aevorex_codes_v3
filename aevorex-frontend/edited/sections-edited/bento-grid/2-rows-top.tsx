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
import PipelineIllustration from "@/edited/illustrations-edited/pipeline";
import CodeEditorIllustration from "@/edited/illustrations-edited/code-editor";
import MockupMobileIllustration from "@/edited/illustrations-edited/mockup-mobile";
import TilesIllustration from "@/edited/illustrations-edited/tiles";

interface TileProps {
  title: string;
  description: ReactNode;
  visual: ReactNode;
  size?: string;
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
      title: "Reliable data sources",
      description: (
        <p className="max-w-[460px]">
          From EODHD market data to FRED economic indicators and Euribor rates — all integrated into one AI-powered research hub. Exportable and audit-friendly.
        </p>
      ),
      visual: (
        <div className="min-h-[160px] grow items-center self-center">
          <PipelineIllustration />
        </div>
      ),
      size: "col-span-12 md:col-span-5",
    },
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
        <div className="min-h-[240px] w-full grow items-center self-center p-4 lg:px-12">
          <CodeEditorIllustration />
        </div>
      ),
      size: "col-span-12 md:col-span-7",
    },
    {
      title: "Always with you",
      description: (
        <p>
          Dashboards and AI tools that are fast and practical on mobile — research anywhere.
        </p>
      ),
      visual: (
        <div className="min-h-[300px] w-full py-12">
          <MockupMobileIllustration />
        </div>
      ),
      size: "col-span-12 md:col-span-6 lg:col-span-4",
    },
    {
      title: "Global market coverage",
      description:
        "Track stocks, sectors, and economies worldwide. From Wall Street to emerging markets.",
      visual: (
        <div className="-mt-12 -mb-20 [&_svg]:h-[420px] [&_svg]:w-[420px]">
          <GlobeIllustration />
        </div>
      ),
      size: "col-span-12 md:col-span-6 lg:col-span-4",
    },
    {
      title: "On your radar",
      description: (
        <p className="max-w-[460px]">
          Watchlists powered by AI keep the companies you care about—like Apple and NVIDIA—on your radar so you never miss the signal.
        </p>
      ),
      visual: (
        <div className="-mr-32 -ml-40">
          <TilesIllustration />
        </div>
      ),
      size: "col-span-12 md:col-span-6 lg:col-span-4",
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
