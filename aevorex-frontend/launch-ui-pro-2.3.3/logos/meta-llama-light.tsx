import * as React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

export default function MetaLlamaLight({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2", className)}>
      <Image 
        src="/vendors/meta-llama.svg" 
        alt="Meta Llama" 
        width={72} 
        height={72} 
        className="h-12 w-auto"
      />
      <span className="sr-only">Meta Llama</span>
    </span>
  );
}
