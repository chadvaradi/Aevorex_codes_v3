import * as React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

export default function AnthropicLight({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2", className)}>
      <Image 
        src="/vendors/anthropic-light.svg" 
        alt="Anthropic" 
        width={184} 
        height={40} 
        className="h-12 w-auto" 
      />
      <span className="sr-only">Anthropic</span>
    </span>
  );
}
