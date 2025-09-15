import * as React from "react";

const BSML = () => (
  <>
    {/* Light theme (fekete logó) */}
    <img
      src="/logos/BSML-light.png"
      alt="BSML"
      className="block dark:hidden w-[140px] h-auto"
    />
    {/* Dark theme (fehér logó) */}
    <img
      src="/logos/BSML-dark.png"
      alt="BSML"
      className="hidden dark:block w-[140px] h-auto"
    />
  </>
);

export default BSML;