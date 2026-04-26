import React from "react";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";

const heroImage =
  "https://static.prod-images.emergentagent.com/jobs/83578421-41c8-4bad-b2f4-e2e33b124e54/images/c78914d355229f3c4b7625e1ed1dca0854e1c774082d7563595acc92382d2336.png";
const sandTexture =
  "https://static.prod-images.emergentagent.com/jobs/83578421-41c8-4bad-b2f4-e2e33b124e54/images/6ced2b76211b91f7f2b3cb8513e3cc7c97c386f547f3726311d1596ef4b9b037.png";

export const Hero = ({ onPlanClick, onExploreClick }) => {
  return (
    <section
      id="top"
      data-testid="hero-section"
      className="relative overflow-hidden ivory-radial"
    >
      <div
        aria-hidden
        className="absolute inset-0 opacity-[0.18] pointer-events-none mix-blend-multiply"
        style={{
          backgroundImage: `url(${sandTexture})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      />

      {/* floating decorative blobs */}
      <div
        aria-hidden
        className="absolute -top-32 -right-24 w-[520px] h-[520px] rounded-full blur-3xl opacity-50"
        style={{
          background:
            "radial-gradient(closest-side, rgba(244,220,213,0.9), transparent 70%)",
        }}
      />
      <div
        aria-hidden
        className="absolute -bottom-32 -left-24 w-[460px] h-[460px] rounded-full blur-3xl opacity-50"
        style={{
          background:
            "radial-gradient(closest-side, rgba(217,197,178,0.7), transparent 70%)",
        }}
      />

      <div className="relative max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 pt-16 pb-28 lg:pt-24 lg:pb-36">
        <div className="grid lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          <div className="lg:col-span-7 stagger">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/70 backdrop-blur border border-[#E6E4DF] text-[#4A4846]">
              <Sparkles className="w-3.5 h-3.5 text-[#D36B4A]" strokeWidth={1.6} />
              <span className="text-[0.72rem] tracking-[0.22em] uppercase font-medium">
                AI-crafted itineraries · since 2026
              </span>
            </div>

            <h1
              data-testid="hero-headline"
              className="mt-8 font-display text-[2.85rem] sm:text-6xl lg:text-[5.25rem] leading-[1.02] tracking-tight text-[#1C1B1A] text-balance"
            >
              Travel,{" "}
              <span className="italic font-light text-[#BE5E3E]">
                thoughtfully
              </span>{" "}
              <br className="hidden sm:block" />
              composed.
            </h1>

            <p
              data-testid="hero-subhead"
              className="mt-7 text-[#4A4846] text-lg lg:text-xl max-w-2xl leading-relaxed font-light"
            >
              VacAIgent designs concierge-grade journeys around the way{" "}
              <em className="font-serif text-[1.15em] text-[#1C1B1A]">you</em>{" "}
              actually travel — your pace, your appetite, your sense of wonder.
              No spreadsheets. No tabs. Just one beautifully written plan.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-start sm:items-center gap-4">
              <button
                data-testid="hero-cta-plan"
                onClick={onPlanClick}
                className="btn-primary"
              >
                Plan my journey
                <ArrowRight className="w-4 h-4" strokeWidth={1.8} />
              </button>
              <button
                data-testid="hero-cta-examples"
                onClick={onExploreClick}
                className="btn-ghost"
              >
                See example trips
              </button>
            </div>

            <div className="mt-12 flex items-center gap-7 text-[#7A7671] text-sm">
              <div className="flex -space-x-2">
                {["#D36B4A", "#D9C5B2", "#1C1B1A"].map((c, i) => (
                  <span
                    key={i}
                    className="w-8 h-8 rounded-full border-2 border-[#FAF9F6]"
                    style={{ backgroundColor: c }}
                  />
                ))}
              </div>
              <p className="leading-snug">
                Trusted by 12,400+ slow travelers,{" "}
                <br className="sm:hidden" />
                couples & curious minds.
              </p>
            </div>
          </div>

          {/* Hero image panel */}
          <motion.div
            initial={{ opacity: 0, y: 30, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
            className="lg:col-span-5 relative"
            data-testid="hero-visual"
          >
            <div className="relative">
              <div className="frame-inset rotate-[1.5deg] hover:rotate-0 transition-transform duration-700">
                <img
                  src={heroImage}
                  alt="Sun-drenched Mediterranean villa at golden hour"
                  className="w-full h-[460px] lg:h-[560px] object-cover"
                />
              </div>

              <div className="absolute -bottom-8 -left-6 sm:-left-10 w-60 sm:w-72 bg-white rounded-3xl shadow-soft-lg border border-[#E6E4DF] p-5 animate-float-slow">
                <div className="uppercase-eyebrow text-[#D36B4A]">
                  Day 03 · Positano
                </div>
                <div className="font-display text-2xl text-[#1C1B1A] mt-2 leading-snug">
                  Lemon orchard lunch, then a quiet boat to Li Galli.
                </div>
                <div className="mt-3 flex items-center gap-2 text-xs text-[#7A7671]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#D36B4A]" />
                  Crafted in 8 seconds
                </div>
              </div>

              <div className="absolute -top-6 -right-4 sm:-right-8 w-44 bg-[#1C1B1A] text-[#FAF9F6] rounded-2xl p-4 shadow-soft-lg">
                <div className="uppercase-eyebrow text-[#D9C5B2]">Pace</div>
                <div className="font-display text-3xl mt-1.5">Slow & curious</div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
