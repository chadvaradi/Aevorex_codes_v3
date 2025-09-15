import * as React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

export default function XAILight({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2", className)}>
      <Image 
        src="/vendors/xai.svg" 
        alt="xAI" 
        width={72} 
        height={72} 
        className="h-12 w-auto"      />
      <span className="sr-only">xAI</span>
    </span>
  );
}
