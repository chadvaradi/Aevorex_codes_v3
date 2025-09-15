import { ReactNode } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";

import {
  Footer,
  FooterColumn,
  FooterBottom,
  FooterContent,
} from "@/launch-ui-pro-2.3.3/ui/footer";
import LaunchUI from "@/launch-ui-pro-2.3.3/logos/launch-ui";
import Github from "@/launch-ui-pro-2.3.3/logos/github";
import X from "@/launch-ui-pro-2.3.3/logos/x";
import Discord from "@/launch-ui-pro-2.3.3/logos/discord";

interface FooterLink {
  text: string;
  href: string;
}

interface FooterColumnProps {
  title: string;
  links: FooterLink[];
}

interface SocialLink {
  icon: ReactNode;
  href: string;
  label: string;
}

interface FooterProps {
  logo?: ReactNode;
  name?: string;
  columns?: FooterColumnProps[];
  copyright?: string;
  socials?: SocialLink[];
  className?: string;
}

export default function FooterSection({
  logo = <LaunchUI />,
  name = "Launch UI",
  columns = [
    {
      title: "Product",
      links: [
        { text: "Changelog", href: "#" },
        { text: "Documentation", href: "#" },
      ],
    },
    {
      title: "Company",
      links: [
        { text: "About", href: "#" },
        { text: "Careers", href: "#" },
        { text: "Blog", href: "#" },
      ],
    },
    {
      title: "Contact",
      links: [
        { text: "Discord", href: "#" },
        { text: "Twitter", href: "#" },
        { text: "Github", href: "https://www.launchuicomponents.com/" },
      ],
    },
    {
      title: "Legal",
      links: [
        { text: "Privacy Policy", href: "#" },
        { text: "Terms of Service", href: "#" },
        { text: "Cookie Policy", href: "#" },
      ],
    },
  ],
  copyright = "© 2025 Aevorex. All rights reserved",
  socials = [
    {
      icon: <Github className="size-5" />,
      href: "https://www.launchuicomponents.com/",
      label: "GitHub",
    },
    {
      icon: <X className="size-5" />,
      href: "https://www.launchuicomponents.com/",
      label: "Twitter",
    },
    {
      icon: <Discord className="size-5" />,
      href: "/",
      label: "Discord",
    },
  ],
  className,
}: FooterProps) {
  return (
    <footer className={cn("bg-background w-full px-4", className)}>
      <div className="max-w-container mx-auto">
        <Footer className="border-border dark:border-border/15 border-t pt-8">
          <FooterContent className="sm:grid-cols-2 md:grid-cols-3">
            <FooterColumn className="col-span-2 flex-row items-center justify-between gap-8 border-b pb-8 md:col-span-1 md:flex-col md:items-start md:justify-start md:border-b-0">
              <div className="flex items-center gap-2">
                {logo}
                <h3 className="text-xl font-bold">{name}</h3>
              </div>
              <div className="ml-2.5 flex gap-4 sm:ml-0">
                {socials.map((social, index) => (
                  <Link
                    key={index}
                    href={social.href}
                    className="text-muted-foreground"
                  >
                    <span className="sr-only">{social.label}</span>
                    {social.icon}
                  </Link>
                ))}
              </div>
            </FooterColumn>
            {columns.map((column, index) => (
              <FooterColumn key={index}>
                <h3 className="text-md pt-1 font-semibold">{column.title}</h3>
                {column.links.map((link, linkIndex) => (
                  <a
                    key={linkIndex}
                    href={link.href}
                    className="text-muted-foreground text-sm"
                  >
                    {link.text}
                  </a>
                ))}
              </FooterColumn>
            ))}
          </FooterContent>
          <FooterBottom className="border-0">
            <div>{copyright}</div>
          </FooterBottom>
        </Footer>
      </div>
    </footer>
  );
}
