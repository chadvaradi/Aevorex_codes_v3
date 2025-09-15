import {
  Lock,
  Network,
  User,
  ArrowRight,
  Cloud,
  Server,
  Settings,
  Database,
  Globe,
  Webhook,
} from "lucide-react";

import Navbar from "../../sections/navbar/floating";
import Hero from "../../sections/hero/illustration";
import Stats from "../../sections/stats/grid-boxed";
import Logos from "../../sections/logos/grid-6";
import BentoGrid from "../../sections/bento-grid/3-rows-top";
import FeatureIllustrationBottom from "../../sections/feature/illustration-bottom";
import Items from "../../sections/items/default-brand";
import TestimonialsGrid from "../../sections/testimonials/grid";
import Pricing from "../../sections/pricing/3-cols-subscription";
import FAQ from "../../sections/faq/static";
import CTA from "../../sections/cta/box";
import Footer from "../../sections/footer/5-columns";
import LunaLogo from "../../logos/luna";
import Catalog from "../../logos/catalog";
import CoreOS from "../../logos/coreos";
import LeapYear from "../../logos/leapyear";
import Peregrin from "../../logos/peregrin";
import PictelAI from "../../logos/pictelai";
import RisingSmallIllustration from "../../illustrations/rising-small";
import RisingLargeIllustration from "../../illustrations/rising-large";
import MockupBrowserIllustration from "../../illustrations/mockup-browser";
import ChatIllustration from "../../illustrations/chat";
import CodeEditorIllustration from "../../illustrations/code-editor";
import MockupMobileIllustration from "../../illustrations/mockup-mobile";
import { Button } from "../../ui/button";
import { Input } from "../../ui/input";

export default function MCPServerPage() {
  return (
    <div
      className="flex flex-col"
      style={
        {
          "--brand-foreground": "var(--brand-titanium-foreground)",
          "--brand": "var(--brand-titanium)",
          "--primary": "light-dark(var(--brand-titanium), oklch(0.985 0 0))",
          "--background": "var(--background-titanium)",
          "--muted": "var(--background-titanium)",
          "--radius": "var(--radius-default)",
        } as React.CSSProperties
      }
    >
      <Navbar
        logo={<LunaLogo className="text-foreground dark:text-white" />}
        name="Luna"
        actions={[
          { text: "Login", href: "#" },
          {
            text: "Join waitlist",
            href: "#",
            isButton: true,
            variant: "default",
          },
        ]}
      />
      <main className="flex-1">
        <Hero
          title="Build MCP servers on a global edge network"
          description="Our platform enables you to quickly deploy MCP servers with global distribution, advanced caching, and optimized performance on our worldwide edge infrastructure."
          illustration={<RisingSmallIllustration />}
          form={
            <>
              <form className="flex w-full max-w-[420px] gap-2">
                <Input
                  type="email"
                  placeholder="Email address"
                  className="border-border/10 bg-foreground/10 grow"
                />
                <Button variant="default" size="lg" asChild>
                  <a href="https://www.launchuicomponents.com/">Join waitlist</a>
                </Button>
              </form>
              <p className="text-muted-foreground text-xs">
                We&apos;ll notify you when we launch.
              </p>
            </>
          }
        />
        <Stats
          title="Industry-leading performance"
          description="Our MCP servers offer exceptional speed and reliability, powering thousands of applications across the globe."
          items={[
            {
              value: "99.99%",
              label: "Uptime guarantee",
              description: "We ensure maximum availability of your MCP servers",
            },
            {
              value: "200+",
              label: "Edge locations",
              description: "Global network presence for reduced latency",
            },
            {
              value: "5,000+",
              label: "Active deployments",
              description: "Trusted by developers across industries",
            },
            {
              value: "<10ms",
              label: "Response time",
              description: "Lightning-fast request processing",
            },
          ]}
        />
        <Logos
          title="Trusted by technology-forward organizations"
          logoItems={[
            { logo: <Catalog className="h-8 w-auto" /> },
            { logo: <CoreOS className="h-8 w-auto" /> },
            { logo: <LeapYear className="h-8 w-auto" /> },
            { logo: <Peregrin className="h-8 w-auto" /> },
            { logo: <PictelAI className="h-8 w-auto" /> },
            { logo: <LunaLogo className="h-8 w-auto" /> },
          ]}
        />
        <BentoGrid
          title="Advanced MCP server features"
          description="Our platform provides a comprehensive suite of tools for deploying, managing, and scaling your MCP servers on the CloudFlare Network infrastructure."
          tiles={[
            {
              title: "Easy Deployment",
              description: (
                <>
                  <p className="max-w-[320px] lg:max-w-[460px]">
                    Deploy your MCP server with just a few clicks using our
                    intuitive interface or via CLI. No complex configuration
                    required to get started.
                  </p>
                </>
              ),
              visual: (
                <div className="min-h-[240px] grow basis-0 sm:p-4 md:min-h-[320px] md:py-12 lg:min-h-[360px]">
                  <MockupBrowserIllustration />
                </div>
              ),
              icon: (
                <Server className="text-muted-foreground size-6 stroke-1" />
              ),
              size: "col-span-12 md:flex-row",
            },
            {
              title: "Global Distribution",
              description: (
                <p className="max-w-[460px]">
                  Automatically distribute your MCP instances across our global
                  edge network to ensure low latency and high availability for
                  all users.
                </p>
              ),
              visual: (
                <div className="min-h-[160px] grow items-center self-center">
                  <ChatIllustration />
                </div>
              ),
              icon: <Globe className="text-muted-foreground size-6 stroke-1" />,
              size: "col-span-12 md:col-span-6 lg:col-span-5",
            },
            {
              title: "Scalable Infrastructure",
              description: (
                <p className="max-w-[460px]">
                  Our system automatically scales your MCP servers based on
                  traffic demands, ensuring optimal performance even during
                  traffic spikes.
                </p>
              ),
              visual: (
                <div className="min-h-[240px] w-full grow items-center self-center px-4 lg:px-12">
                  <CodeEditorIllustration />
                </div>
              ),
              icon: (
                <Database className="text-muted-foreground size-6 stroke-1" />
              ),
              size: "col-span-12 md:col-span-6 lg:col-span-7",
            },
            {
              title: "Advanced Caching",
              description:
                "Intelligent caching mechanisms dramatically reduce load times and minimize origin server requests, improving user experience.",
              visual: (
                <div className="min-h-[240px] grow basis-0 sm:p-4 md:min-h-[320px] md:py-12 lg:min-h-[360px]">
                  <MockupBrowserIllustration />
                </div>
              ),
              icon: <Cloud className="text-muted-foreground size-6 stroke-1" />,
              size: "col-span-12 md:col-span-6 lg:col-span-6",
            },
            {
              title: "Real-time Analytics",
              description: (
                <p className="max-w-[460px]">
                  Monitor your MCP server performance, traffic patterns, and
                  resource usage with comprehensive real-time analytics.
                </p>
              ),
              visual: (
                <div className="min-h-[240px] w-full grow items-center self-center px-4 lg:px-12">
                  <MockupMobileIllustration />
                </div>
              ),
              icon: (
                <Settings className="text-muted-foreground size-6 stroke-1" />
              ),
              size: "col-span-12 md:col-span-6 lg:col-span-6",
            },
          ]}
        />
        <FeatureIllustrationBottom
          title="Comprehensive MCP infrastructure"
          description="Our platform integrates seamlessly with your existing applications, providing a robust infrastructure for running your MCP servers across a global network."
          visual={<RisingLargeIllustration />}
        />
        <Items
          title="MCP server capabilities"
          items={[
            {
              title: "SSL Encryption",
              description:
                "Automatic SSL certificate provisioning and renewal for secure connections to your MCP servers.",
              icon: <Lock className="text-muted-foreground size-6 stroke-1" />,
            },
            {
              title: "Custom Domains",
              description:
                "Connect your own domain names to your MCP servers with easy DNS configuration and management.",
              icon: <Globe className="text-muted-foreground size-6 stroke-1" />,
            },
            {
              title: "API Integration",
              description:
                "Comprehensive API access for automating deployments, configurations, and management tasks.",
              icon: (
                <Network className="text-muted-foreground size-6 stroke-1" />
              ),
            },
            {
              title: "Edge Computing",
              description:
                "Execute code at the edge for faster responses and reduced backend load.",
              icon: <Cloud className="text-muted-foreground size-6 stroke-1" />,
            },
            {
              title: "Configuration Management",
              description:
                "Version-controlled configuration files with easy rollback capabilities.",
              icon: (
                <Settings className="text-muted-foreground size-6 stroke-1" />
              ),
            },
            {
              title: "Logging & Monitoring",
              description:
                "Advanced logging with searchable history and customizable alerts for critical events.",
              icon: (
                <Database className="text-muted-foreground size-6 stroke-1" />
              ),
            },
            {
              title: "Priority Support",
              description:
                "Priority support for critical issues and proactive assistance to ensure your MCP servers are always running smoothly.",
              icon: <User className="text-muted-foreground size-6 stroke-1" />,
            },
            {
              title: "Custom Integrations",
              description:
                "Seamless integration with your existing systems and tools for a streamlined deployment process.",
              icon: (
                <Webhook className="text-muted-foreground size-6 stroke-1" />
              ),
            },
          ]}
        />
        <TestimonialsGrid
          items={[
            {
              name: "David Chen",
              role: "CTO, TechStream",
              text: "Deploying our MCP servers on CloudFlare Network has reduced our global response times by 65%. The integration was seamless and the performance is outstanding.",
              image: "/avatars/sarah.jpg",
              Logo: Catalog,
            },
            {
              name: "Alex Rodriguez",
              role: "Lead Developer, DataFlex",
              text: "The ability to deploy MCP servers across multiple regions with a single command has transformed our deployment pipeline. We're shipping features faster than ever.",
              image: "/avatars/marcin.jpg",
              Logo: CoreOS,
            },
          ]}
        />
        <Pricing
          title="MCP server plans for applications of all sizes"
          description="Choose the right level of resources and capabilities for your application needs with our flexible MCP server packages."
          plans={[
            {
              name: "Developer",
              description: "Essential features for individual developers",
              monthlyPrice: 19,
              yearlyPrice: 190,
              features: [
                "1 MCP server instance",
                "10GB bandwidth/month",
                "3 custom domains",
                "Basic analytics",
                "Community support",
              ],
              cta: {
                label: "Get started",
                href: "#",
                variant: "glow",
              },
            },
            {
              name: "Business",
              description: "Advanced features for growing applications",
              monthlyPrice: 79,
              yearlyPrice: 790,
              variant: "glow-brand",
              features: [
                "10 MCP server instances",
                "100GB bandwidth/month",
                "Unlimited custom domains",
                "Advanced analytics",
                "Edge computing",
                "Priority support",
              ],
              cta: {
                label: "Get started",
                href: "#",
                variant: "default",
              },
            },
            {
              name: "Enterprise",
              description:
                "Complete solution for mission-critical applications",
              monthlyPrice: 199,
              yearlyPrice: 1990,
              features: [
                "Unlimited MCP instances",
                "Custom bandwidth allocation",
                "Dedicated account manager",
                "Custom integrations",
                "Advanced security features",
                "24/7 premium support",
              ],
              cta: {
                label: "Contact sales",
                href: "#",
                variant: "glow",
              },
            },
          ]}
        />
        <FAQ
          title="Frequently asked questions"
          items={[
            {
              question: "How quickly can I deploy an MCP server?",
              answer: (
                <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                  Deployment typically takes less than 2 minutes. Once
                  you&apos;ve created your account, you can deploy your first
                  MCP server with just a few clicks or a single CLI command. The
                  server will be instantly available across our global network.
                </p>
              ),
            },
            {
              question: "Can I use my existing edge provider account?",
              answer: (
                <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                  Yes, you can connect your existing edge provider account to
                  our platform. This allows you to manage your MCP servers
                  alongside your other services while taking advantage of our
                  specialized MCP management tools.
                </p>
              ),
            },
            {
              question: "How does scaling work for MCP servers?",
              answer: (
                <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                  Our platform automatically scales your MCP servers based on
                  traffic patterns. You can also set manual scaling rules or
                  schedule scaling events for predictable traffic increases. All
                  scaling happens without downtime or performance degradation.
                </p>
              ),
            },
            {
              question: "Can I run custom code on my MCP servers?",
              answer: (
                <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                  Absolutely. Our MCP servers support custom code execution in
                  multiple languages, including JavaScript, Python, Go, and
                  Rust. You can deploy code directly from your Git repositories
                  or upload directly through our interface or API.
                </p>
              ),
            },
            {
              question: "Do you offer a free trial?",
              answer: (
                <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                  Yes, we offer a 14-day free trial of our Business plan with no
                  credit card required. This gives you full access to our
                  platform features so you can evaluate how it works with your
                  applications before making a commitment.
                </p>
              ),
            },
          ]}
        />
        <CTA
          title="Ready to deploy your MCP server?"
          description="Get started with our platform today and experience the power of MCP servers on our global edge infrastructure."
          buttons={[
            {
              text: "Deploy now",
              href: "#",
              variant: "default",
            },
            {
              text: "View documentation",
              href: "#",
              variant: "outline",
            },
          ]}
        />
      </main>
      <Footer
        logo={<LunaLogo className="text-foreground dark:text-white" />}
        columns={[
          {
            title: "Product",
            links: [
              { text: "Features", href: "#" },
              { text: "Pricing", href: "#" },
              { text: "Documentation", href: "#" },
              { text: "API", href: "#" },
            ],
          },
          {
            title: "Resources",
            links: [
              { text: "Guides", href: "#" },
              { text: "Examples", href: "#" },
              { text: "Webinars", href: "#" },
              { text: "Case Studies", href: "#" },
            ],
          },
          {
            title: "Company",
            links: [
              { text: "About", href: "#" },
              { text: "Blog", href: "#" },
              { text: "Careers", href: "#" },
              { text: "Contact", href: "#" },
            ],
          },
        ]}
        copyright="© 2023 MCP Server Platform. All rights reserved."
        socials={[
          {
            label: "Twitter",
            href: "#",
            icon: <ArrowRight />,
          },
          {
            label: "LinkedIn",
            href: "#",
            icon: <ArrowRight />,
          },
          {
            label: "GitHub",
            href: "#",
            icon: <ArrowRight />,
          },
        ]}
      />
    </div>
  );
}
