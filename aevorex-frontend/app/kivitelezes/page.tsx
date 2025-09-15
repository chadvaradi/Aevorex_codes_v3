// /app/kivitelezes/page.tsx

import { Section } from "@/launch-ui-pro-2.3.3/ui/section";
import Navbar from "@/launch-ui-pro-2.3.3/sections/navbar/barebone";
import Hero from "@/launch-ui-pro-2.3.3/sections/hero/default";
import Logos from "@/launch-ui-pro-2.3.3/sections/logos/grid-6";
import Feature from "@/launch-ui-pro-2.3.3/sections/feature/sticky-left";
import Stats from "@/launch-ui-pro-2.3.3/sections/stats/grid-boxed";
import Gallery from "@/launch-ui-pro-2.3.3/sections/gallery/subsections";
import Carousel from "@/launch-ui-pro-2.3.3/sections/carousel/external";

import Cta from "@/launch-ui-pro-2.3.3/sections/cta/beam";
import Faq from "@/launch-ui-pro-2.3.3/sections/faq/2-cols";
import Footer from "@/launch-ui-pro-2.3.3/sections/footer/default";
import { ArrowRight } from "lucide-react";
import type { ReactNode } from "react"; 
import Screenshot from "@/launch-ui-pro-2.3.3/ui/screenshot";
import { Button } from "@/launch-ui-pro-2.3.3/ui/button";
import { Input } from "@/launch-ui-pro-2.3.3/ui/input";
import Glow from "@/launch-ui-pro-2.3.3/ui/glow";

export default function KivitelezesPage() {
    return (
        <div
      className="flex flex-col"
      style={
        {
          "--brand-foreground": "var(--brand-emerald-foreground)",
          "--brand": "var(--brand-emerald)",
          "--primary": "light-dark(var(--brand-emerald), oklch(0.985 0 0))",
          "--background": "var(--background-emerald)",
          "--muted": "var(--background-emerald)",
          "--radius": "1rem",
        } as React.CSSProperties
      }
    >
        <Navbar
            logo={null}
            name="Konzolep"
            homeUrl="/kivitelezes"
            mobileLinks={[
                { text: "Rólunk", href: "/rolunk" },
                { text: "Szolgáltatások", href: "/szolgaltatasok" },
                { text: "Referenciák", href: "/referenciak" },
                { text: "Kapcsolat", href: "/kapcsolat" },
                { text: "Ajánlatkérés", href: "/ajanlatkeres" },
            ]}
            actions={[
                { text: "Rólunk", href: "/rolunk" },
                { text: "Szolgáltatások", href: "/szolgaltatasok" },
                { text: "Referenciák", href: "/referenciak" },
                { text: "Kapcsolat", href: "/kapcsolat" },
                {
                text: "Ajánlatkérés",
                href: "/ajanlatkeres",
                isButton: true,
                variant: "default",
                iconRight: <ArrowRight className="ml-1 h-4 w-4" />,
                },
            ]}
            />
        <Hero
            title="Mérnöki szakszerűség Budapest jövőjéért"
            description="A Budapest Közút Zrt. Mérnök Igazgatósága évtizedes tapasztalattal, kamarai jogosultságok teljes körével és díjnyertes projektek sorával biztosítja a nagyberuházások, közlekedési és városi fejlesztések magas szintű műszaki ellenőrzését és lebonyolítását – a tervezéstől a kivitelezésig, a fenntartási időszak végéig."
            buttons={[
                {
                href: "/referenciak",
                text: "Tekintse meg referenciáinkat",
                variant: "default",
                },
                {
                href: "/kapcsolat",
                text: "Lépjen kapcsolatba velünk",
                variant: "glow",
                },
            ]}
            mockup={
                <Screenshot
                    srcLight="/kivitelezes/Picture20.jpg"
                    srcDark="/kivitelezes/Picture20.jpg"
                    alt="Kivitelezési projekt"
                    width={1248}
                    height={765}
                    className="w-full object-cover rounded-2xl"
                    />
            }
            badge={false}
            />
      <Feature
            title="Mérnöki szakszerűség minden részletben"
            description={
                <>
                <p>
                    Minden projektünkben elsődleges szempont a fenntarthatóság, a biztonság és a közérdek. 
                    A tervezéstől a kivitelezésig, a fenntartási időszak végéig biztosítjuk 
                    a beruházások hosszú távú értékét.
                </p>
                </>
            }
            visual={
                <img
                src="/kivitelezes/Picture5.jpg"
                alt="Építészeti részlet"
                className="rounded-2xl border border-gray-200 shadow-md w-[500px] object-cover"
                />
            }
        />
        <Stats
        title="Évtizedes tapasztalat"
        description="Mérnöki szakszerűség és díjnyertes projektek a tervezéstől a kivitelezésig."
        items={[
            {
            label: "",
            value: 20,
            suffix: "+",
            description: " tapasztalat nagyberuházások mérnöki ellenőrzésében és lebonyolításában",
            },
            {
            label: "",
            value: 100,
            suffix: "+",
            description: "városi és országos közlekedési, híd- és útépítési beruházás",
            },
            {
            label: "",
            value: 10,
            suffix: "+",
            description: "építőipari és mérnöki nívódíj az elmúlt évtizedekben",
            },
            {
            label: "",
            value: 50,
            suffix: "+",
            description: "városi fejlesztés, metró- és hídrekonstrukció országszerte",
            },
        ]}
        />
        <Gallery
        title="Projektek, amelyekre büszkék vagyunk"
        description="A Lánchídtól a Blaha Lujza térig – számos ikonikus fejlesztésben vettünk részt a tervezéstől a kivitelezésig."
        sections={[
            {
            title: "Kiemelt projekt",
            description: "Egyetlen referencia – próba galéria.",
            items: [
                {
                title: "Lánchíd felújítása",
                description: "Dilatációcsere és szerkezeti munkák.",
                // link opcionális; ha nem kell, töröld
                link: { url: "/referenciak/lanchid" },
                visual: (
                    <img
                    src="/kivitelezes/Picture1.jpg"
                    alt="Lánchíd felújítása"
                    width={500}
                    height={300}
                    className="w-full h-[300px] object-cover rounded-xl"
                    />
                ),
                },
                {
                    title: "Alagút rekonstrukció",
                    description: "Betonburkolat és vízszigetelés cseréje.",
                    // link opcionális; ha nem kell, töröld
                    link: { url: "/referenciak/lanchid" },
                    visual: (
                        <img
                        src="/kivitelezes/Picture2.jpg"
                        alt="Alagút rekonstrukció"
                        width={500}
                        height={300}
                        className="w-full h-[300px] object-cover rounded-xl"
                        />
                    ),
                    },
                    {
                        title: "Pályaszerkezet felújítás",
                        description: "Vasbeton és sínrögzítési munkák.",
                        // link opcionális; ha nem kell, töröld
                        link: { url: "/referenciak/lanchid" },
                        visual: (
                            <img
                            src="/kivitelezes/Picture3.jpg"
                            alt="Pályaszerkezet felújítás"
                            width={500}
                            height={300}
                            className="w-full h-[300px] object-cover rounded-xl"
                            />
                        ),
                        },
                        {
                            title: "Szakmai csapat",
                            description: "Mérnöki és kivitelezői együttműködés.",
                            // link opcionális; ha nem kell, töröld
                            link: { url: "/referenciak/lanchid" },
                            visual: (
                                <img
                                src="/kivitelezes/Picture4.jpg"
                                alt="Szakmai csapat"
                                width={500}
                                height={300}
                                className="w-full h-[300px] object-cover rounded-xl"
                                />
                            ),
                            },
                            {
                                title: "Műemlék épület",
                                description: "Restaurálási és belsőépítészeti munkák.",
                                // link opcionális; ha nem kell, töröld
                                link: { url: "/referenciak/lanchid" },
                                visual: (
                                    <img
                                    src="/kivitelezes/Picture5.jpg"
                                    alt="Műemlék épület"
                                    width={500}
                                    height={300}
                                    className="w-full h-[300px] object-cover rounded-xl"
                                    />
                                ),
                                },
                                {
                                    title: "Híd felújítása",
                                    description: "Szerkezeti erősítés és burkolatcsere.",
                                    // link opcionális; ha nem kell, töröld
                                    link: { url: "/referenciak/lanchid" },
                                    visual: (
                                        <img
                                        src="/kivitelezes/Picture6.jpg"
                                        alt="Híd felújítása"
                                        width={500}
                                        height={300}
                                        className="w-full h-[300px] object-cover rounded-xl"
                                        />
                                    ),
                                    },
                                    {
                                        title: "Akadálymentesítés",
                                        description: "Rámpák és liftek kialakítása.",
                                        // link opcionális; ha nem kell, töröld
                                        link: { url: "/referenciak/lanchid" },
                                        visual: (
                                            <img
                                            src="/kivitelezes/Picture7.jpg"
                                            alt="Akadálymentesítés"
                                            width={500}
                                            height={300}
                                            className="w-full h-[300px] object-cover rounded-xl"
                                            />
                                        ),
                                        },
                                        {
                                            title: "Metró állomás",
                                            description: "Pálya- és szerkezeti beavatkozások.",
                                            // link opcionális; ha nem kell, töröld
                                            link: { url: "/referenciak/lanchid" },
                                            visual: (
                                                <img
                                                src="/kivitelezes/Picture8.jpg"
                                                alt="Metró állomás"
                                                width={500}
                                                height={300}
                                                className="w-full h-[300px] object-cover rounded-xl"
                                                />
                                            ),
                                            },
                                            {
                                                title: "Városi csomópont",
                                                description: "Forgalomtechnikai és szerkezeti fejlesztés.",
                                                // link opcionális; ha nem kell, töröld
                                                link: { url: "/referenciak/lanchid" },
                                                visual: (
                                                    <img
                                                    src="/kivitelezes/Picture9.jpg"
                                                    alt="Városi csomópont"
                                                    width={500}
                                                    height={300}
                                                    className="w-full h-[300px] object-cover rounded-xl"
                                                    />
                                                ),
                                                },
                                                {
                                                    title: "Alagútépítés",
                                                    description: "Gépi kivitelezés és betonozás.",
                                                    // link opcionális; ha nem kell, töröld
                                                    link: { url: "/referenciak/lanchid" },
                                                    visual: (
                                                        <img
                                                        src="/kivitelezes/Picture10.jpg"
                                                        alt="Alagútépítés"
                                                        width={500}
                                                        height={300}
                                                        className="w-full h-[300px] object-cover rounded-xl"
                                                        />
                                                    ),
                                                    },
                                                    {
                                                        title: "Szerkezetépítés",
                                                        description: "Vasbeton födémek kivitelezése.",
                                                        // link opcionális; ha nem kell, töröld
                                                        link: { url: "/referenciak/lanchid" },
                                                        visual: (
                                                            <img
                                                            src="/kivitelezes/Picture11.jpg"
                                                            alt="Szerkezetépítés"
                                                            width={500}
                                                            height={300}
                                                            className="w-full h-[300px] object-cover rounded-xl"
                                                            />
                                                        ),
                                                        },
                                                        {
                                                            title: "Gépház rekonstrukció",
                                                            description: "Szellőztető és gépészeti berendezések felújítása.",
                                                            // link opcionális; ha nem kell, töröld
                                                            link: { url: "/referenciak/lanchid" },
                                                            visual: (
                                                                <img
                                                                src="/kivitelezes/Picture12.jpg"
                                                                alt="Gépház rekonstrukció"
                                                                width={500}
                                                                height={300}
                                                                className="w-full h-[300px] object-cover rounded-xl"
                                                                />
                                                            ),
                                                            },
                                                            {
                                                                title: "Közlekedési alagút",
                                                                description: "Burkolatcsere és szigetelés.",
                                                                // link opcionális; ha nem kell, töröld
                                                                link: { url: "/referenciak/lanchid" },
                                                                visual: (
                                                                    <img
                                                                    src="/kivitelezes/Picture13.jpg"
                                                                    alt="Közlekedési alagút"
                                                                    width={500}
                                                                    height={300}
                                                                    className="w-full h-[300px] object-cover rounded-xl"
                                                                    />
                                                                ),
                                                                },
                                                                {
                                                                    title: "Kábelcsatorna felújítás",
                                                                    description: "Elektromos és közművezetékek rendezése.",
                                                                    // link opcionális; ha nem kell, töröld
                                                                    link: { url: "/referenciak/lanchid" },
                                                                    visual: (
                                                                        <img
                                                                        src="/kivitelezes/Picture14.jpg"
                                                                        alt="Kábelcsatorna felújítás"
                                                                        width={500}
                                                                        height={300}
                                                                        className="w-full h-[300px] object-cover rounded-xl"
                                                                        />
                                                                    ),
                                                                    },
                                                                    {
                                                                        title: "Álmennyezet szerelés",
                                                                        description: "Modern belsőépítészeti munkák.",
                                                                        // link opcionális; ha nem kell, töröld
                                                                        link: { url: "/referenciak/lanchid" },
                                                                        visual: (
                                                                            <img
                                                                            src="/kivitelezes/Picture15.jpg"
                                                                            alt="Álmennyezet szerelés"
                                                                            width={500}
                                                                            height={300}
                                                                            className="w-full h-[300px] object-cover rounded-xl"
                                                                            />
                                                                        ),
                                                                        },
                                                                        {
                                                                            title: "Gépészeti központ",
                                                                            description: "Villamos és gépészeti berendezések kiépítése.",
                                                                            // link opcionális; ha nem kell, töröld
                                                                            link: { url: "/referenciak/lanchid" },
                                                                            visual: (
                                                                                <img
                                                                                src="/kivitelezes/Picture16.jpg"
                                                                                alt="Gépészeti központ"
                                                                                width={500}
                                                                                height={300}
                                                                                className="w-full h-[300px] object-cover rounded-xl"
                                                                                />
                                                                            ),
                                                                            },
                                                                            {
                                                                                title: "Vasúti alagút",
                                                                                description: "Pálya és szellőzőrendszer korszerűsítése.",
                                                                                // link opcionális; ha nem kell, töröld
                                                                                link: { url: "/referenciak/lanchid" },
                                                                                visual: (
                                                                                    <img
                                                                                    src="/kivitelezes/Picture17.jpg"
                                                                                    alt="Vasúti alagút"
                                                                                    width={500}
                                                                                    height={300}
                                                                                    className="w-full h-[300px] object-cover rounded-xl"
                                                                                    />
                                                                                ),
                                                                                },
                                                                                {
                                                                                    title: "Nagyfeszültségű berendezések",
                                                                                    description: "Erősáramú kábelek és transzformátorok.",
                                                                                    // link opcionális; ha nem kell, töröld
                                                                                    link: { url: "/referenciak/lanchid" },
                                                                                    visual: (
                                                                                        <img
                                                                                        src="/kivitelezes/Picture18.jpg"
                                                                                        alt="Nagyfeszültségű berendezések"
                                                                                        width={500}
                                                                                        height={300}
                                                                                        className="w-full h-[300px] object-cover rounded-xl"
                                                                                        />
                                                                                    ),
                                                                                    },
                                                                                    {
                                                                                        title: "Közműalagút",
                                                                                        description: "Vezetékrendszerek és szigetelések.",
                                                                                        // link opcionális; ha nem kell, töröld
                                                                                        link: { url: "/referenciak/lanchid" },
                                                                                        visual: (
                                                                                            <img
                                                                                            src="/kivitelezes/Picture19.jpg"
                                                                                            alt="Közműalagút"
                                                                                            width={500}
                                                                                            height={300}
                                                                                            className="w-full h-[300px] object-cover rounded-xl"
                                                                                            />
                                                                                        ),
                                                                                        },
                                                                                        {
                                                                                            title: "Városi beruházás",
                                                                                            description: "Út- és hídrekonstrukciós projekt.",
                                                                                            // link opcionális; ha nem kell, töröld
                                                                                            link: { url: "/referenciak/lanchid" },
                                                                                            visual: (
                                                                                                <img
                                                                                                src="/kivitelezes/Picture20.jpg"
                                                                                                alt="Városi beruházás"
                                                                                                width={500}
                                                                                                height={300}
                                                                                                className="w-full h-[300px] object-cover rounded-xl"
                                                                                                />
                                                                                            ),
                                                                                            },
                            
                            
            ],
            },
        ]}
        />
        <Faq
  title="Gyakran Ismételt Kérdések"
  items={[
    {
      question: "Milyen típusú projekteket vállalnak?",
      answer: (
        <>
          <p className="text-muted-foreground mb-4 max-w-[640px]">
            Híd-, út-, alagút- és közműépítési beruházások, városi
            közlekedési létesítmények, peron- és csomópont-felújítások,
            akadálymentesítések, valamint komplex műszaki ellenőrzési
            és lebonyolítási feladatok.
          </p>
        </>
      ),
    },
    {
      question: "Mekkora tapasztalattal rendelkeznek?",
      answer: (
        <>
          <p className="text-muted-foreground mb-4 max-w-[640px]">
            Több mint <strong>20 év</strong> mérnöki és projektlebonyolítói
            tapasztalat, országos és fővárosi nagyberuházásokon, díjnyertes
            referenciákkal.
          </p>
        </>
      ),
    },
    {
      question: "Hogyan biztosítják a minőséget és a jogszerűséget?",
      answer: (
        <>
          <p className="text-muted-foreground mb-4 max-w-[640px]">
            Kamarai jogosultságokkal rendelkező szakemberekkel,
            átlátható szerződésmenedzsmenttel, FIDIC-gyakorlat alapján,
            szigorú minőségellenőrzési és dokumentációs eljárásokkal.
          </p>
        </>
      ),
    },
    {
      question: "Vállalnak műszaki ellenőrzést és beruházáslebonyolítást is?",
      answer: (
        <>
          <p className="text-muted-foreground mb-4 max-w-[640px]">
            Igen. Teljes körű műszaki ellenőrzést, mérnöki szolgáltatást és
            projektlebonyolítást végzünk a tervezéstől a kivitelezésen át a
            jótállási időszak végéig.
          </p>
        </>
      ),
    },
    {
      question: "Milyen szerepük van az akadálymentesítésben?",
      answer: (
        <>
          <p className="text-muted-foreground mb-4 max-w-[640px]">
            Felvonók, taktilis jelzések, rámpák, peron- és csomóponti
            megoldások tervezésének és kivitelezésének ellenőrzése az
            MSZ EN 81-70 és kapcsolódó szabványok szerint.
          </p>
        </>
      ),
    },
    {
      question: "Hogyan kezelik a kockázatokat és az ütemezést?",
      answer: (
        <>
          <p className="text-muted-foreground mb-4 max-w-[640px]">
            Kockázati mátrix, ütemterv-kontroll (kritikus út), rendszeres
            helyszíni kooperációk és költség-/határidő-követés alapján,
            döntéstámogató riportokkal.
          </p>
        </>
      ),
    },
    {
      question: "Tudnak-e segíteni közbeszerzésben és ár-/szerződésmenedzsmentben?",
      answer: (
        <>
          <p className="text-muted-foreground mb-4 max-w-[640px]">
            Igen. Műszaki tartalom ellenőrzése, árazás és költségvetés
            felülvizsgálata, ajánlatok bírálata, szerződéses kockázatok
            kezelése, változás- és többletigények kezelése.
          </p>
        </>
      ),
    },
    {
      question: "Hogyan kérhetek ajánlatot?",
      answer: (
        <>
          <p className="text-muted-foreground mb-4 max-w-[640px]">
            Az <strong>Ajánlatkérés</strong> menüpont űrlapján vagy a
            „Kapcsolat” oldalon található elérhetőségeken. Rövid projektleírás,
            helyszín, ütemezés és elvárt feladatkör megadását kérjük.
          </p>
        </>
      ),
    },
  ]}
/>
<section id="cta">
  <Section className="relative w-full overflow-hidden">
    <div className="max-w-container relative z-10 mx-auto flex flex-col items-center gap-6 text-center sm:gap-10">
      <h2 className="text-3xl font-semibold sm:text-5xl">
        Kérjen ajánlatot mérnöki szakértelemmel
      </h2>
      <p className="text-muted-foreground">
        Kérjen ajánlatot tapasztalt mérnökcsapatunktól.
      </p>
      <div className="relative z-1 flex flex-col items-center gap-4 self-stretch">
        <form className="flex w-full max-w-[420px] gap-2">
          <Input
            type="email"
            placeholder="Email cím"
            className="border-border/10 bg-foreground/10 grow"
          />
          <Button variant="default" size="lg" asChild>
            <a href="/kapcsolat">Kapcsolatfelvétel</a>
          </Button>
        </form>
      </div>
      <Glow
        variant="center"
        className="scale-y-[50%] opacity-60 sm:scale-y-[35%] md:scale-y-[45%]"
      />
    </div>
  </Section>
</section>
        {/* --- Footer --- */}
<Footer
  name="Konzolep"
  logo={
    <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-foreground/10 text-sm font-bold">
      K
    </span>
  }
  columns={[
    {
      title: "Szolgáltatások",
      links: [
        { text: "Mérnöki ellenőrzés", href: "/szolgaltatasok" },
        { text: "Beruházáslebonyolítás", href: "/szolgaltatasok" },
        { text: "Projektmenedzsment", href: "/szolgaltatasok" },
      ],
    },
    {
      title: "Cégünkről",
      links: [
        { text: "Rólunk", href: "/rolunk" },
        { text: "Referenciák", href: "/referenciak" },
        { text: "Kapcsolat", href: "/kapcsolat" },
      ],
    },
    {
      title: "Kapcsolat",
      links: [
        { text: "info@konzolep.hu", href: "mailto:info@konzolep.hu" },
        { text: "+36 1 234 5678", href: "tel:+3612345678" },
        { text: "Ajánlatkérés", href: "/ajanlatkeres" },
      ],
    },
  ]}
  copyright="© 2025 Konzolep. Minden jog fenntartva."
  policies={[
    { text: "Adatkezelési tájékoztató", href: "/adatvedelem" },
    { text: "Felhasználási feltételek", href: "/aszf" },
  ]}
  showModeToggle={true}
/>
      </div>
    );
  }