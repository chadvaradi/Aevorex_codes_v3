import { ReactNode } from "react";

import ReactLogo from "@/launch-ui-pro-2.3.3/logos/react";
import Logo from "@/launch-ui-pro-2.3.3/ui/logo";
import { Section } from "@/launch-ui-pro-2.3.3/ui/section";

interface LogosProps {
  title?: string;
  logos?: ReactNode[] | false;
  className?: string;
}

export default function Logos({
  title = "Inspired by the communities we're part of",
  logos = [
    // <Logo key="react" image={ReactLogo} name="React" version="18.3.1" />,
    // Add more default logos here if needed
  ],
  className,
}: LogosProps) {
  return (
    <Section className={className}>
      <div className="max-w-container mx-auto flex flex-col items-center gap-8 text-center">
        <h2 className="text-md font-semibold">{title}</h2>
        {logos !== false && logos.length > 0 && (
          <div className="flex flex-wrap items-center justify-center gap-8">
            {logos}
          </div>
        )}
      </div>
    </Section>
  );
}
