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
import ChatApp from "@/edited/chat/app";


export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <ChatApp />
      </main>
      <Footer />
    </>
  );
}
