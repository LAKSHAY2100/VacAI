import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const phrases = [
  "Curating destinations…",
  "Consulting local guides…",
  "Mapping golden-hour windows…",
  "Choosing tables worth waiting for…",
  "Composing your travel brief…",
  "Finalizing your itinerary…",
];

export const LoadingState = () => {
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    const t = setInterval(() => {
      setIdx((i) => (i + 1) % phrases.length);
    }, 1800);
    return () => clearInterval(t);
  }, []);

  return (
    <section
      data-testid="loading-state"
      className="bg-[#FAF9F6]"
    >
      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-20 lg:py-28">
        <div className="relative bg-white border border-[#E6E4DF] rounded-[2rem] p-10 sm:p-14 lg:p-20 shadow-soft overflow-hidden">
          <div
            aria-hidden
            className="absolute inset-0 pointer-events-none opacity-60"
            style={{
              background:
                "radial-gradient(700px 300px at 20% 10%, rgba(244,220,213,0.7), transparent 60%), radial-gradient(600px 280px at 90% 90%, rgba(217,197,178,0.4), transparent 60%)",
            }}
          />
          <div className="relative">
            <div className="uppercase-eyebrow text-[#D36B4A]">In composition</div>
            <h2 className="mt-4 font-display text-4xl sm:text-5xl lg:text-6xl tracking-tight text-[#1C1B1A] leading-[1.05] text-balance">
              Quiet hands at work.
            </h2>
            <p className="mt-6 max-w-xl text-[#4A4846] text-lg font-light leading-relaxed">
              A team of agents is reading the city, listening for the right
              hour, and choosing what's worth your time.
            </p>

            <div className="mt-12 flex items-center gap-4">
              <div className="relative w-10 h-10">
                <span className="absolute inset-0 rounded-full border border-[#D36B4A]/30" />
                <span className="absolute inset-0 rounded-full border-t-2 border-[#D36B4A] animate-spin" style={{ animationDuration: "2.4s" }} />
                <span className="absolute inset-3 rounded-full bg-[#D36B4A]" />
              </div>
              <AnimatePresence mode="wait">
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  transition={{ duration: 0.4 }}
                  className="font-display text-2xl sm:text-3xl text-[#1C1B1A]"
                  data-testid="loading-phrase"
                >
                  {phrases[idx]}
                </motion.div>
              </AnimatePresence>
            </div>

            <div className="mt-10 grid sm:grid-cols-3 gap-4">
              {["Destination research", "Day pacing", "Hidden gems"].map(
                (label, i) => (
                  <div
                    key={label}
                    className="rounded-2xl border border-[#F0EFEB] bg-[#FAF9F6] p-5"
                  >
                    <div className="uppercase-eyebrow">Step {i + 1}</div>
                    <div className="mt-2 font-display text-xl text-[#1C1B1A]">
                      {label}
                    </div>
                    <div className="mt-4 h-1 rounded-full bg-[#F0EFEB] overflow-hidden">
                      <motion.div
                        className="h-full bg-[#D36B4A]"
                        initial={{ width: "10%" }}
                        animate={{ width: ["10%", "90%", "60%", "100%"] }}
                        transition={{
                          duration: 3.6,
                          repeat: Infinity,
                          delay: i * 0.4,
                          ease: "easeInOut",
                        }}
                      />
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default LoadingState;
