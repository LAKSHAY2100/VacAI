import React from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Download, RotateCcw, Sparkles } from "lucide-react";

export const ResultsPanel = ({ itinerary, meta, onReset }) => {
  const handleDownload = () => {
    const blob = new Blob([itinerary], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const slug = (meta?.destination || "itinerary")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
    a.href = url;
    a.download = `vacaigent-${slug}.md`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <section
      id="results"
      data-testid="results-section"
      className="bg-[#FAF9F6] relative"
    >
      <div className="max-w-6xl mx-auto px-6 sm:px-10 lg:px-14 py-20 lg:py-28">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
          className="bg-white rounded-[2rem] border border-[#E6E4DF] shadow-soft-lg overflow-hidden"
        >
          {/* Header bar */}
          <div className="relative px-8 sm:px-12 lg:px-16 pt-10 pb-9 border-b border-[#F0EFEB]">
            <div
              aria-hidden
              className="absolute inset-0 pointer-events-none opacity-50"
              style={{
                background:
                  "radial-gradient(600px 200px at 80% 0%, rgba(244,220,213,0.55), transparent 60%)",
              }}
            />
            <div className="relative flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
              <div>
                <div className="uppercase-eyebrow text-[#D36B4A] flex items-center gap-2">
                  <Sparkles className="w-3.5 h-3.5" strokeWidth={1.6} />
                  Your travel brief
                </div>
                <h2 className="mt-3 font-display text-4xl lg:text-5xl tracking-tight text-[#1C1B1A] leading-[1.05]">
                  {meta?.destination || "Your journey"}
                </h2>
                {meta ? (
                  <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1.5 text-sm text-[#7A7671]">
                    <span>From {meta.origin}</span>
                    <span className="text-[#D9C5B2]">·</span>
                    <span>
                      {meta.start_date} → {meta.end_date}
                    </span>
                  </div>
                ) : null}
              </div>
              <div className="flex items-center gap-3">
                <button
                  data-testid="results-download"
                  onClick={handleDownload}
                  className="btn-ghost"
                >
                  <Download className="w-4 h-4" strokeWidth={1.6} />
                  Download .md
                </button>
                <button
                  data-testid="results-replan"
                  onClick={onReset}
                  className="btn-ghost"
                >
                  <RotateCcw className="w-4 h-4" strokeWidth={1.6} />
                  Plan another
                </button>
              </div>
            </div>
          </div>

          {/* Markdown body */}
          <div className="px-8 sm:px-12 lg:px-16 py-12 lg:py-14">
            <article
              data-testid="results-markdown"
              className="prose prose-editorial max-w-none"
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {itinerary || ""}
              </ReactMarkdown>
            </article>
          </div>

          <div className="px-8 sm:px-12 lg:px-16 pb-10 -mt-2">
            <div className="editorial-rule" />
            <p className="mt-6 text-xs uppercase tracking-[0.22em] text-[#7A7671]">
              Composed by VacAIgent · Adjust freely · Bookings sold separately
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default ResultsPanel;
