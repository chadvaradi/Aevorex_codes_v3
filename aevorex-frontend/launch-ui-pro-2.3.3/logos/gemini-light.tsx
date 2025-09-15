import * as React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

export default function GeminiLight({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2", className)}>
      <Image 
        src="/vendors/gemini.svg" 
        alt="Gemini" 
        width={72} 
        height={72} 
        className="h-12 w-auto brightness-0"
      />
      <span className="sr-only">Gemini</span>
    </span>
  );
}
