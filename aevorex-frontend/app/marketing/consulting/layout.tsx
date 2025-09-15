import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Aevorex Consulting – AI Strategy & Execution",
  description:
    "Practical, scalable AI-driven solutions tailored to your business. Develop your competitive edge with Aevorex.",
  openGraph: {
    title: "Aevorex Consulting – AI Strategy & Execution",
    description:
      "Practical, scalable AI-driven solutions tailored to your business. Develop your competitive edge with Aevorex.",
    url: "https://aevorex.com/consulting", // 🔑 teljes URL
    siteName: "Aevorex Consulting",
    images: [
      {
        url: "https://aevorex.com/website_banner.png", // 🔑 abszolút URL
        width: 1200,
        height: 630,
        alt: "Aevorex Consulting – AI Strategy & Execution",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Aevorex Consulting – AI Strategy & Execution",
    description:
      "Practical, scalable AI-driven solutions tailored to your business.",
    images: ["https://aevorex.com/website_banner.png"], // 🔑 abszolút URL
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function ConsultingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}