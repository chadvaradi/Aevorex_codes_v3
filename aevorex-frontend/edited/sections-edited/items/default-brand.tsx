import { ReactNode } from "react";
import {
  Cpu,
  DollarSign,
  File,
  Globe,
  Linkedin,
  Lightbulb,
  Mail,
  MonitorSmartphoneIcon,
  
} from "lucide-react";

import {
  Item,
  ItemIcon,
  ItemTitle,
  ItemDescription,
} from "@/launch-ui-pro-2.3.3/ui/item";
import { Section } from "@/launch-ui-pro-2.3.3/ui/section";

interface ItemProps {
  title: string;
  description: string;
  icon: ReactNode;
}

interface ItemsProps {
  title?: string;
  items?: ItemProps[] | false;
  className?: string;
}

export default function Items({
  title = "Fast results, even if you're just starting out.",
  items = [
    {
      title: "AI-powered financial research",
      description: "Leverage advanced AI to analyze markets and data faster than ever.",
      icon: <Cpu className="text-brand size-5 stroke-1" />,
    },
    {
      title: "AI-powered finance",
      description: "Track and analyze markets with currency-level precision.",
      icon: <DollarSign className="text-brand size-5 stroke-1" />,
    },
    {
      title: "Seamless workflows",
      description: "Export docs, continue in ChatGPT, or use instantly in other tools.",
      icon: <File className="text-brand size-5 stroke-1" />,
    },
    {
      title: "Global insights",
      description: "Made for worldwide coverage and emerging markets.",
      icon: <Globe className="text-brand size-5 stroke-1" />,
    },
    {
      title: "Early network expansion",
      description: "Build your connections among students and professionals to grow faster.",
      icon: <Linkedin className="text-brand size-5 stroke-1" />,
    },
    {
      title: "Research smarter",
      description: "Turn raw data into sharper insights and actionable intelligence.",
      icon: <Lightbulb className="text-brand size-5 stroke-1" />,
    },
    {
      title: "Stay connected",
      description: "Email alerts, market newsletters, and updates in real time.",
      icon: <Mail className="text-brand size-5 stroke-1" />,
    },
    {
      title: "Mobile-ready design",
      description: "Optimized for seamless use on both smartphones and laptops.",
      icon: <MonitorSmartphoneIcon className="text-brand size-5 stroke-1" />,
    },
  ],
  className,
}: ItemsProps) {
  return (
    <Section className={className}>
      <div className="max-w-container mx-auto flex flex-col items-center gap-6 sm:gap-20">
        <h2 className="max-w-[560px] text-center text-3xl leading-tight font-semibold sm:text-5xl sm:leading-tight">
          {title}
        </h2>
        {items !== false && items.length > 0 && (
          <div className="grid auto-rows-fr grid-cols-2 gap-0 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4">
            {items.map((item, index) => (
              <Item key={index}>
                <ItemTitle className="flex items-center gap-2">
                  <ItemIcon>{item.icon}</ItemIcon>
                  {item.title}
                </ItemTitle>
                <ItemDescription>{item.description}</ItemDescription>
              </Item>
            ))}
          </div>
        )}
      </div>
    </Section>
  );
}
