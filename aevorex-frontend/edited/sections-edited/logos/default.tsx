import { ReactNode } from "react";

import Figma from "@/launch-ui-pro-2.3.3/logos/figma";
import React from "@/launch-ui-pro-2.3.3/logos/react";
import ShadcnUi from "@/launch-ui-pro-2.3.3/logos/shadcn-ui";
import Tailwind from "@/launch-ui-pro-2.3.3/logos/tailwind";
import TypeScript from "@/launch-ui-pro-2.3.3/logos/typescript";
import Logo from "@/launch-ui-pro-2.3.3/ui/logo";
import { Section } from "@/launch-ui-pro-2.3.3/ui/section";
import { Badge } from "@/launch-ui-pro-2.3.3/ui/badge";

interface LogosProps {
  title?: string;
  badge?: ReactNode | false;
  logos?: ReactNode[] | false;
  className?: string;
}

export default function Logos({
  title = "Inspired by the communities we're part of",
  badge = (
    <Badge variant="outline" className="border-brand/30 text-brand">
      Last updated: 1000
    </Badge>
  ),
  logos = [
    // <Logo key="figma" image={Figma} name="Figma" />,
    // <Logo key="react" image={React} name="React" version="19.0.0" />,
    // <Logo
    //   key="typescript"
    //   image={TypeScript}
    //   name="TypeScript"
    //   version="5.6.3"
    // />,
    // <Logo
    //   key="shadcn"
    //   image={ShadcnUi}
    //   name="Shadcn/ui"
    //   version="2.4.0"
    //   badge="New"
    // />,
    // <Logo
    //   key="tailwind"
    //   image={Tailwind}
    //   name="Tailwind"
    //   version="4.0"
    //   badge="New"
    // />,
  ],
  className,
}: LogosProps) {
  return (
    <Section className={className}>
      <div className="max-w-container mx-auto flex flex-col items-center gap-8 text-center">
        <div className="flex flex-col items-center gap-6">
          {badge !== false && badge}
          <h2 className="text-md font-semibold sm:text-2xl">{title}</h2>
        </div>
        {logos !== false && logos.length > 0 && (
          <div className="flex flex-wrap items-center justify-center gap-8">
            {logos}
          </div>
        )}
      </div>
    </Section>
  );
}
