import * as React from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";

export default function Aevorex({ className, size = "default" }: { className?: string; size?: "small" | "default" | "large" }) {
  const sizeClasses = {
    small: "h-4 w-auto", // Calendar sidebar - 4x nagyobb (16px -> 64px)
    default: "h-8 w-auto", // Navbar - eredeti méret (48px)
    large: "h-20 w-auto"
  };

  // Calendar sidebar-ban SVG-t használunk, máshol PNG-t
  const logoSrc = size === "small" ? "/vendors/aevorex2.svg" : "/vendors/aevorex.png";

  return (
    <span className={cn("inline-flex items-center gap-2", className)}>
      <Image 
        src={logoSrc} 
        alt="Aevorex" 
        width={532} 
        height={469} 
        className={cn(sizeClasses[size], "dark:brightness-0 dark:invert object-contain")} 
      />
      <span className="sr-only">Aevorex</span>
    </span>
  );
}
