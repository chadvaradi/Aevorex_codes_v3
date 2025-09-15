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
  Phone,
  Mail,
  Sparkles,
  MessageCircle,
  Code,
  Cable,
  Smartphone
} from "lucide-react";
import { Section } from "@/launch-ui-pro-2.3.3/ui/section";
import Navbar from "@/edited/sections-edited/navbar/floating";
import Hero from "@/launch-ui-pro-2.3.3/sections/hero/illustration";
import Stats from "@/launch-ui-pro-2.3.3/sections/stats/grid-boxed";
import Logos from "@/launch-ui-pro-2.3.3/sections/logos/grid-6";
import BentoGrid from "@/launch-ui-pro-2.3.3/sections/bento-grid/3-rows-top";
import FeatureIllustrationBottom from "@/launch-ui-pro-2.3.3/sections/feature/illustration-bottom";
import Items from "@/launch-ui-pro-2.3.3/sections/items/default-brand";
import TestimonialsGrid from "@/launch-ui-pro-2.3.3/sections/testimonials/grid";
import Pricing from "@/launch-ui-pro-2.3.3/sections/pricing/3-cols-subscription";
import FAQ from "@/launch-ui-pro-2.3.3/sections/faq/2-cols-raised";
import CTA from "@/launch-ui-pro-2.3.3/sections/cta/box";
import Footer from "@/edited/sections-edited/footer/minimal";
import Calendar from "@/edited/calendar-edited-consulting/app";

import AevorexLogo from "@/launch-ui-pro-2.3.3/logos/aevorex";
import Catalog from "@/launch-ui-pro-2.3.3/logos/catalog";
import CoreOS from "@/launch-ui-pro-2.3.3/logos/coreos";
import LeapYear from "@/launch-ui-pro-2.3.3/logos/leapyear";
import Peregrin from "@/launch-ui-pro-2.3.3/logos/peregrin";
import PictelAI from "@/launch-ui-pro-2.3.3/logos/pictelai";
import OpenAIDark from "@/launch-ui-pro-2.3.3/logos/openai-dark";
import AnthropicDark from "@/launch-ui-pro-2.3.3/logos/anthropic-dark";
import GeminiDark from "@/launch-ui-pro-2.3.3/logos/gemini-dark";
import XAIDark from "@/launch-ui-pro-2.3.3/logos/xai-dark";
import MetaLlamaDark from "@/launch-ui-pro-2.3.3/logos/meta-llama-dark";
import CursorDark from "@/launch-ui-pro-2.3.3/logos/cursor-dark";
import OpenAILight from "@/launch-ui-pro-2.3.3/logos/openai-light";
import AnthropicLight from "@/launch-ui-pro-2.3.3/logos/anthropic-light";
import GeminiLight from "@/launch-ui-pro-2.3.3/logos/gemini-light";
import XAILight from "@/launch-ui-pro-2.3.3/logos/xai-light";
import MetaLlamaLight from "@/launch-ui-pro-2.3.3/logos/meta-llama-light";
import CursorLight from "@/launch-ui-pro-2.3.3/logos/cursor-light";
import LinkedIn from "@/launch-ui-pro-2.3.3/logos/linkedin";

import RisingSmallIllustration from "@/launch-ui-pro-2.3.3/illustrations/rising-small";
import RisingLargeIllustration from "@/launch-ui-pro-2.3.3/illustrations/rising-large";
import ChatIllustration from "@/launch-ui-pro-2.3.3/illustrations/chat";
import CodeEditorIllustration from "@/launch-ui-pro-2.3.3/illustrations/code-editor";
import { Beam } from "@/launch-ui-pro-2.3.3/ui/beam";
import { Button } from "@/launch-ui-pro-2.3.3/ui/button";
import { Input } from "@/launch-ui-pro-2.3.3/ui/input";
import { Mockup, MockupFrame } from "@/launch-ui-pro-2.3.3/ui/mockup";
import Screenshot from "@/launch-ui-pro-2.3.3/ui/screenshot";
import Glow from "@/launch-ui-pro-2.3.3/ui/glow";
import { Link } from "lucide-react";
import { cn } from "@/lib/utils";
import FeatureStickyLeft from "@/launch-ui-pro-2.3.3/sections/feature/sticky-left";
import GeminiCliIllustration from "@/edited/illustrations-edited/gemini-cli";
import FeatureStickyRight from "@/launch-ui-pro-2.3.3/sections/feature/sticky-right";
import ConsultingForm from "./consulting-form";
function MockupBrowserIllustration({ className }: { className?: string }) {
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
              srcLight="/screenshots/chatgpt.png"
              srcDark="/screenshots/chatgpt.png"
              alt="ChatGPT Platform screenshot"
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

// Custom MockupBrowserIllustration component with cursor.png (for Advanced Caching)
function MockupBrowserIllustrationCursor({ className }: { className?: string }) {
  return (
    <div
      data-slot="mockup-browser-illustration-cursor"
      className={cn("h-full w-full", className)}
    >
      <div className="relative h-full w-full">
        <div className="absolute top-0 left-[50%] z-10 w-full -translate-x-[50%] translate-y-0 transition-all duration-1000 ease-in-out group-hover:-translate-y-4">
          <Mockup
            type="responsive"
            className="min-w-[640px] flex-col rounded-[12px]"
          >
            
            <Screenshot
              srcLight="/screenshots/cursor.png"
              srcDark="/screenshots/cursor.png"
              alt="Cursor Platform screenshot"
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

// Custom MockupMobileIllustration component with grok_mobile_img.jpeg
function MockupMobileIllustration() {
  return (
    <div
      data-slot="mockup-mobile-illustration"
      className="relative h-full w-full"
    >
      <MockupFrame
        size="small"
        className="absolute top-0 left-[50%] w-full max-w-[366px] -translate-x-[50%] translate-y-0 rounded-[56px] transition-all duration-1000 ease-in-out group-hover:-translate-y-8"
      >
        <Mockup type="mobile">
          <Screenshot
            srcLight="/screenshots/grok_mobile_img.jpeg"
            srcDark="/screenshots/grok_mobile_img.jpeg"
            alt="Grok Mobile screenshot"
            width={350}
            height={765}
          />
        </Mockup>
      </MockupFrame>
      <Glow
        variant="bottom"
        className="translate-y-20 scale-x-[1.2] opacity-70 transition-all duration-1000 group-hover:translate-y-8 group-hover:opacity-100"
      />
    </div>
  );
}

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
        logo={<AevorexLogo className="text-foreground dark:text-white" />}
        name="Aevorex"
        mobileLinks={[
          { text: "Home", href: "#hero" },
          { text: "Book a Call", href: "#calendar" },
          { text: "Finance × AI", href: "#finance" },
          { text: "Innovation × Execution", href: "#innovation" },
          { text: "AI Tools", href: "#bento" },
          { text: "FAQ", href: "#faq" },
          { text: "Contact", href: "#contact" },
          { text: "HU", href: "https://aevorex.com/marketing/consulting/hun" },
        ]}
        actions={[
          { text: "HU", href: "https://aevorex.com/marketing/consulting/hun" },
          { text: "Book a consultation", href: "#calendar", isButton: true, variant: "default" },
        ]}
      />
      <main className="flex-1">
        <section id="hero">
          <Hero
            title="Develop Your Competitive AI Strategy"
            description="Practical, Scalable, AI-Driven Solutions Tailored to Your Business."
            illustration={<RisingSmallIllustration />}
          form={<ConsultingForm />}
        />
        </section>
        <section id="calendar">
        <Section className="pt-0">
          <div className="max-w-container mx-auto flex flex-col gap-6 sm:gap-10">
            <div className="text-center">
              <h2 className="text-3xl font-semibold sm:text-5xl">
                Book a consultation
              </h2>
              <p className="text-muted-foreground mt-2">
                Select a {45} minute slot that fits your schedule. Booking is completed on Calendly.
              </p>
            </div>

            {/* A Calendar saját keretet és üveg-hátteret ad magának */}
            <Calendar heightClassName="h-[420px] sm:h-[560px] md:h-[720px] lg:h-[880px]" />
          </div>
        </Section>
        </section>
        
        {/* <Stats
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
        /> */}
        
        {/* Dark theme logos */}
        <div className="dark:block hidden">
          <Logos
            title="We Help You Leverage Leading AI Platforms"
            logoItems={[
              { logo: <OpenAIDark className="h-24 w-auto" /> },
              { logo: <AnthropicDark className="h-24 w-auto" /> },
              { logo: <GeminiDark className="h-24 w-auto" /> },
              { logo: <XAIDark className="h-24 w-auto" /> },
              { logo: <MetaLlamaDark className="h-24 w-auto" /> },
              { logo: <CursorDark className="h-24 w-auto" /> },
            ]}
          />
        </div>

        {/* Light theme logos */}
        <div className="dark:hidden block">
          <Logos
            title="We Help You Leverage Leading AI Platforms"
            logoItems={[
              { logo: <OpenAILight className="h-24 w-auto" /> },
              { logo: <AnthropicLight className="h-24 w-auto" /> },
              { logo: <GeminiLight className="h-24 w-auto" /> },
              { logo: <XAILight className="h-24 w-auto" /> },
              { logo: <MetaLlamaLight className="h-24 w-auto" /> },
              { logo: <CursorLight className="h-24 w-auto" /> },
            ]}
          />
        </div>
        <p className="text-center text-xs text-muted-foreground mt-4">
          Logos are trademarks of their respective owners; usage here indicates tooling compatibility, not endorsement.
        </p>


       <section id="finance">
       {/* Mobil és tablet (lg alatt) → hosszú verzió */}
<div className="block lg:hidden">
  <FeatureStickyLeft
    title="Bocconi Finance × Artificial Intelligence"
    description={
      <p className="text-muted-foreground">
        At one of Europe’s top finance schools, pioneering how AI tools can be mastered and applied with confidence.
      </p>
    }
    visual={
      <Beam tone="brandLight" className="after:scale-y-150 md:after:-translate-x-1/2">
        <Mockup type="mobile">
          <Screenshot
            srcLight="/portrait_sda_out_straight.jpeg"
            srcDark="/portrait_sda_out_straight.jpeg"
            alt="Mobile app preview"
            width={2000}
            height={720}
          />
        </Mockup>
        <Glow
          variant="center"
          className="translate-y-0 scale-x-200 opacity-20 transition-all duration-1000 group-hover:-translate-y-12 group-hover:opacity-30"
        />
      </Beam>
    }
  />
</div>

{/* Laptop és nagyobb (lg+) → rövid verzió */}
<div className="hidden lg:block">
  <FeatureStickyLeft
    title="Bocconi × AI"
    description={
      <p className="text-muted-foreground">
        At one of Europe’s top finance schools, pioneering how AI tools can be mastered and applied with confidence.
      </p>
    }
    visual={
      <Beam tone="brandLight" className="after:scale-y-150 md:after:-translate-x-1/2">
        <Mockup type="mobile">
          <Screenshot
            srcLight="/portrait_sda_out_straight.jpeg"
            srcDark="/portrait_sda_out_straight.jpeg"
            alt="Mobile app preview"
            width={2000}
            height={720}
          />
        </Mockup>
        <Glow
          variant="center"
          className="translate-y-0 scale-x-200 opacity-20 transition-all duration-1000 group-hover:-translate-y-12 group-hover:opacity-30"
        />
      </Beam>
    }
  />
</div>
</section>

<section id="innovation">
{/* Mobil és tablet (lg alatt) → hosszú verzió */}
<div className="block lg:hidden">
  <FeatureStickyRight
    title="Innovative Approach × Rapid Execution"
    description={
      <p className="text-muted-foreground">
        This page could have been live just 2 days after the initial concept.
      </p>
    }
    visual={
      <Beam tone="brandLight" className="after:scale-y-150 md:after:-translate-x-1/2">
        <Mockup type="mobile">
          <Screenshot
            srcLight="/bocconi_inside_back.jpeg"
            srcDark="/bocconi_inside_back.jpeg"
            alt="Mobile app preview"
            width={2000}
            height={720}
          />
        </Mockup>
        <Glow
          variant="center"
          className="translate-y-0 scale-x-200 opacity-20 transition-all duration-1000 group-hover:-translate-y-12 group-hover:opacity-30"
        />
      </Beam>
    }
  />
</div>

{/* Laptop és nagyobb (lg+) → rövid verzió */}
<div className="hidden lg:block">
  <FeatureStickyRight
    title="Innovation × Execution"
    description={
      <p className="text-muted-foreground">
       This page could have been live just 2 days after the initial concept.
      </p>
    }
    visual={
      <Beam tone="brandLight" className="after:scale-y-150 md:after:-translate-x-1/2">
        <Mockup type="mobile">
          <Screenshot
            srcLight="/bocconi_inside_back.jpeg"
            srcDark="/bocconi_inside_back.jpeg"
            alt="Mobile app preview"
            width={2000}
            height={720}
          />
        </Mockup>
        <Glow
          variant="center"
          className="translate-y-0 scale-x-200 opacity-20 transition-all duration-1000 group-hover:-translate-y-12 group-hover:opacity-30"
        />
      </Beam>
    }
  />
</div>
</section>
        <section id="bento">
        <BentoGrid
          title="Work Smarter With Today's Best AI Tools."
          description="Why use only ChatGPT when you can learn how to combine Gemini, Claude, Perplexity, Grok and beyond, applying them to coding, design, data, and strategy to deliver results?"
          tiles={[
            {
              title: "Advanced ChatGPT Usage",
              description: (
                <>
                  <p className="max-w-[320px] lg:max-w-[460px]">
                  Learn how to use ChatGPT not just as an assistant, 
                  but as your strategic partner. Adapt it to your workflows,
                   automate routine tasks, and support decision-making. 
                   It’s like adding extra brainpower to your team, that you can leverage 
                   far beyond a single person’s capacity.
                  </p>
                </>
              ),
              visual: (
                <div className="min-h-[240px] grow basis-0 sm:p-4 md:min-h-[320px] md:py-12 lg:min-h-[360px]">
                  <MockupBrowserIllustration />
                </div>
              ),
              icon: (
                <MessageCircle className="text-muted-foreground size-6 stroke-1" />
              ),
              size: "col-span-12 md:flex-row",
            },
            {
              title: "Use Deeper AI Tools in Your Workflows",
              description: (
                <p className="max-w-[460px]">
                  Be able to communicate more effectively with your AI tools,
                  not just through chat, but via CLI and integrated workflows.
                   Being able to understand the language of  the computer allows more powerful 
                  connections with your data, and code.
                </p>
              ),
              visual: (
                <div className="min-h-[160px] grow items-center self-center">
                  <GeminiCliIllustration />
                </div>
              ),
              icon: <Sparkles className="text-muted-foreground size-6 stroke-1" />,
              size: "col-span-12 md:col-span-6 lg:col-span-5",
            },
            {
              title: "AI Coding, Done Right",
              description: (
                <p className="max-w-[460px]">
                  Yes, AI can write code fast. But knowing which model to 
                  trust for refactoring, debugging, or building from scratch 
                  makes all the difference. I guide you through the strengths
                   and pitfalls of each tool, so you get cleaner code and fewer headaches and faster execution.
                </p>
              ),
              visual: (
                <div className="min-h-[240px] w-full grow items-center self-center px-4 lg:px-12">
                  <CodeEditorIllustration />
                </div>
              ),
              icon: (
                <Code className="text-muted-foreground size-6 stroke-1" />
              ),
              size: "col-span-12 md:col-span-6 lg:col-span-7",
            },
            {
              title: "A Whole AI Ecosystem",
              description:
                "Chat apps excel at memory. Some models are built for refactoring, others for debugging. Certain AI-powered IDEs shine in rapid prototyping, while others are made for scaling. I help you navigate the strengths and pitfalls of today’s tools, so you get real results without wasted effort.",
              visual: (
                <div className="min-h-[240px] grow basis-0 sm:p-4 md:min-h-[320px] md:py-12 lg:min-h-[360px]">
                  <MockupBrowserIllustrationCursor />
                </div>
              ),
              icon: <Cable className="text-muted-foreground size-6 stroke-1" />,
              size: "col-span-12 md:col-span-6 lg:col-span-6",
            },
            {
              title: "AI in Your Pocket",
              description: (
                <p className="max-w-[460px]">
                 Turn your phone into a superbrain. Learn how to use AI apps
                  on mobile as powerful companions: whether it’s brainstorming,
                   research, or creative work, right from your hand.

                </p>
              ),
              visual: (
                <div className="min-h-[240px] w-full grow items-center self-center px-4 lg:px-12">
                  <MockupMobileIllustration />
                </div>
              ),
              icon: (
                <Smartphone className="text-muted-foreground size-6 stroke-1" />
              ),
              size: "col-span-12 md:col-span-6 lg:col-span-6",
            },
          ]}
        />
        <FeatureIllustrationBottom
          title="Move Too Slow, Fall Behind. Move Too Fast, Break Things."
          description="AI adoption is urgent,  but rushing leads to errors. I help you find the balance: integrate tools quickly, safely, to keep your business competitive."
          visual={<RisingLargeIllustration />}
        />
        <Items
          title="AI Consulting Capabilities"
          items={[
            {
              title: "Tool Onboarding & Training",
              description:
                "Hands-on workshops to show how to use ChatGPT, Gemini, Claude and other AI tools effectively. Practical tips on memory, limits, and prompting.",
              icon: <Lock className="text-muted-foreground size-6 stroke-1" />,
            },
            {
              title: "License & Tool Strategy",
              description:
                "Guidance on which subscriptions are truly needed. Optimize cost by matching the right tools to the right teams instead of overspending on unused seats.",
              icon: <Globe className="text-muted-foreground size-6 stroke-1" />,
            },
            {
              title: "Management Insights",
              description:
                "Clear briefings for executives: what is hype, what is real, and where the risks are. Enabling CEOs, CFOs, and CTOs to make informed AI decisions.",
              icon: (
                <Network className="text-muted-foreground size-6 stroke-1" />
              ),
            },
            {
              title: "1:1 Workflow Coaching",
              description:
                "Individual sessions with employees to review their daily workflows. Identify automation opportunities and deliver actionable improvements they can apply immediately.",
              icon: <User className="text-muted-foreground size-6 stroke-1" />,
            },
            {
              title: "AI Adoption Roadmap",
              description:
                "A 3–6 month plan for structured AI rollout. Ensures the company adopts fast enough to stay competitive, but not so fast that it creates chaos.",
              icon: (
                <Settings className="text-muted-foreground size-6 stroke-1" />
              ),
            },
            {
              title: "Developer Enablement",
              description:
                "Support for engineering teams: which models to use for refactoring, debugging, or prototyping. Guidance on AI-powered IDEs like Cursor, Replit, or Windsurf.",
              icon: (
                <Code className="text-muted-foreground size-6 stroke-1" />
              ),
            },
            {
              title: "Best Practices & Pitfalls",
              description:
                "Knowledge transfer on what works and what doesn't. Save time by avoiding common AI mistakes and adopting tested best practices.",
              icon: (
                <Database className="text-muted-foreground size-6 stroke-1" />
              ),
            },
            {
              title: "Culture Shift: Asking Better Questions",
              description:
                "Train teams to use AI not as a shortcut to quick answers, but as a partner in critical thinking. Unlock human-level output by asking the right questions.",
              icon: (
                <MessageCircle className="text-muted-foreground size-6 stroke-1" />
              ),
            },
          ]}
        />
        </section>
        
        
        <section id="faq">
        <FAQ
          title="Frequently asked questions"
          items={[
            {
              question: "Why should we learn from you instead of just experimenting on our own?",
              answer: (
                <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                  Because unlike most teams, I don&apos;t do this as a side project. For me, it&apos;s a necessity. 
                  My own work requires me to track the latest AI trends, test new tools as soon as they appear, 
                  and learn their strengths and weaknesses in depth. In a company, no manager or employee has 
                  the time to research and experiment at this level. I bring you the distilled insights, 
                  so your team can skip the trial-and-error phase and apply what works immediately.
                </p>
              ),
            },
            {
              question: "How do you help us avoid AI's common pitfalls?",
              answer: (
                <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                  AI tools are powerful but not flawless. I know the failure modes, hallucinations, 
                  inconsistent outputs, and compliance risks, and I help you build workflows that minimize 
                  these issues without adding heavy oversight or unnecessary costs.
                </p>
              ),
            },
            {
              question: "How do you decide which AI tools a company should actually use?",
              answer: (
                <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                  I analyze your workflows, licensing costs, and team needs. Then I recommend the right mix 
                  of tools — whether it&apos;s ChatGPT, Gemini, Claude, Perplexity, or AI-powered IDEs. Often, 
                  companies overspend on licenses they don&apos;t need; I help you optimize and cut costs.
                </p>
              ),
            },
            {
              question: "What are the risks of adopting AI too fast or too slow?",
              answer: (
                <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                  Move too slow, and competitors outpace you. Move too fast, and you risk unreliable outputs, 
                  compliance issues, or wasted budgets. I help you set the right pace with a 3–6 month roadmap 
                  that aligns with your business goals and risk appetite.
                </p>
              ),
            },
            {
              question: "Can you work with developers as well as managers?",
              answer: (
                <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                  Yes. For managers, I provide clarity on strategy, risk, and cost. For developers, I give 
                  practical guidance: which model to use for debugging vs. refactoring, which IDEs accelerate 
                  prototyping, and what pitfalls to avoid in real coding environments.
                </p>
              ),
            },
            {
              question: "Do you provide ongoing support as our AI needs evolve?",
              answer: (
                <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                  Yes. I offer continuous support through check-ins, quarterly reviews, and on-demand sessions. 
                  The aim is to grow your team&apos;s internal AI competence, so you rely less on outside consulting 
                  over time.
                </p>
              ),
            },
          ]}
        />
        </section>
        <section id="contact" className="scroll-mt-28 md:scroll-mt-40">
        <CTA
          title="The companies that master AI today will define tomorrow’s market."
          description="The question is simple: will you let competitors outpace you, or seize the smarter path?"        buttons={[
          {
            text: "Call me directly",
            href: "tel:+36309392194",
            variant: "default",
          },
          {
            text: "Schedule Consultation",
            href: "#calendar",
            variant: "outline",
          },
        ]}
      />
      </section>
      </main>
      <Footer
        copyright="© 2025 Aevorex Consulting. All rights reserved."
        links={[
          { icon: <LinkedIn className="h-5 w-5" />, href: "https://linkedin.com/in/csanad-varadi" },
          { icon: <Phone className="h-4 w-4" />, text: "+36309392194", href: "tel:+36309392194" },
          { icon: <Mail className="h-4 w-4" />, text: "csanad.varadi@gmail.com", href: "mailto:csanad.varadi@gmail.com" },
        ]}
        showModeToggle={true}
      />
    </div>
  );
}
