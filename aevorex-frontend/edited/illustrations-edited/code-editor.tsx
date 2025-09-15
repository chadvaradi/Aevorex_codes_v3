import * as React from "react";
import Glow from "../../launch-ui-pro-2.3.3/ui/glow";
import ReactLogo from "../../launch-ui-pro-2.3.3/logos/react";
import Tailwind from "../../launch-ui-pro-2.3.3/logos/tailwind";

function CodeEditorIllustration() {
  return (
    <div data-slot="code-editor-illustration" className="h-full w-full">
      <div className="relative h-full w-full">
        <div className="absolute top-0 left-[50%] z-10 w-full -translate-x-[50%] translate-y-0">
          <div className="border-border/100 bg-muted dark:border-border/5 dark:border-t-border/15 dark:bg-accent/30 relative flex min-h-[540px] min-w-[460px] flex-col gap-4 rounded-[12px] border">
            <div className="flex w-full items-center justify-start gap-4 overflow-hidden py-2">
              <div className="hidden gap-2 pl-4 lg:flex">
                <div className="bg-accent dark:bg-foreground/10 size-3 rounded-full"></div>
                <div className="bg-accent dark:bg-foreground/10 size-3 rounded-full"></div>
                <div className="bg-accent dark:bg-foreground/10 size-3 rounded-full"></div>
              </div>
              <div className="relative flex w-[320px]">
                <div className="text-muted-foreground relative z-10 flex grow basis-0 items-center gap-2 px-4 py-1.5 text-xs">
                  <ReactLogo className="size-4" />
                  <p>pipeline.py</p>
                </div>
                <div className="text-muted-foreground relative z-10 flex grow basis-0 items-center gap-2 px-4 py-1.5 text-xs">
                  <Tailwind className="size-4" />
                  <p>component.tsx</p>
                </div>
                <div className="absolute top-0 left-0 h-full w-[50%] px-2 transition-all duration-1000 ease-in-out group-hover:left-[50%]">
                  <div className="glass-4 h-full w-full rounded-md shadow-md"></div>
                </div>
              </div>
            </div>
            <div className="relative w-full grow overflow-hidden">
              <div className="absolute top-0 left-0 translate-x-0 px-8 transition-all duration-1000 ease-in-out group-hover:translate-x-[-100%] group-hover:opacity-0">
                <pre className="text-muted-foreground font-mono text-xs">
{`# Aevorex · Data Pipeline
import aevorex_client
from typing import Dict, List

# Configure data sources
sources = {
    "market_data": "EODHD",
    "economic": "FRED", 
    "rates": "EURIBOR"
}

# AI analysis workflow
def analyze_stock(ticker: str) -> Dict:
    # Fetch real-time data
    market_data = fetch_eodhd(ticker)
    economic_data = fetch_fred_indicators()
    
    # LLM processing
    analysis = llm_analyze(market_data, economic_data)
    
    return {
        "insights": analysis,
        "sources": sources,
        "audit_trail": True
    }

# Export formats
export_formats = ["CSV", "PDF", "JSON"]`}
                </pre>
              </div>

              <div className="absolute top-0 left-0 translate-x-[100%] px-8 opacity-0 transition-all duration-1000 ease-in-out group-hover:translate-x-0 group-hover:opacity-100">
                <pre className="text-muted-foreground font-mono text-xs">
{`// Aevorex · React Component
import React, { useState, useEffect } from 'react';
import { useAevorexClient } from './hooks/useAevorex';

interface StockComparisonProps {
  ticker1: string;
  ticker2: string;
}

export const StockComparison: React.FC<StockComparisonProps> = ({
  ticker1,
  ticker2
}) => {
  const [analysis, setAnalysis] = useState(null);
  const { fetchComparison } = useAevorexClient();

  useEffect(() => {
    const runAnalysis = async () => {
      const result = await fetchComparison(ticker1, ticker2);
      setAnalysis(result);
    };
    runAnalysis();
  }, [ticker1, ticker2]);

  return (
    <div className="analysis-container">
      {analysis && (
        <div className="insights">
          <h3>Earnings Trend Analysis</h3>
          <Chart data={analysis.chart} />
          <Table data={analysis.table} />
        </div>
      )}
    </div>
  );
};`}
                </pre>
              </div>
            </div>
          </div>
        </div>
        <Glow
          variant="below"
          className="translate-y-32 scale-150 opacity-40 transition-all duration-1000 group-hover:scale-200 group-hover:opacity-60"
        />
      </div>
    </div>
  );
}

export default CodeEditorIllustration;
