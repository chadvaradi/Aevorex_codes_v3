import React from "react";

export default function ImageSkeleton() {
  return (
    <div className="animate-reveal h-full w-full">
      <div className="relative h-full w-full animate-pulse">
        <div className="sr-only">Generating image...</div>

        <div className="glass-4 absolute inset-0 z-10 rounded-lg backdrop-blur-lg" />
        <div className="absolute inset-0 z-10 rounded-lg backdrop-blur-xl" />
        <div className="absolute inset-0 z-10 rounded-lg shadow-xl shadow-amber-500/20" />
        <div className="absolute inset-0 z-10 rotate-90 rounded-lg shadow-xl shadow-pink-500/20" />
        <div className="absolute inset-0 z-10 rotate-180 rounded-lg shadow-xl shadow-purple-500/20" />
        <div className="absolute inset-0 z-10 rotate-270 rounded-lg shadow-xl shadow-blue-500/20" />

        {/* Animated background gradient effect */}
        <div className="animate-rotate absolute inset-0 z-0 flex flex-wrap opacity-20">
          <div className="h-[50%] w-[50%] scale-[2.25] rounded-full bg-radial from-amber-500 via-amber-500/20 via-50% to-transparent to-70%"></div>
          <div className="h-[50%] w-[50%] scale-[2.25] rounded-full bg-radial from-pink-500 via-pink-500/20 via-50% to-transparent to-70%"></div>
          <div className="h-[50%] w-[50%] scale-[2.25] rounded-full bg-radial from-purple-500 via-purple-500/20 via-50% to-transparent to-70%"></div>
          <div className="h-[50%] w-[50%] scale-[2.25] rounded-full bg-radial from-blue-500 via-blue-500/20 via-50% to-transparent to-70%"></div>
        </div>
      </div>
    </div>
  );
}
