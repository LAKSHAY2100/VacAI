import React from "react";
import { motion } from "framer-motion";
import { Telescope, Map, Sparkles } from "lucide-react";

const features = [
  {
    icon: Telescope,
    eyebrow: "01",
    title: "Personalized itineraries",
    body: "Tuned to your pace, taste, and travelers — not a one-size-fits-all checklist.",
  },
  {
    icon: Map,
    eyebrow: "02",
    title: "Smart destination research",
    body: "We surface the hidden bays, the right table, and the quiet hour to visit.",
  },
  {
    icon: Sparkles,
    eyebrow: "03",
    title: "CrewAI-powered planning",
    body: "A team of intelligent agents collaborates so your plan reads like a guide wrote it.",
  },
];

export const FeatureStrip = () => {
  return (
    <section
      id="how-it-works"
      data-testid="features-section"
      className="bg-[#F0EFEB] relative overflow-hidden"
    >
      <div
        aria-hidden
        className="absolute inset-0 opacity-30 pointer-events-none"
        style={{
          background:
            "radial-gradient(800px 300px at 50% 0%, rgba(217,197,178,0.45), transparent 60%)",
        }}
      />
      <div className="relative max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-24 lg:py-32">
        <div className="max-w-3xl">
          <div className="uppercase-eyebrow">Why VacAIgent</div>
          <h2 className="mt-4 font-display text-4xl sm:text-5xl lg:text-6xl tracking-tight text-[#1C1B1A] leading-[1.05] text-balance">
            Less planning.
            <span className="italic font-light text-[#BE5E3E]"> More journey.</span>
          </h2>
          <p className="mt-6 text-[#4A4846] text-lg font-light leading-relaxed max-w-2xl">
            Three quiet capabilities that, together, replace the tab graveyard
            and the half-finished spreadsheet.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 lg:gap-8 mt-16">
          {features.map((f, i) => {
            const Icon = f.icon;
            return (
              <motion.div
                key={f.title}
                data-testid={`feature-card-${i + 1}`}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-80px" }}
                transition={{
                  duration: 0.7,
                  delay: i * 0.12,
                  ease: [0.22, 1, 0.36, 1],
                }}
                className="group relative bg-[#FAF9F6] rounded-3xl border border-[#E6E4DF] p-9 lg:p-11 hover:bg-white transition-colors duration-500 hover:shadow-soft-lg shadow-soft"
              >
                <div className="flex items-start justify-between">
                  <div className="w-12 h-12 rounded-2xl bg-[#F9EAE5] text-[#BE5E3E] flex items-center justify-center transition-transform duration-500 group-hover:-rotate-6">
                    <Icon className="w-5 h-5" strokeWidth={1.5} />
                  </div>
                  <span className="font-display text-3xl text-[#D9C5B2]">
                    {f.eyebrow}
                  </span>
                </div>
                <h3 className="font-display text-3xl text-[#1C1B1A] mt-10 leading-tight">
                  {f.title}
                </h3>
                <p className="text-[#4A4846] mt-4 leading-relaxed font-light">
                  {f.body}
                </p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default FeatureStrip;
