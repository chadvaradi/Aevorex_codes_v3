import Hero from "@/launch-ui-pro-2.3.3/sections/hero/layers";
import Navbar from "@/launch-ui-pro-2.3.3/sections/navbar/sticky";
import Image from "next/image";
import BentoGrid from "@/launch-ui-pro-2.3.3/sections/bento-grid/2-rows-bottom";
import { Carousel } from "@/launch-ui-pro-2.3.3/ui/carousel";
import CarouselSmall from "@/launch-ui-pro-2.3.3/sections/carousel/small";
import FAQ from "@/launch-ui-pro-2.3.3/sections/faq/2-cols-raised";
import Feature from "@/launch-ui-pro-2.3.3/sections/feature/mockup";
import Gallery from "@/launch-ui-pro-2.3.3/sections/gallery/default";
import Items from "@/launch-ui-pro-2.3.3/sections/items/default-brand";
import Logos from "@/launch-ui-pro-2.3.3/sections/logos/static";
import Pricing from "@/launch-ui-pro-2.3.3/sections/pricing/3-cols-subscription";
import SocialProof from "@/launch-ui-pro-2.3.3/sections/social-proof/marquee-2-rows";
import Stats from "@/launch-ui-pro-2.3.3/sections/stats/grid-boxed";
import Tabs from "@/launch-ui-pro-2.3.3/sections/tabs/bottom";
import TestimonialsCarousel from "@/launch-ui-pro-2.3.3/sections/testimonials/grid";
import CTA from "@/launch-ui-pro-2.3.3/sections/cta/beam";
import Footer from "@/launch-ui-pro-2.3.3/sections/footer/minimal";
import LaunchUI from "@/launch-ui-pro-2.3.3/logos/launch-ui";
import LinkedIn from "@/launch-ui-pro-2.3.3/logos/linkedin";
import { MousePointerClick, Shield, TextCursor, Wrench } from "lucide-react";

import RippleIllustration from "@/edited/illustrations-edited/ripple";
import ChatIllustration from "@/edited/illustrations-edited/chat";
import MockupResponsiveTopIllustration from "@/edited/illustrations-edited/mockup-responsive-top";
import RadarSmallIllustration from "@/edited/illustrations-edited/radar-small";
import { Section } from "@/launch-ui-pro-2.3.3/ui/section";
import Glow from "@/launch-ui-pro-2.3.3/ui/glow";
import { Mockup } from "@/launch-ui-pro-2.3.3/ui/mockup";
import Screenshot from "@/launch-ui-pro-2.3.3/ui/screenshot";
import Logo from "@/launch-ui-pro-2.3.3/ui/logo";
import Bocconi from "@/launch-ui-pro-2.3.3/logos/Bocconi";
import BSML from "@/launch-ui-pro-2.3.3/logos/BSML";
import BSFM from "@/launch-ui-pro-2.3.3/logos/BSFM";
import {
  Cpu,
  DollarSign,
  File as FileIcon,
  Globe,
  Linkedin,
  Lightbulb,
  Mail,
  MonitorSmartphoneIcon,
} from "lucide-react";
import { Button } from "@/launch-ui-pro-2.3.3/ui/button";
import { Input } from "@/launch-ui-pro-2.3.3/ui/input";
export default function Home() {
  return (
    <>
      <Navbar
        logo={<LaunchUI />}
        name="FinanceHub"
        homeUrl="/marketing/financehub"
        actions={[
          { text: "Login", href: "/auth/login", isButton: false },
          { text: "Join the waitlist", href: "#cta", isButton: true, variant: "default" },
        ]}
        mobileLinks={[
          { text: "Home", href: "/marketing/financehub" },
          { text: "Features", href: "/marketing/financehub#feature" },
          { text: "Waitlist", href: "#cta" }, // ÚJ
        ]}
      />
      <main>
        <section id="hero">
          <Hero
            title="WHERE FINANCIAL DATA MEETS INTELLIGENCE"
            description="Faster financial research, powered by reliable data and AI."
            buttons={[
              {
                href: "#cta",
                text: "Join the waitlist",
                variant: "default",
              },
              {
                href: "https://www.linkedin.com/company/aevorex/about/",
                text: "LinkedIn",
                variant: "glow",
                icon: <LinkedIn className="mr-2 size-4" />,
              },
            ]}
            extraContent={false}
          />
        </section>
        <section id="bento">
          <BentoGrid
            title="Meet the next era of financial research"
            description="Combining real-time market data, company filings, and alternative sources with AI — so you can make faster, sharper investment decisions."
            tiles={[
              {
                title: "Global market coverage",
                description: (
                  <>
                    <p>
                      Track stocks, sectors, and economies worldwide. From Wall Street to emerging markets.
                    </p>
                    <p>No limitations, no regional restrictions.</p>
                  </>
                ),
                visual: (
                  <div className="-mx-32 -my-16 lg:my-0">
                    <RippleIllustration />
                  </div>
                ),
                icon: <MousePointerClick className="text-muted-foreground size-8 stroke-1" />,
                size: "col-span-12 lg:col-span-4",
              },
              {
                title: "Reliable data sources",
                description: (
                  <>
                    <p>
                      From EODHD market data to FRED economic indicators and Euribor rates — all integrated into one AI-powered research hub.
                    </p>
                    <p>Exportable and audit-friendly data.</p>
                  </>
                ),
                visual: (
                  <div className="w-full sm:p-4 md:p-8">
                    <ChatIllustration />
                  </div>
                ),
                icon: <TextCursor className="text-muted-foreground size-8 stroke-1" />,
                size: "col-span-12 md:col-span-6 lg:col-span-4",
              },
              {
                title: "On your radar",
                description: (
                  <p className="max-w-[520px]">
                    Watchlists powered by AI keep the companies you care about—like Apple and NVIDIA—on your radar so you never miss the signal.
                  </p>
                ),
                visual: (
                  <div className="relative min-h-[240px]">
                    <RadarSmallIllustration className="absolute top-1/2 left-1/2 -mt-32 h-[512px] w-[512px] -translate-x-1/2 -translate-y-1/2" />
                  </div>
                ),
                icon: <Shield className="text-muted-foreground size-8 stroke-1" />,
                size: "col-span-12 md:col-span-6 lg:col-span-4",
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
                  <div className="min-h-[240px] grow basis-0 sm:p-4 md:min-h-[320px] md:py-12 lg:px-12">
                    <MockupResponsiveTopIllustration />
                  </div>
                ),
                icon: <Wrench className="text-muted-foreground size-8 stroke-1" />,
                size: "col-span-12 md:flex-row",
              },
            ]}
          />
        </section>
       {/* <section id="carousel"><CarouselSmall /></section> */}
       {/* <section id="gallery"><Gallery /></section> */}
        <section id="feature">
          <Section className="relative w-full overflow-hidden pb-0 sm:pb-0 md:pb-0">
            <div className="relative">
              <div className="max-w-container mx-auto flex flex-col items-center gap-8 sm:gap-24">
                <div className="flex flex-col items-center gap-4 text-center sm:gap-8">
                  <h1 className="max-w-[920px] text-3xl font-semibold text-balance sm:text-5xl sm:leading-tight md:text-7xl md:leading-tight">
                    Research a stock in seconds, not hours.
                  </h1>
                  <p className="text-md text-muted-foreground max-w-[620px] font-medium text-balance sm:text-xl">
                    AI-powered financial analysis designed for beginners who want information fast.
                  </p>
                </div>
                <div className="relative w-full">
                  <Mockup>
                    <Screenshot
                      srcLight="/app-light.png"
                      srcDark="/app-dark.png"
                      alt="Aevorex app screenshot"
                      width={1248}
                      height={765}
                    />
                  </Mockup>
                  <Glow variant="top" />
                </div>
              </div>
            </div>
          </Section>
        </section>
        <section id="items">
          <Items
            title="Fast results, even if you're just starting out."
            items={[
              {
                title: "AI-powered financial research",
                description:
                  "Leverage advanced AI to analyze markets and data faster than ever.",
                icon: <Cpu className="text-brand size-5 stroke-1" />,
              },
              {
                title: "AI-powered finance",
                description:
                  "Track and analyze markets with currency-level precision.",
                icon: <DollarSign className="text-brand size-5 stroke-1" />,
              },
              {
                title: "Seamless workflows",
                description:
                  "Export docs, continue in ChatGPT, or use instantly in other tools.",
                icon: <FileIcon className="text-brand size-5 stroke-1" />,
              },
              {
                title: "Global insights",
                description:
                  "Made for worldwide coverage and emerging markets.",
                icon: <Globe className="text-brand size-5 stroke-1" />,
              },
              {
                title: "Early network expansion",
                description:
                  "Build your connections among students and professionals to grow faster.",
                icon: <Linkedin className="text-brand size-5 stroke-1" />,
              },
              {
                title: "Research smarter",
                description:
                  "Turn raw data into sharper insights and actionable intelligence.",
                icon: <Lightbulb className="text-brand size-5 stroke-1" />,
              },
              {
                title: "Stay connected",
                description:
                  "Email alerts, market newsletters, and updates in real time.",
                icon: <Mail className="text-brand size-5 stroke-1" />,
              },
              {
                title: "Mobile-ready design",
                description:
                  "Optimized for seamless use on both smartphones and laptops.",
                icon: (
                  <MonitorSmartphoneIcon className="text-brand size-5 stroke-1" />
                ),
              },
            ]}
          />
        </section>
        <section id="logos">
          <Logos
            title="Inspired by the communities we're part of"
            logos={[
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
            ]}
          />
        </section>
       {/* <section id="social-proof"><SocialProof /></section> */}
       {/* <section id="stats"><Stats /></section> */}
       {/* <section id="tabs"><Tabs /></section> */}
       {/* <section id="testimonials"><TestimonialsCarousel /></section> */} 
       {/* <section id="pricing"><Pricing /></section> */}
       <section id="faq">
          <FAQ
            title="Questions and Answers"
            items={[
              {
                question: "What is Aevorex?",
                answer: (
                  <>
                    <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                      An AI-powered financial research and analysis platform that makes markets easier to understand by turning raw data into clear, actionable insights.
                    </p>
                  </>
                ),
              },
              {
                question: "Who is it for?",
                answer: (
                  <>
                    <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                      Students, junior analysts, and professionals who need fast, reliable insights without relying on expensive or overly complex tools.
                    </p>
                  </>
                ),
              },
              {
                question: "How is it different from traditional platforms?",
                answer: (
                  <>
                    <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                      Most financial platforms are either too complicated or too expensive. Aevorex is lightweight, AI-driven, mobile-friendly, and delivers results in seconds instead of hours.
                    </p>
                  </>
                ),
              },
              {
                question: "Do I need a financial background to use it?",
                answer: (
                  <>
                    <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                      Not at all. Aevorex is designed to be accessible: it explains indicators and results in plain language so you can learn while you analyze.
                    </p>
                  </>
                ),
              },
              {
                question: "How reliable are the AI-generated insights?",
                answer: (
                  <>
                    <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                      Aevorex uses multiple data sources and transparent methodologies. The AI doesn&apos;t make predictions — it accelerates research, highlights patterns, and saves time.
                    </p>
                  </>
                ),
              },
              {
                question: "Can I use it on my phone?",
                answer: (
                  <>
                    <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                      Yes. Aevorex is fully responsive, so it works seamlessly on laptops, tablets, and smartphones.
                    </p>
                  </>
                ),
              },
              {
                question: "Is there a free version?",
                answer: (
                  <>
                    <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                      Yes. Students and early testers can access the core features for free. Premium plans unlock advanced indicators, AI-driven reports, and deeper analytics.
                    </p>
                  </>
                ),
              },
              {
                question: "What about communities like Bocconi?",
                answer: (
                  <>
                    <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                      Aevorex is inspired by student and professional communities. It aims to connect people who want to grow together through AI-driven financial research.
                    </p>
                  </>
                ),
              },
            ]}
          />
        </section>
        <section id="cta">
          <Section className="relative w-full overflow-hidden">
            <div className="max-w-container relative z-10 mx-auto flex flex-col items-center gap-6 text-center sm:gap-10">
              <h2 className="text-3xl font-semibold sm:text-5xl">
              Subscribe to the waitlist
              </h2>
              <p className="text-muted-foreground">
                Join now to get early access to Aevorex
              </p>
              <div className="relative z-1 flex flex-col items-center gap-4 self-stretch">
                <form className="flex w-full max-w-[420px] gap-2">
                  <Input
                    type="email"
                    placeholder="Email address"
                    className="border-border/10 bg-foreground/10 grow"
                  />
                  <Button variant="default" size="lg" asChild>
                    <a href="#">Join waitlist</a>
                  </Button>
                </form>
                <p className="text-muted-foreground text-xs">
                  No spam. Just early access updates.
                </p>
              </div>
              <Glow
                variant="center"
                className="scale-y-[50%] opacity-60 sm:scale-y-[35%] md:scale-y-[45%]"
              />
            </div>
          </Section>

        </section>
      </main>
      <Footer />
    </>
  );
}
