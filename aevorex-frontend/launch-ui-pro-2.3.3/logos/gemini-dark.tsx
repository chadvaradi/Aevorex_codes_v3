import * as React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

export default function GeminiDark({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2", className)}>
      <Image 
        src="/vendors/gemini.svg" 
        alt="Gemini" 
        width={72} 
        height={72} 
        className="h-18 w-18 brightness-0 invert" 
      />
      <span className="sr-only">Gemini</span>
    </span>
  );
}
