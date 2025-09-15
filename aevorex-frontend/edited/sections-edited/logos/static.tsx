import { ReactNode } from "react";

import Logo from "@/launch-ui-pro-2.3.3/ui/logo";
import { Section } from "@/launch-ui-pro-2.3.3/ui/section";
import Bocconi from "@/launch-ui-pro-2.3.3/logos/Bocconi";
import BSML from "@/launch-ui-pro-2.3.3/logos/BSML";
import BSFM from "@/launch-ui-pro-2.3.3/logos/BSFM";
import Catalog from "@/launch-ui-pro-2.3.3/logos/catalog";
import PictelAI from "@/launch-ui-pro-2.3.3/logos/pictelai";
import CoreOS from "@/launch-ui-pro-2.3.3/logos/coreos";
import EasyTax from "@/launch-ui-pro-2.3.3/logos/easytax";
import Peregrin from "@/launch-ui-pro-2.3.3/logos/peregrin";
import LeapYear from "@/launch-ui-pro-2.3.3/logos/leapyear";

interface LogosProps {
  title?: string;
  logos?: ReactNode[] | false;
  className?: string;
}

export default function Logos({
  title = "Inspired by the communities we're part of",
  logos = [
    <Logo
    key="bsfm"
    image={BSFM}
    name="BSFM"
    width={120}
    height={120}
    showName={false}
  />,
    <Logo
      key="bocconi"
      image={Bocconi}
      name="Bocconi University"
      width={180}
      height={40}
      showName={false}
    />,
    <Logo
      key="bsml"
      image={BSML}
      name="BSML"
      width={140}
      height={140}
      showName={false}
    />,
 
    // <Logo
    //   key="catalog"
    //   image={Catalog}
    //   name="Catalog"
    //   width={114}
    //   height={36}
    //   showName={false}
    // />,
    // <Logo
    //   key="pictelai"
    //   image={PictelAI}
    //   name="PictelAI"
    //   width={123}
    //   height={36}
    //   showName={false}
    // />,
    // <Logo
    //   key="coreos"
    //   image={CoreOS}
    //   name="CoreOS"
    //   width={110}
    //   height={36}
    //   showName={false}
    // />,
    // <Logo
    //   key="easytax"
    //   image={EasyTax}
    //   name="EasyTax"
    //   width={120}
    //   height={36}
    //   showName={false}
    // />,
    // <Logo
    //   key="peregrin"
    //   image={Peregrin}
    //   name="Peregrin"
    //   width={123}
    //   height={36}
    //   showName={false}
    // />,
    // <Logo
    //   key="leapyear"
    //   image={LeapYear}
    //   name="LeapYear"
    //   width={123}
    //   height={36}
    //   showName={false}
    // />,
  ],
  className,
}: LogosProps) {
  return (
    <Section className={className}>
      <div className="max-w-container mx-auto flex flex-col items-center gap-8 text-center">
        <h2 className="text-md text-muted-foreground font-semibold">{title}</h2>
        {logos !== false && logos.length > 0 && (
          <div className="flex flex-wrap items-center justify-center gap-8">
            {logos}
          </div>
        )}
      </div>
    </Section>
  );
}
