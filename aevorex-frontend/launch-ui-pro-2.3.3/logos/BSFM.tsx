import * as React from "react";

const BSFM = () => (
  <>
    {/* Light theme (fekete logó) */}
    <img
      src="/logos/BSFM-light.png"
      alt="BSFM"
      className="block dark:hidden w-[120px] h-auto"
    />
    {/* Dark theme (fehér logó) */}
    <img
      src="/logos/BSFM-dark.avif"
      alt="BSFM"
      className="hidden dark:block w-[120px] h-auto"
    />
  </>
);

export default BSFM;