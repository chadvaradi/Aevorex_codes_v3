import * as React from "react";
import { Link } from "lucide-react";
import { cn } from "@/lib/utils";
import Glow from "../../launch-ui-pro-2.3.3/ui/glow";
import { Mockup } from "../../launch-ui-pro-2.3.3/ui/mockup";
import Screenshot from "../../launch-ui-pro-2.3.3/ui/screenshot";

function GeminiCliIllustration({ className }: { className?: string }) {
  return (
    <div
      data-slot="mockup-browser-illustration"
      className={cn("h-full w-full", className)}
    >
      <div className="relative h-full w-full">
        <div className="absolute top-0 left-[50%] z-10 w-full -translate-x-[50%] translate-y-0 transition-all duration-1000 ease-in-out group-hover:-translate-y-4">
          <Mockup
            type="responsive"
            className="min-w-[640px] flex-col rounded-[12px]"
          >
              
            <Screenshot
              srcLight="/gemini-cli.png"
              srcDark="/gemini-cli.png"
              alt="Launch UI app screenshot"
              width={1340}
              height={820}
            />
          </Mockup>
        </div>
        <Glow
          variant="center"
          className="translate-y-0 scale-x-200 opacity-20 transition-all duration-1000 group-hover:-translate-y-12 group-hover:opacity-30"
        />
      </div>
    </div>
  );
}

export default GeminiCliIllustration;
