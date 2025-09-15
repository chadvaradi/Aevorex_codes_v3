import {
  ArrowRight,
  PenTool,
  BrainCircuit,
  Sparkles,
  MessageSquare,
  Terminal,
  Lock,
  Zap,
  BarChart,
  Users,
} from "lucide-react";
import Link from "next/link";

import Navbar from "../../sections/navbar/sticky";
import Hero from "../../sections/hero/top-glow";
import ChatApp from "../../templates/chat/app";
import LogosMarquee from "../../sections/logos/marquee";
import Items from "../../sections/items/default-brand";
import Pricing from "../../sections/pricing/2-cols";
import FAQ from "../../sections/faq/2-cols-raised";
import CTA from "../../sections/cta/beam";
import Footer from "../../sections/footer/default";
import NeptuneLogo from "../../logos/neptune";
import BentoGrid from "../../sections/bento-grid/3-rows-top";
import FeatureMockup from "../../sections/feature/mockup";
import SocialProof from "../../sections/social-proof/masonry";
import TestimonialsCarousel from "../../sections/testimonials/carousel";
import CodeEditorIllustration from "../../illustrations/code-editor";
import MockupMobileIllustration from "../../illustrations/mockup-mobile";
import ChatIllustration from "../../illustrations/chat";
import MockupBrowserIllustration from "../../illustrations/mockup-browser";
import { Button } from "../../ui/button";
import PipelineIllustration from "../../illustrations/pipeline";
import CoreOS from "../../logos/coreos";
import Peregrin from "../../logos/peregrin";
import EasyTax from "../../logos/easytax";
import CarouselLarge from "../../sections/carousel/large";
import Screenshot from "../../ui/screenshot";

function Neptune() {
  return (
    <div
      className="flex flex-col"
      style={
        {
          "--brand-foreground": "var(--brand-ultraviolet-foreground)",
          "--brand": "var(--brand-ultraviolet)",
          "--primary": "light-dark(var(--brand-ultraviolet), oklch(0.985 0 0))",
          "--background": "var(--background-ultraviolet)",
          "--muted": "var(--background-ultraviolet)",
          "--radius": "1.5rem",
        } as React.CSSProperties
      }
    >
      <Navbar
        logo={<NeptuneLogo />}
        name="Neptune"
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
            text: "Try for free",
            href: "/",
            isButton: true,
            variant: "default",
          },
        ]}
        className="-mb-32"
      />
      <Hero
        title="The world's most advanced AI assistant"
        description="Neptune AI combines cutting-edge neural networks with a deep understanding of human language to deliver unparalleled AI capabilities. Generate text, code, and images with a single platform."
        buttons={[
          {
            href: "/",
            text: "Try for free",
            variant: "default",
            iconRight: <ArrowRight className="ml-2 size-4" />,
          },
          {
            href: "/",
            text: "See demo",
            variant: "glow",
          },
        ]}
        mockup={
          <div className="bg-background">
            <ChatApp />
          </div>
        }
      />
      <LogosMarquee />
      <BentoGrid
        title="One AI assistant. Limitless possibilities."
        description="Neptune AI is designed to be your universal thinking partner, helping with everything from creative writing to complex coding tasks."
        tiles={[
          {
            title: "Advanced coding assistant",
            description: (
              <p>
                Get help with any programming language, framework, or coding
                task. Neptune understands code context and can generate,
                explain, and debug with precision.
              </p>
            ),
            visual: (
              <div className="min-h-[300px] w-full py-12">
                <CodeEditorIllustration />
              </div>
            ),
            size: "col-span-12 md:col-span-6 lg:col-span-7",
          },
          {
            title: "Revolutionary neural architecture",
            description: (
              <p className="max-w-[460px]">
                Powered by our proprietary neural architecture with over 1
                trillion parameters for deeper understanding and more natural
                interactions.
              </p>
            ),
            visual: (
              <div className="min-h-[160px] grow items-center self-center">
                <PipelineIllustration />
              </div>
            ),
            size: "col-span-12 md:col-span-6 lg:col-span-5",
          },
          {
            title: "Natural conversations",
            description: (
              <p className="max-w-[460px]">
                Neptune maintains context throughout long conversations,
                remembers your preferences, and learns from your interactions.
              </p>
            ),
            visual: (
              <div className="w-full sm:p-4 md:p-8">
                <ChatIllustration />
              </div>
            ),
            size: "col-span-12 md:col-span-6 lg:col-span-5",
          },
          {
            title: "Stunning image generation",
            description:
              "Create beautiful, detailed images from simple text descriptions with our advanced diffusion model.",
            visual: (
              <div className="min-h-[240px] grow basis-0 sm:p-4 md:min-h-[320px] md:py-12 lg:min-h-[360px]">
                <MockupBrowserIllustration />
              </div>
            ),
            size: "col-span-12 md:col-span-6 lg:col-span-7",
          },
          {
            title: "Continuous learning",
            description: (
              <p className="max-w-[460px]">
                Neptune gets smarter with every interaction, continuously
                refining its responses based on your feedback.
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
            title: "Mobile companion",
            description: (
              <p>
                Take Neptune with you everywhere with our powerful mobile app.
                Same capabilities, optimized for on-the-go use.
              </p>
            ),
            visual: (
              <div className="min-h-[300px] w-full py-12">
                <MockupMobileIllustration />
              </div>
            ),
            size: "col-span-12 md:col-span-6 lg:col-span-5",
          },
        ]}
      />
      <FeatureMockup
        title="Supercharged content creation"
        description="Neptune AI understands context, follows instructions with precision, and generates high-quality content in seconds."
        visual={
          <div className="bg-background relative z-10 w-full">
            <ChatApp />
          </div>
        }
      />
      <Items
        title="The most versatile AI assistant ever created"
        items={[
          {
            title: "Text generation",
            description:
              "Create essays, stories, blog posts, emails, and more with unprecedented fluency and creativity",
            icon: <MessageSquare className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Code generation",
            description:
              "Write efficient, bug-free code in over 50 programming languages with detailed explanations",
            icon: <Terminal className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Image generation",
            description:
              "Create stunning, detailed images from text descriptions with our advanced diffusion model",
            icon: <PenTool className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Advanced reasoning",
            description:
              "Solve complex problems with step-by-step thinking and logical analysis of difficult scenarios",
            icon: <BrainCircuit className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Contextual awareness",
            description:
              "Maintains conversation history and learns from interactions to provide more personalized responses",
            icon: <Sparkles className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Built-in privacy",
            description:
              "Enterprise-grade security with data encryption and optional no-storage mode for sensitive information",
            icon: <Lock className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Lightning-fast responses",
            description:
              "Get answers in milliseconds thanks to our optimized inference engine and distributed architecture",
            icon: <Zap className="text-brand size-5 stroke-1" />,
          },
          {
            title: "Detailed analytics",
            description:
              "Track usage, monitor performance, and gain insights into how your team uses Neptune",
            icon: <BarChart className="text-brand size-5 stroke-1" />,
          },
        ]}
      />
      <TestimonialsCarousel
        items={[
          {
            name: "Alex Chen",
            role: "Senior Software Engineer, TechCorp",
            text: "Neptune AI has completely transformed my workflow. I'm writing better code in half the time, with fewer bugs and more elegant solutions.",
            image: "/avatars/alex.jpg",
            Logo: CoreOS,
          },
          {
            name: "Sophia Martinez",
            role: "Digital Artist & Illustrator",
            text: "The image generation capabilities are mind-blowing. I can create concept art in minutes that would have taken me days before.",
            image: "/avatars/sophia.jpg",
            Logo: Peregrin,
          },
          {
            name: "James Wilson",
            role: "Content Marketing Manager",
            text: "As a content creator, Neptune AI is like having a writing partner who's always available. It helps me overcome writer's block and refine my ideas.",
            image: "/avatars/james.jpg",
            Logo: EasyTax,
          },
        ]}
      />
      <SocialProof
        title="Join thousands of satisfied users"
        description="See what people are saying about Neptune AI on social media"
        items={[
          {
            name: "David Thompson",
            username: "davecodes",
            text: (
              <>
                <span className="text-brand">@NeptuneAI</span> just helped me
                refactor an entire codebase in a few hours. The code suggestions
                are so intelligent it feels like pair programming with a genius.
              </>
            ),
            image: "/avatars/marcin.jpg",
            url: "https://twitter.com/davecodes",
          },
          {
            name: "Sarah Chen",
            username: "sarahcreates",
            text: (
              <>
                Mind. Blown. 🤯 <span className="text-brand">@NeptuneAI</span>
              </>
            ),
            image: "/avatars/sarah.jpg",
            url: "https://twitter.com/sarahcreates",
          },
          {
            name: "Marcus Rodriguez",
            username: "marcusdev",
            text: (
              <>
                The way <span className="text-brand">@NeptuneAI</span> maintains
                context throughout a long conversation is incredible. It
                remembers details from earlier in our chat that even I had
                forgotten! Never going back to other AI assistants.
              </>
            ),
            image: "/avatars/marcus.jpg",
            url: "https://twitter.com/marcusdev",
          },
          {
            name: "Priya Patel",
            username: "priyatech",
            text: (
              <>
                <span className="text-brand">@NeptuneAI</span> is pure magic ✨
              </>
            ),
            image: "/avatars/paulina.jpg",
            url: "https://twitter.com/priyatech",
          },
          {
            name: "James Wilson",
            username: "jwilsontech",
            text: (
              <>
                Our entire development team switched to{" "}
                <span className="text-brand">@NeptuneAI</span> last month. The
                collaborative features have improved our codebase quality
                significantly. Best decision we&apos;ve made this year.
              </>
            ),
            image: "/avatars/felix.jpg",
            url: "https://twitter.com/jwilsontech",
          },
          {
            name: "Olivia Zhang",
            username: "oliviawrites",
            text: (
              <>
                Game changer for content creation!{" "}
                <span className="text-brand">@NeptuneAI</span>
              </>
            ),
            image: "/avatars/olivia.jpg",
            url: "https://twitter.com/oliviawrites",
          },
          {
            name: "Michael Foster",
            username: "mikefoster",
            text: (
              <>
                <span className="text-brand">@NeptuneAI</span> helped me build
                an entire MVP in 48 hours. The code quality is outstanding and
                it even caught edge cases I would have missed. This is the
                future of development.
              </>
            ),
            image: "/avatars/mikolaj.jpg",
            url: "https://twitter.com/mikefoster",
          },
          {
            name: "Lisa Park",
            username: "lisadesigns",
            text: (
              <>
                Finally, an AI that gets design!{" "}
                <span className="text-brand">@NeptuneAI</span>
              </>
            ),
            image: "/avatars/esme.jpg",
            url: "https://twitter.com/lisadesigns",
          },
          {
            name: "Alex Kumar",
            username: "alexk",
            text: (
              <>
                The way <span className="text-brand">@NeptuneAI</span> handles
                complex technical discussions is unreal. It&apos;s like having a
                senior architect on call 24/7.
              </>
            ),
            image: "/avatars/darius.jpg",
            url: "https://twitter.com/alexk",
          },
          {
            name: "Rachel Morgan",
            username: "rachelm",
            text: (
              <>
                <span className="text-brand">@NeptuneAI</span> just saved my
                deadline 🙏
              </>
            ),
            image: "/avatars/paulina.jpg",
            url: "https://twitter.com/rachelm",
          },
          {
            name: "Carlos Mendoza",
            username: "carlosdev",
            text: (
              <>
                Switching to <span className="text-brand">@NeptuneAI</span>{" "}
                boosted our team&apos;s productivity by 3x. The AI understands
                our codebase better than some of our own developers!
              </>
            ),
            image: "/avatars/kai.jpg",
            url: "https://twitter.com/carlosdev",
          },
          {
            name: "Emma Watson",
            username: "emmacodes",
            text: (
              <>
                10/10 would recommend{" "}
                <span className="text-brand">@NeptuneAI</span>
              </>
            ),
            image: "/avatars/sarah.jpg",
            url: "https://twitter.com/emmacodes",
          },
          {
            name: "Yuki Tanaka",
            username: "yukidev",
            text: (
              <>
                <span className="text-brand">@NeptuneAI</span> revolutionized
                our localization workflow. It handles context and nuance across
                languages better than any tool I&apos;ve used in my 15 years of
                development. Simply incredible.
              </>
            ),
            image: "/avatars/fabrizio.jpg",
            url: "https://twitter.com/yukidev",
          },
          {
            name: "Zara Ahmed",
            username: "zarabuilds",
            text: (
              <>
                Wow. Just wow. <span className="text-brand">@NeptuneAI</span> 🚀
              </>
            ),
            image: "/avatars/olivia.jpg",
            url: "https://twitter.com/zarabuilds",
          },
          {
            name: "Sofia Rodriguez",
            username: "sofiatech",
            text: (
              <>
                Perfect. <span className="text-brand">@NeptuneAI</span>
              </>
            ),
            image: "/avatars/esme.jpg",
            url: "https://twitter.com/sofiatech",
          },
          {
            name: "Thomas Anderson",
            username: "neo_codes",
            text: (
              <>
                Just watched <span className="text-brand">@NeptuneAI</span>{" "}
                debug a complex race condition in milliseconds. My jaw is on the
                floor. This is what the future of programming looks like.
              </>
            ),
            image: "/avatars/mikolaj.jpg",
            url: "https://twitter.com/neo_codes",
          },
        ]}
      />
      <CarouselLarge
        title="Live changing stories from our users"
        description="Neptune AI is helping people to radically transform their lives and businesses"
        slides={[
          {
            tagline: "To 10k MRR in 3 months",
            title: "New viral AI game born overnight",
            description:
              "John used Neptune AI to create a viral AI game that went from 0 to 10k MRR in 3 months. During one weekend, he managed to lay the groundwork for the game and the rest is history. Neptune AI helped him to plan the works and execute majority of the work.",
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
            tagline: "From idea to bestseller",
            title: "AI-powered novel writing journey",
            description:
              "Sarah used Neptune AI to help outline, draft and edit her debut science fiction novel. The AI provided creative suggestions, helped maintain consistency, and even assisted with world-building. Her book hit the Amazon bestseller list within two weeks of launch.",
            image: (
              <Screenshot
                srcLight="/app-mail-light.png"
                srcDark="/app-mail-dark.png"
                alt="Writing assistant"
                width={900}
                height={600}
              />
            ),
          },
          {
            tagline: "Learning breakthrough",
            title: "Mastering quantum physics at 65",
            description:
              "Retired engineer Bob always struggled with quantum physics. Using Neptune AI as his study companion, he finally grasped complex concepts through personalized explanations and interactive problem-solving. He's now teaching an online course sharing his knowledge with others.",
            image: (
              <Screenshot
                srcLight="/app-light.png"
                srcDark="/app-dark.png"
                alt="Learning assistant"
                width={900}
                height={600}
              />
            ),
          },
          {
            tagline: "Small business revolution",
            title: "Local bakery goes global",
            description:
              "Maria's family bakery was struggling until she used Neptune AI to optimize recipes, create marketing content, and build an e-commerce strategy. Her unique AI-enhanced recipes now ship nationwide, and revenue has increased 500% in 6 months.",
            image: (
              <Screenshot
                srcLight="/app-settings-light.png"
                srcDark="/app-settings-dark.png"
                alt="Business growth"
                width={900}
                height={600}
              />
            ),
          },
        ]}
      />
      <Pricing
        title="Choose the plan that works for you"
        description="From solo creators to large enterprises, we have a plan to fit your needs and budget"
        plans={[
          {
            name: "Starter",
            description: "Perfect for personal projects and individuals",
            price: 15,
            priceNote: "Monthly or save 20% annually",
            cta: {
              variant: "glow",
              label: "Get started",
              href: "#",
            },
            features: [
              "Up to 1,000 messages per month",
              "Basic text generation",
              "Code assistance",
              "Limited image generation",
              "Mobile app access",
              "Email support",
            ],
            variant: "glow",
          },
          {
            name: "Pro",
            description: "For professionals who need powerful AI capabilities",
            icon: <Users className="size-4" />,
            price: 30,
            priceNote: "Monthly or save 20% annually",
            cta: {
              variant: "default",
              label: "Get started",
              href: "#",
            },
            features: [
              "Unlimited messages",
              "Advanced text generation",
              "Priority code assistance",
              "Full image generation",
              "API access (limited)",
              "Chat history (90 days)",
              "Priority support",
              "Team collaboration (up to 3 members)",
            ],
            variant: "glow-brand",
          },
        ]}
      />
      <FAQ
        title="Frequently asked questions"
        items={[
          {
            question:
              "What makes Neptune AI different from other AI assistants?",
            answer: (
              <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                Neptune AI utilizes our proprietary neural architecture with
                over 1 trillion parameters, trained on a diverse dataset of
                text, code, and images. This results in more accurate responses,
                better understanding of context, and more creative outputs
                compared to other AI assistants.
              </p>
            ),
          },
          {
            question: "Is my data safe with Neptune AI?",
            answer: (
              <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                We take data privacy seriously. By default, we use your
                conversations to improve our models, but you can enable Privacy
                Mode to prevent any data storage. Enterprise plans include
                additional security features like encrypted storage, audit logs,
                and custom data retention policies.
              </p>
            ),
          },
          {
            question: "Can I integrate Neptune AI with my existing tools?",
            answer: (
              <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                Yes! Neptune AI offers APIs and integrations with popular tools
                like Meet, Notion, GitHub, Zoom, and many more. Our Pro plan
                includes API access so you can build custom integrations with
                your existing workflows.
              </p>
            ),
          },
          {
            question: "How accurate is the code generation feature?",
            answer: (
              <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                Our code generation capabilities are best-in-class, supporting
                over 50 programming languages. Internal testing shows Neptune AI
                produces code with 95% accuracy on common tasks, and includes
                detailed explanations to help you understand and adapt the code
                to your specific needs.
              </p>
            ),
          },
          {
            question: "Can Neptune AI generate images?",
            answer: (
              <p className="text-muted-foreground mb-4 max-w-[640px] text-balance">
                Absolutely! Neptune AI includes a powerful image generation
                model that can create high-quality images from text
                descriptions. Pro plan includes more generation credits and
                higher resolution outputs, with fine-grained control over the
                style and content of generated images.
              </p>
            ),
          },
        ]}
      />
      <CTA
        title="Experience the future of AI assistance today"
        description="Try Neptune AI risk-free with our 14-day trial."
        form={
          <div className="flex flex-wrap justify-center gap-4">
            <Button variant="default" size="lg" asChild>
              <Link href="/">Try for free</Link>
            </Button>
            <Button variant="glow" size="lg" asChild>
              <Link href="/">Schedule a demo</Link>
            </Button>
          </div>
        }
      />
      <Footer
        name="Neptune AI"
        logo={<NeptuneLogo />}
        copyright="© 2024 Neptune AI. All rights reserved."
        columns={[
          {
            title: "Product",
            links: [
              { text: "Features", href: "/" },
              { text: "Pricing", href: "/" },
              { text: "Integrations", href: "/" },
              { text: "Updates", href: "/" },
            ],
          },
          {
            title: "Resources",
            links: [
              { text: "Documentation", href: "/" },
              { text: "API", href: "/" },
              { text: "Tutorials", href: "/" },
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
              { text: "AI Ethics", href: "/" },
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

export default Neptune;
