import * as React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

export default function OpenAILight({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2", className)}>
      <Image
        src="/vendors/openai.svg"
        alt="OpenAI"
        width={72}
        height={72}
        priority={false}
        className="h-18 w-18 white "
      />
      <span className="sr-only">OpenAI</span>
    </span>
  );
}
