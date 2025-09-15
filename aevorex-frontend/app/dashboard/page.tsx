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


export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <section id="hero"><Hero /></section>
        <section id="bento"><BentoGrid /></section>
        {/* <section id="carousel"><CarouselSmall /></section> */}
        <section id="feature"><Feature /></section>
        {/* <section id="gallery"><Gallery /></section> */}
        <section id="items"><Items /></section>
        <section id="logos"><Logos /></section>
       {/*<section id="social-proof"><SocialProof /></section>
        {/* <section id="stats"><Stats /></section> */}
        {/* <section id="tabs"><Tabs /></section>
        {/* <section id="testimonials"><TestimonialsCarousel /></section> */}
        {/*<section id="pricing"><Pricing /></section>*/}
        <section id="faq"><FAQ /></section>
        <section id="cta"><CTA /></section>
      </main>
      <Footer />
    </>
  );
}
