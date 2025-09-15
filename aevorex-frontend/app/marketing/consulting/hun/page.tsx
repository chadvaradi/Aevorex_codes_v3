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
  
  import { Button } from "@/launch-ui-pro-2.3.3/ui/button";
  import { Input } from "@/launch-ui-pro-2.3.3/ui/input";
  import { Mockup, MockupFrame } from "@/launch-ui-pro-2.3.3/ui/mockup";
  import Screenshot from "@/launch-ui-pro-2.3.3/ui/screenshot";
  import Glow from "@/launch-ui-pro-2.3.3/ui/glow";
  import { Beam } from "@/launch-ui-pro-2.3.3/ui/beam";
  import { Link } from "lucide-react";
import { cn } from "@/lib/utils";
import FeatureStickyLeft from "@/launch-ui-pro-2.3.3/sections/feature/sticky-left";
import GeminiCliIllustration from "@/edited/illustrations-edited/gemini-cli";
import FeatureStickyRight from "@/launch-ui-pro-2.3.3/sections/feature/sticky-right";
import ConsultingForm from "./consulting-form";
import ChatApp from "@/edited/chat/app";
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
            { text: "Főoldal", href: "#hero" },
            { text: "Időpont foglalás", href: "#calendar" },
            { text: "Pénzügy × AI", href: "#finance" },
            { text: "Innováció × Kivitelezés", href: "#innovation" },
            { text: "AI Eszközök", href: "#bento" },
            { text: "GYIK", href: "#faq" },
            { text: "Kapcsolat", href: "#contact" },
            { text: "EN", href: "https://aevorex.com/marketing/consulting/en" },
          ]}
          actions={[
            { text: "EN", href: "https://aevorex.com/marketing/consulting/en" },
            { text: "Konzultáció foglalása", href: "#calendar", isButton: true, variant: "default" },
          ]}
        />
        <main className="flex-1">
          <section id="hero" className="scroll-mt-28 md:scroll-mt-40">
          <Hero
            title="Építs versenyelőnyt AI-stratégiával"
            description="Tanulja meg az AI-t valódi üzleti előnyként használni biztonságosan, gyorsan és mérhető eredményekkel, ahogy azt a versenytársai még nem képesek."
            illustration={<RisingSmallIllustration />}
            form={<ConsultingForm />}
          />
          </section>
          <section id="calendar" className="scroll-mt-28 md:scroll-mt-40">
          <Section className="pt-0">
            <div className="max-w-container mx-auto flex flex-col gap-6 sm:gap-10">
              <div className="text-center">
                <h2 className="text-3xl font-semibold sm:text-5xl">
                  Konzultáció Foglalása
                </h2>
                <p className="text-muted-foreground mt-2">
                  Válasszon egy {45} perces idősávot. A foglalás a Calendly felületén zárul.
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
              title="A vezető AI-platformok erejét hozzuk közelebb vállalatához."
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
              title="A vezető AI-platformok erejét hozzuk közelebb vállalatához."
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
            A feltüntetett logók a tulajdonosaik védjegyei; jelenlétük kizárólag az eszközök kompatibilitását jelzi.
          </p>
          
          <section id="finance" className="scroll-mt-28 md:scroll-mt-40">
          {/* Mobil és tablet (lg alatt) → hosszú verzió */}
          <div className="block lg:hidden">
            <FeatureStickyLeft
              title="Bocconi Pénzügy × Mesterséges Intelligencia"
              description={
                <p className="text-muted-foreground">
                  Európa egyik legjobb pénzügyi egyeteméről szerzett tapasztalatok alapján, új módon mutatom meg, hogyan lehet az AI-eszközöket magabiztosan elsajátítani és alkalmazni.
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
                  Európa egyik legjobb pénzügyi egyeteméről szerzett tapasztalatok alapján, új módon mutatom meg, hogyan lehet az AI-eszközöket magabiztosan elsajátítani és alkalmazni.
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
          <section id="innovation" className="scroll-mt-28 md:scroll-mt-40">
          {/* Mobil és tablet (lg alatt) → hosszú verzió */}
          <div className="block lg:hidden">
            <FeatureStickyRight
              title="Innovatív Megközelítés, Gyors Kivitelezés"
              description={
                <p className="text-muted-foreground">
                  Ez tette lehetővé, hogy ezt az oldalt már 2 nappal az eredeti koncepció után Ön élesben láthassa.
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
              title="Innováció × Kivitelezés"
              description={
                <p className="text-muted-foreground">
                  Ez az oldal már 2 nappal az eredeti koncepció után élesben is lehetett volna.
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
          <section id="bento" className="scroll-mt-28 md:scroll-mt-40">
          <BentoGrid
            title="Költséghatékonyan a legjobb AI-eszközökkel"
            description="A ChatGPT jó kezdet, de az áttörés akkor jön, ha megtanulja kombinálni a különböző szolgáltatók - Gemini, Claude, Perplexity, Grok és más eszközök- termékeinek erősségeit a szöveg- és kódírás, adat, tervezés és stratégia terén"
            tiles={[
              {
                title: "Professzionális ChatGPT-használat",
                description: (
                  <>
                    <p className="max-w-[320px] lg:max-w-[460px]">
                    Asszisztensből stratégiai partner.
                    Tanulja meg, hogyan alakíthatja a ChatGPT-t a munkafolyamataiba: a rutinfeladatait automatizálja, a stratégiai döntésekben használja kritikus másodvéleményként.
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
                title: "Mélyebb AI-eszközök integrálása",
                description: (
                  <p className="max-w-[460px]">
                    Tanulja meg, hogyan kommunikálhat hatékonyabban az AI-val nemcsak chaten, 
                    hanem CLI-n és integrált folyamatokon keresztül. A gép nyelvének értése 
                    erősebb kapcsolatot teremt az adatokkal és a kóddal.
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
                title: "AI-kódolás, helyesen",
                description: (
                  <p className="max-w-[460px]">
                    Az AI gyorsan ír kódot – de nem mindegy, melyik modell alkalmas 
                    refaktorálásra, hibakeresésre vagy új rendszerek építésére. Segítek a megfelelő 
                    eszköz kiválasztásában, hogy tiszta kódot és gyors eredményeket kapjon, kevesebb kockázattal.
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
                title: "Teljes AI-ökoszisztéma",
                description:
                  "A sima chatfelületek a memóriájukban erősek.  Egyes LLM-ek a refaktorban, mások a hibakeresésben tűnnek ki. Az IDE-k közül van, amelyik prototípus-előkészítésben, másik annak skálázásában erősebb. Segítek eligazodni, hogy elkerülje a felesleges köröket és a drága zsákutcákat.",
                visual: (
                  <div className="min-h-[240px] grow basis-0 sm:p-4 md:min-h-[320px] md:py-12 lg:min-h-[360px]">
                    <MockupBrowserIllustrationCursor />
                  </div>
                ),
                icon: <Cable className="text-muted-foreground size-6 stroke-1" />,
                size: "col-span-12 md:col-span-6 lg:col-span-6",
              },
              {
                title: "AI a zsebében",
                description: (
                  <p className="max-w-[460px]">
                   Alakítsa mobilját szuperaggyá: tanulja meg, hogyan használhatja az AI-alkalmazásokat 
                    ötletelésre, kutatásra vagy kreatív munkára, bárhol és bármikor.
  
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
            title="Ha elutasítja, lemarad. Ha optimista, hibát vét."
            description="Az AI bevezetése elkerülhetetlen, de a kapkodás kockázatos. Segítek megtalálni az optimális ritmust: gyors és biztonságos integrációt, amely megőrzi vállalata versenyképességét."
            visual={<RisingLargeIllustration />}
          />
          <Items
            title="AI Tanácsadási Képességek"
            items={[
              {
                title: "Eszköz Bevezetés és Képzés",
                description:
                  "Gyakorlati workshopok, amelyek bemutatják, hogyan használj hatékonyan ChatGPT, Gemini, Claude és más AI eszközöket. Promptolási taktikát és tippek a memóriáról, korlátokról és promptolásról.",
                icon: <Lock className="text-muted-foreground size-6 stroke-1" />,
              },
              {
                title: "Licence és Eszköz Stratégia",
                description:
                  "Útmutatás arról, hogy mely előfizetések mikor szükségesek. Optimalizálja a költségeket azáltal, hogy a megfelelő eszközöket a megfelelő csapatokhoz rendeli, ahelyett, hogy feleslegesen költekezne.",
                icon: <Globe className="text-muted-foreground size-6 stroke-1" />,
              },
              {
                title: "Vezetői Megállapítások",
                description:
                  "Tiszta tájékoztatás a vezetőknek: mi a hype, mi a valóság, és hol vannak a kockázatok. Lehetővé teszi a CEO-k, CFO-k és CTO-k számára, hogy tájékozott AI döntéseket hozzanak.",
                icon: (
                  <Network className="text-muted-foreground size-6 stroke-1" />
                ),
              },
              {
                title: "1:1 Munkafolyamat Mentoring",
                description:"Egyéni ülések alkalmazottakkal a napi munkafolyamataik áttekintésére. Azonosítsuk az automatizálási lehetőségeket.",
                icon: <User className="text-muted-foreground size-6 stroke-1" />,
              },
              {
                title: "AI Bevezetési Útvonal",
                description:
                  "Egy 3-6 hónapos terv a strukturált AI bevezetéshez. Biztosítja, hogy a cég elég gyorsan vezesse be, hogy versenyképes maradjon, de ne olyan gyorsan, hogy káoszt okozzon.",
                icon: (
                  <Settings className="text-muted-foreground size-6 stroke-1" />
                ),
              },
              {
                title: "Fejlesztői Támogatás",
                description:
                  "Támogatás a mérnöki csapatoknak: mely modelleket használj refaktoráláshoz, hibakereséshez vagy prototípuskészítéshez. Útmutatás AI-alapú IDE-khez, mint a Cursor, Replit vagy Windsurf.",
                icon: (
                  <Code className="text-muted-foreground size-6 stroke-1" />
                ),
              },
              {
                title: "Best Practice és Buktatók",
                description:
                  "Tudásátadás arról, hogy mi működik és mi nem. Időt takarítson meg azáltal, hogy elkerülje a gyakori AI hibákat és alkalmazza a tesztelt legjobb gyakorlatokat.",
                icon: (
                  <Database className="text-muted-foreground size-6 stroke-1" />
                ),
              },
              {
                title: "Kultúraváltás: Jobb Kérdések Feltétele",
                description:
                  "Képezzük a csapatokat, hogy az AI-t ne gyors válaszok rövidítésként használják, hanem kritikus gondolkodás partnerként. Nyisd ki az emberi szintű teljesítményt a megfelelő kérdések feltételével.",
                icon: (
                  <MessageCircle className="text-muted-foreground size-6 stroke-1" />
                ),
              },
            ]}
          />
          </section>
          
          
          <section id="faq" className="scroll-mt-28 md:scroll-mt-40">
          <FAQ
            title="Gyakran ismételt kérdések"
            items={[
              {
                question: "Miért tőlünk tanuljatok, ahelyett, hogy saját magatok kísérleteznétek?",
                answer: (
                  <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                    Mert a legtöbb csapattal ellentétben én ezt nem mellékprojektként csinálom — számomra ez szükségszerűség. 
                    A saját munkám megköveteli, hogy követjem a legújabb AI trendeket, teszteljem az új eszközöket, amint megjelennek, 
                    és mélyen megismerjem azok erősségeit és gyengeségeit. Egy vállalatban egyetlen vezető vagy alkalmazott sem rendelkezik 
                    annyi idővel, hogy ezen a szinten kutasson és kísérletezzen. Én hozom el nektek a lepárolt megállapításokat, 
                    hogy a csapatotok kihagyhassa a próbálgatásos fázist és azonnal alkalmazhassa, ami működik.
                  </p>
                ),
              },
              {
                question: "Hogyan segítetek elkerülni az AI gyakori buktatóit?",
                answer: (
                  <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                    Az AI eszközök erősek, de nem hibátlanok. Ismerem a hibamódokat — hallucinációk, 
                    inkonzisztens kimenetek és megfelelőségi kockázatok — és segítek munkafolyamatokat építeni, amelyek minimalizálják 
                    ezeket a problémákat nehéz felügyelet vagy szükségtelen költségek hozzáadása nélkül.
                  </p>
                ),
              },
              {
                question: "Hogyan döntitek el, hogy egy vállalat mely AI eszközöket használja valójában?",
                answer: (
                  <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                    Elemzem a munkafolyamataitokat, licencelési költségeket és csapat igényeket. Aztán ajánlom a megfelelő 
                    eszközkeveréket — legyen szó ChatGPT, Gemini, Claude, Perplexity vagy AI-alapú IDE-kről. Gyakran 
                    a vállalatok túlköltekeznek olyan licencekre, amelyekre nincs szükségük; segítek optimalizálni és csökkenteni a költségeket.
                  </p>
                ),
              },
              {
                question: "Mik a kockázatok az AI túl gyors vagy túl lassú bevezetésénél?",
                answer: (
                  <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                    Ha nem alkalmazkodik cége, a versenytársak leelőzik. Túl agresszív eszközhasználattal kockáztatja a megbízhatatlan kimeneteket, 
                    megfelelőségi problémákat vagy pazarló költségvetést. Segítek beállítani a megfelelő tempót egy 3-6 hónapos útvonallal, 
                    amely összhangban van az üzleti céljaiddal és kockázati hajlandóságoddal.
                  </p>
                ),
              },
              {
                question: "Dolgozhattok fejlesztőkkel és vezetőkkel is?",
                answer: (
                  <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                    Igen. A vezetőknek tisztaságot adok a stratégia, kockázat és költségek terén. A fejlesztőknek 
                    gyakorlati útmutatást adok: melyik modellt használj hibakereséshez vs. refaktoráláshoz, mely IDE-k gyorsítják 
                    a prototípuskészítést, és milyen buktatókat kerülj el valódi kódolási környezetekben.
                  </p>
                ),
              },
              {
                question: "Folyamatos támogatást nyújtotok, ahogy az AI igényeink fejlődnek?",
                answer: (
                  <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                    Igen. Folyamatos támogatást kínálok ellenőrző beszélgetéseken, negyedéves értékeléseken és igény szerinti üléseken keresztül. 
                    A cél, hogy növeld a csapatod belső AI kompetenciáját, hogy idővel kevésbé támaszkodj külső tanácsadásra.
                  </p>
                ),
              },
            ]}
          />
          </section>
          <section id="contact" className="scroll-mt-28 md:scroll-mt-40">
          <CTA
            title="Azok a vállalatok, amelyek ma mesteri szinten sajátítják el az AI-t, holnap a piacvezetők lesznek."
            description="Öné a döntés: átengedi az előnyt versenytársainak, vagy Ön választja az okosabb utat?"        buttons={[
            {
              text: "Hívjon közvetlenül",
              href: "tel:+36309392194",
              variant: "default",
            },
            {
              text: "Konzultáció Foglalása",
              href: "#calendar",
              variant: "outline",
            },
          ]}
        />
        </section>
        </main>
        <Footer
          copyright="© 2025 Aevorex Consulting. Minden jog fenntartva."
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