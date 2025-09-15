import { ReactNode } from "react";
import Link from "next/link";

import { Section } from "@/launch-ui-pro-2.3.3/ui/section";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/launch-ui-pro-2.3.3/ui/accordion-raised";

interface FAQItemProps {
  question: string;
  answer: ReactNode;
  value?: string;
}

interface FAQProps {
  title?: string;
  items?: FAQItemProps[] | false;
  className?: string;
}

export default function FAQ({
  title = "Questions and Answers",
  items = [
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
            Aevorex uses multiple data sources and transparent methodologies. The AI doesn't make predictions — it accelerates research, highlights patterns, and saves time.
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
  ],
  className,
}: FAQProps) {
  return (
    <Section className={className}>
      <div className="max-w-container mx-auto flex flex-col items-center gap-8 md:flex-row md:items-start">
        <h2 className="text-center text-3xl leading-tight font-semibold sm:text-5xl md:text-left md:leading-tight">
          {title}
        </h2>
        {items !== false && items.length > 0 && (
          <Accordion type="single" collapsible className="w-full max-w-[800px]">
            {items.map((item, index) => (
              <AccordionItem
                key={index}
                value={item.value || `item-${index + 1}`}
              >
                <AccordionTrigger>{item.question}</AccordionTrigger>
                <AccordionContent>{item.answer}</AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        )}
      </div>
    </Section>
  );
}
