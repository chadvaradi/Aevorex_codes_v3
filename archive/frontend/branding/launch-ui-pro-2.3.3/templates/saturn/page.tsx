import {
  ArrowRight,
  CalendarClockIcon,
  GlobeIcon,
  CommandIcon,
  LanguagesIcon,
  CalendarDaysIcon,
  CalendarRangeIcon,
  XCircleIcon,
  SmartphoneIcon,
  CalendarIcon,
  Users,
  Building,
} from "lucide-react";

import Navbar from "../../sections/navbar/centered";
import Hero from "../../sections/hero/default";
import Calendar from "../calendar/app";
import Logos from "../../sections/logos/default";
import Items from "../../sections/items/default-brand";
import Pricing from "../../sections/pricing/3-cols-subscription";
import FAQ from "../../sections/faq/default";
import CTA from "../../sections/cta/default";
import Footer from "../../sections/footer/default";
import Logo from "../../ui/logo";
import Notion from "../../logos/notion";
import Meet from "../../logos/meet";
import Github from "../../logos/github";
import Zoom from "../../logos/zoom";
import SaturnLogo from "../../logos/saturn";
import Navigation from "../../ui/navigation";
import BentoGrid from "../../sections/bento-grid/3-rows-top";
import TabsTop from "../../sections/tabs/top";
import SocialProof from "../../sections/social-proof/marquee-2-rows";
import RadarSmallIllustration from "../../illustrations/radar-small";
import MockupMobileIllustration from "../../illustrations/mockup-mobile";
import CodeEditorIllustration from "../../illustrations/code-editor";
import GlobeIllustration from "../../illustrations/globe";
import ChatIllustration from "../../illustrations/chat";
import CarouselSmall from "../../sections/carousel/small";
import Screenshot from "../../ui/screenshot";

function Saturn() {
  return (
    <div
      className="() flex flex-col"
      style={
        {
          "--brand-foreground": "var(--brand-fire-foreground)",
          "--brand": "var(--brand-fire)",
          "--primary": "light-dark(var(--brand-fire), oklch(0.985 0 0))",
          "--background": "var(--background-fire)",
          "--muted": "var(--background-fire)",
          "--radius": "var(--radius-default)",
        } as React.CSSProperties
      }
    >
      <Navbar
        logo={<SaturnLogo />}
        name="Saturn"
        homeUrl="/"
        mobileLinks={[
          { text: "Features", href: "/" },
          { text: "Pricing", href: "/" },
          { text: "Resources", href: "/" },
          { text: "About", href: "/" },
        ]}
        actions={[
          { text: "Sign in", href: "/", isButton: false },
          {
            text: "Get Started",
            href: "/",
            isButton: true,
            variant: "default",
          },
        ]}
        customNavigation={
          <Navigation
            logo={<SaturnLogo />}
            logoTitle="Saturn"
            logoDescription="The ultimate calendar app for you and your team. Seamlessly integrate with your favorite tools."
            menuItems={[
              {
                title: "Features",
                content: "default",
              },
              {
                title: "Resources",
                content: "components",
              },
              {
                title: "About",
                isLink: true,
                href: "/",
              },
              {
                title: "Pricing",
                isLink: true,
                href: "/",
              },
            ]}
            introItems={[
              {
                title: "For individuals",
                href: "/",
                description:
                  "Manage your personal schedule with our intuitive calendar interface.",
              },
              {
                title: "For teams",
                href: "/",
                description:
                  "Coordinate schedules and meetings across your entire organization.",
              },
              {
                title: "For enterprises",
                href: "/",
                description:
                  "Custom solutions for large organizations with advanced security needs.",
              },
            ]}
            components={[
              {
                title: "Documentation",
                href: "/",
                description:
                  "Comprehensive guides to help you get the most out of Saturn Calendar.",
              },
              {
                title: "API Reference",
                href: "/",
                description:
                  "Integrate Saturn Calendar with your own applications and services.",
              },
              {
                title: "Tutorials",
                href: "/",
                description:
                  "Step-by-step guides for common tasks and advanced features.",
              },
              {
                title: "Blog",
                href: "/",
                description:
                  "Latest news, tips, and best practices for calendar management.",
              },
              {
                title: "Community",
                href: "/",
                description:
                  "Join our community of users to share ideas and get help.",
              },
              {
                title: "Support",
                href: "/",
                description:
                  "Get help from our team of experts whenever you need it.",
              },
            ]}
          />
        }
      />
      <Hero
        badge={false}
        title="The ultimate calendar for you and your team"
        description="All your events, tasks and commitments in one simple calendar app. Easy to use and packed with features. It also looks good."
        mockup={<Calendar />}
        buttons={[
          {
            href: "/",
            text: "Get Started",
            variant: "default",
            iconRight: <ArrowRight className="ml-2 size-4" />,
          },
          {
            href: "/",
            text: "Contact sales",
            variant: "glow",
          },
        ]}
      />
      <Logos
        badge={false}
        title="Works with all your favorite tools"
        logos={[
          <Logo key="meet" image={Meet} name="Google Meet" />,
          <Logo key="notion" image={Notion} name="Notion" />,
          <Logo key="github" image={Github} name="Github" />,
          <Logo key="zoom" image={Zoom} name="Zoom" />,
        ]}
      />
      <CarouselSmall
        title="Everything you need from a perfect calendar app"
        description="Saturn Calendar is a modern and intuitive calendar app that makes it easy to manage your schedule and stay on top of your commitments."
        slides={[
          {
            tagline: "Integrated AI",
            title: "Intelligent scheduling",
            description:
              "Saturn Calendar uses AI to suggest the best times for your meetings and events.",
            image: (
              <Screenshot
                srcLight="/app-settings-light.png"
                srcDark="/app-settings-dark.png"
                alt="Navbars"
                width={900}
                height={600}
              />
            ),
          },
          {
            tagline: "Seamless syncing",
            title: "Sync all your calendars",
            description:
              "Saturn Calendar integrates with all your calendars, including Google Calendar, Outlook, and iCloud.",
            image: (
              <Screenshot
                srcLight="/app-mail-light.png"
                srcDark="/app-mail-dark.png"
                alt="Bento grids"
                width={900}
                height={600}
              />
            ),
          },
          {
            tagline: "Team collaboration",
            title: "Collaborate with your team",
            description:
              "Saturn Calendar allows you to collaborate with your team on your schedule.",
            image: (
              <Screenshot
                srcLight="/app-light.png"
                srcDark="/app-dark.png"
                alt="Hero sections"
                width={900}
                height={600}
              />
            ),
          },
          {
            tagline: "Mobile-first",
            title: "Start with the right impression",
            description:
              "Optimized to look and feel great on all devices, including mobile, tablet and desktop.",
            image: (
              <Screenshot
                srcLight="/app-settings-light.png"
                srcDark="/app-settings-dark.png"
                alt="Navbars"
                width={900}
                height={600}
              />
            ),
          },
        ]}
      />

      <BentoGrid
        title="Finally, a calendar experience done right."
        description="Saturn Calendar is a modern and intuitive calendar app that makes it easy to manage your schedule and stay on top of your commitments."
        tiles={[
          {
            title: "Mobile-first",
            description: (
              <p>
                Optimized to look and feel great on all devices, including
                mobile, tablet and desktop.
              </p>
            ),
            visual: (
              <div className="min-h-[300px] w-full py-12">
                <MockupMobileIllustration />
              </div>
            ),
            size: "col-span-12 md:col-span-6 lg:col-span-5",
          },
          {
            title: "Connect to all your calendars at once",
            description: (
              <>
                <p className="max-w-[460px]">
                  Integrate your landing page directly in the product and forget
                  about multiple codebases and unnecessary APIs.
                </p>
                <p>No extra dependencies, no extra maintenance.</p>
              </>
            ),
            visual: (
              <div className="mt-12 -mb-48 flex w-full grow items-center justify-center self-center">
                <RadarSmallIllustration className="max-w-[480px]" />
              </div>
            ),
            size: "col-span-12 md:col-span-6 lg:col-span-7",
          },
          {
            title: "Stay on top of your schedule",
            description: (
              <p className="max-w-[460px]">
                With Saturn Calendar, you&apos;ll never miss an important
                meeting or appointment again.
              </p>
            ),
            visual: (
              <div className="min-h-[240px] w-full grow items-center self-center px-4 lg:px-12">
                <CodeEditorIllustration />
              </div>
            ),
            size: "col-span-12 md:col-span-6 lg:col-span-7",
          },
          {
            title: "Support for multiple time zones",
            description:
              "Easily manage and visualize schedules across different time zones.",
            visual: (
              <div className="-mb-[96px] sm:-mb-[186px] md:-mx-32">
                <GlobeIllustration className="[&_svg]:h-[100%] [&_svg]:w-[100%]" />
              </div>
            ),
            size: "col-span-12 md:col-span-6 lg:col-span-5",
          },
          {
            title: "Team centric",
            description: (
              <>
                <p>
                  Saturn Calendar is designed to work seamlessly with your team.
                </p>
                <p>
                  Easily add your team members to collaborate in real-time on
                  shared calendars and events.
                </p>
              </>
            ),
            visual: (
              <div className="w-full sm:p-4 md:p-8">
                <ChatIllustration />
              </div>
            ),
            size: "col-span-12 md:col-span-6 lg:col-span-5",
          },
          {
            title: "Smart conflict prevention",
            description: (
              <p className="max-w-[460px]">
                Automatically blocks busy time slots across all your connected
                calendars.
              </p>
            ),
            visual: (
              <div className="min-h-[240px] w-full grow items-center self-center px-4 lg:px-12">
                <CodeEditorIllustration />
              </div>
            ),
            size: "col-span-12 md:col-span-6 lg:col-span-7",
          },
        ]}
      />
      <Items
        title="Everything you need in one calendar app"
        items={[
          {
            title: "Built-in scheduling",
            description:
              "Share your availability and let others book time with you without switching apps",
            icon: <CalendarClockIcon className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Global time zone support",
            description:
              "Collaborate seamlessly with teams worldwide by visualizing schedules across time zones",
            icon: <GlobeIcon className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Efficient interface",
            description:
              "Navigate quickly with command menu and keyboard shortcuts for faster workflows",
            icon: <CommandIcon className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Multilingual support",
            description:
              "Available in 12 languages including English, Japanese, Korean, and major European languages",
            icon: <LanguagesIcon className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Unified calendar view",
            description:
              "See all your personal and work commitments in one place to avoid scheduling conflicts",
            icon: <CalendarDaysIcon className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Multiple calendar sync",
            description:
              "Easily connect and manage both work and personal calendars in a single interface",
            icon: <CalendarRangeIcon className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Smart conflict prevention",
            description:
              "Automatically blocks busy time slots across all your connected calendars",
            icon: <XCircleIcon className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Mobile-friendly design",
            description:
              "Check and manage your schedule on the go with our intuitive mobile application",
            icon: <SmartphoneIcon className="text-brand size-5 stroke-1" />,
          },
        ]}
      />
      <TabsTop
        title="Choose your view"
        description="Saturn Calendar offers multiple ways to visualize your schedule so you can stay on top of your commitments"
        defaultTab="month"
        tabs={[
          {
            value: "month",
            title: "Month view",
            description: "See your whole month at a glance",
            icon: <CalendarIcon className="size-5 stroke-1" />,
            content: (
              <div className="bg-background relative z-10 w-full grow">
                <Calendar defaultView="month" />
              </div>
            ),
          },
          {
            value: "week",
            title: "Week view",
            description: "Plan your week effectively",
            icon: <CalendarRangeIcon className="size-5 stroke-1" />,
            content: (
              <div className="bg-background relative z-10 w-full grow">
                <Calendar defaultView="week" />
              </div>
            ),
          },
          {
            value: "day",
            title: "Day view",
            description: "Focus on your daily schedule",
            icon: <CalendarDaysIcon className="size-5 stroke-1" />,
            content: (
              <div className="bg-background relative z-10 w-full grow">
                <Calendar defaultView="day" />
              </div>
            ),
          },
        ]}
      />
      <SocialProof
        title="Loved by professionals and teams worldwide"
        description="Here's what our users are saying about Saturn Calendar"
        items={[
          {
            name: "Alex Thompson",
            username: "alexthompson",
            text: (
              <>
                <span className="text-brand">@SaturnCalendar</span> has
                completely transformed how our team coordinates meetings across
                time zones. The interface is intuitive and beautiful.
              </>
            ),
            image: "/avatars/alex.jpg",
            url: "https://twitter.com/alexthompson",
          },
          {
            name: "Sarah Parker",
            username: "sparkdev",
            text: (
              <>
                As a freelancer juggling multiple clients,{" "}
                <span className="text-brand">@SaturnCalendar</span> has been a
                game-changer. The scheduling feature alone has saved me hours
                each week.
              </>
            ),
            image: "/avatars/sarah.jpg",
            url: "https://twitter.com/sparkdev",
          },
          {
            name: "Marcus Chen",
            username: "marcusdev",
            text: (
              <>
                The multiple calendar sync in{" "}
                <span className="text-brand">@SaturnCalendar</span> is
                revolutionary. No more double bookings between work and personal
                commitments!
              </>
            ),
            image: "/avatars/marcus.jpg",
            url: "https://twitter.com/marcusdev",
          },
          {
            name: "Nina Patel",
            username: "ninadev",
            text: (
              <>
                The way <span className="text-brand">@SaturnCalendar</span>{" "}
                handles recurring events and team availability is brilliant.
                Makes everything so intuitive.
              </>
            ),
            image: "/avatars/nina.jpg",
            url: "https://twitter.com/ninadev",
          },
          {
            name: "James Wilson",
            username: "jwilsontech",
            text: (
              <>
                Our entire development team switched to{" "}
                <span className="text-brand">@SaturnCalendar</span> last month.
                The keyboard shortcuts and command menu have boosted our
                productivity.
              </>
            ),
            image: "/avatars/james.jpg",
            url: "https://twitter.com/jwilsontech",
          },
          {
            name: "Olivia Blackwood",
            username: "olivia1992",
            text: (
              <>
                <span className="text-brand">@SaturnCalendar</span> is not
                messing around with its cross-platform sync and mobile app.
                Super responsive and reliable.
              </>
            ),
            image: "/avatars/olivia.jpg",
            url: "https://twitter.com/olivia1992",
          },
        ]}
      />
      <Pricing
        title="Choose a plan that works for you"
        description="Saturn Calendar offers flexible pricing options to fit your needs, from individuals to large teams"
        yearlyDiscount={15}
        plans={[
          {
            name: "Basic",
            description: "Forever free for personal use",
            monthlyPrice: 0,
            yearlyPrice: 0,
            cta: {
              variant: "glow",
              label: "Get started for free",
              href: "#",
            },
            features: [
              "Personal calendar",
              "Mobile app access",
              "Basic scheduling tools",
              "Email reminders",
              "Connect 1 external calendar",
            ],
          },
          {
            name: "Team",
            description: "For teams who need the best scheduling experience",
            icon: <Users className="size-4" />,
            monthlyPrice: 12,
            yearlyPrice: 120,
            cta: {
              variant: "default",
              label: "Get started",
              href: "#",
            },
            features: [
              "Everything in Basic",
              "Advanced scheduling tools",
              "Multiple time zone support",
              "Connect up to 5 calendars",
              "Custom event types",
              "Calendar analytics",
              "Priority support",
            ],
            variant: "glow-brand",
          },
          {
            name: "Enterprise",
            description:
              "For larger teams that need to coordinate on a global scale",
            icon: <Building className="size-4" />,
            monthlyPrice: 25,
            yearlyPrice: 250,
            cta: {
              variant: "glow",
              label: "Contact sales",
              href: "#",
            },
            features: [
              "Everything in Team",
              "Team scheduling features",
              "Admin dashboard",
              "Resource booking",
              "Team calendar views",
              "Unlimited calendars",
              "SSO authentication",
              "API access",
              "Dedicated account manager",
            ],
            variant: "glow",
          },
        ]}
      />
      <FAQ
        title="Questions & answers"
        items={[
          {
            question:
              "Which calendar provider(s) is Saturn Calendar compatible with?",
            answer: (
              <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                Currently, Saturn Calendar integrates and syncs with Google
                Calendar accounts. Adding support for other calendar providers
                such as Outlook and iCloud is on our roadmap.
              </p>
            ),
          },
          {
            question: "Is Saturn Calendar available on mobile devices?",
            answer: (
              <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                Yes, Saturn Calendar is available for iPhone and Android
                devices. We&apos;re also working on an optimized version for
                tablet devices, such as iPad, to make Saturn Calendar the best
                experience on all platforms.
              </p>
            ),
          },
          {
            question: "Can I share my calendar with team members?",
            answer: (
              <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                Yes, Saturn Calendar offers robust team sharing features. You
                can share your calendar with specific team members, set
                different permission levels, and even create team-wide calendars
                for better coordination and scheduling.
              </p>
            ),
          },
          {
            question: "Does Saturn Calendar support multiple time zones?",
            answer: (
              <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                Absolutely! Saturn Calendar has comprehensive time zone support.
                You can view events in multiple time zones, schedule meetings
                across different regions, and automatically adjust times when
                traveling. The calendar will always show the correct local time
                for all participants.
              </p>
            ),
          },
          {
            question: "What kind of customer support do you offer?",
            answer: (
              <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                We provide 24/7 email support for all users. Team and Enterprise
                plan subscribers get priority support with guaranteed response
                times and access to live chat. Enterprise customers also receive
                a dedicated account manager for personalized assistance.
              </p>
            ),
          },
        ]}
      />
      <CTA
        title="Ready to transform your scheduling experience?"
        buttons={[
          {
            href: "/",
            text: "Get Started",
            variant: "default",
          },
          {
            href: "/",
            text: "Contact sales",
            variant: "glow",
          },
        ]}
      />
      <Footer
        name="Saturn"
        logo={<SaturnLogo />}
        copyright="© 2025 Saturn Calendar. All rights reserved."
        columns={[
          {
            title: "Product",
            links: [
              { text: "Features", href: "/" },
              { text: "Pricing", href: "/" },
              { text: "Integrations", href: "/" },
              { text: "Changelog", href: "/" },
            ],
          },
          {
            title: "Resources",
            links: [
              { text: "Documentation", href: "/" },
              { text: "API", href: "/" },
              { text: "Guides", href: "/" },
              { text: "Help Center", href: "/" },
            ],
          },
          {
            title: "Company",
            links: [
              { text: "About", href: "/" },
              { text: "Blog", href: "/" },
              { text: "Careers", href: "/" },
              { text: "Contact", href: "/" },
            ],
          },
          {
            title: "Legal",
            links: [
              { text: "Privacy", href: "/" },
              { text: "Terms", href: "/" },
              { text: "Cookie Policy", href: "/" },
            ],
          },
        ]}
        policies={[
          { text: "Privacy Policy", href: "/" },
          { text: "Terms of Service", href: "/" },
          { text: "Cookie Settings", href: "/" },
        ]}
      />
    </div>
  );
}

export default Saturn;
