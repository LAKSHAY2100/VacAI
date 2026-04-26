import React from "react";
import { Compass } from "lucide-react";

export const Footer = () => {
  return (
    <footer
      data-testid="site-footer"
      className="bg-[#1C1B1A] text-[#E6E4DF] mt-0"
    >
      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-20">
        <div className="grid lg:grid-cols-12 gap-10 items-start">
          <div className="lg:col-span-6">
            <div className="flex items-center gap-3">
              <span className="w-9 h-9 rounded-full bg-[#FAF9F6] text-[#1C1B1A] flex items-center justify-center">
                <Compass className="w-4 h-4" strokeWidth={1.6} />
              </span>
              <div className="font-display text-3xl text-[#FAF9F6]">
                VacAIgent
              </div>
            </div>
            <p className="mt-6 max-w-md text-[#D9C5B2] font-light leading-relaxed">
              Concierge-grade itineraries, intelligently composed. Built for
              travelers who treat a journey as a story worth telling well.
            </p>
          </div>

          <div className="lg:col-span-6 grid sm:grid-cols-3 gap-8 text-sm">
            <div>
              <div className="uppercase-eyebrow text-[#D9C5B2]">Studio</div>
              <ul className="mt-4 space-y-2 text-[#E6E4DF]">
                <li>About</li>
                <li>Journal</li>
                <li>Press</li>
              </ul>
            </div>
            <div>
              <div className="uppercase-eyebrow text-[#D9C5B2]">Travel</div>
              <ul className="mt-4 space-y-2 text-[#E6E4DF]">
                <li>Sample journeys</li>
                <li>How it works</li>
                <li>FAQ</li>
              </ul>
            </div>
            <div>
              <div className="uppercase-eyebrow text-[#D9C5B2]">Contact</div>
              <ul className="mt-4 space-y-2 text-[#E6E4DF]">
                <li>concierge@vacaigent.co</li>
                <li>Mon — Fri · 9–18 CET</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-16 pt-8 border-t border-[#4A4846]/60 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-xs text-[#9C9892]">
          <div>© {new Date().getFullYear()} VacAIgent Studio. All journeys reserved.</div>
          <div className="uppercase tracking-[0.22em]">Crafted with quiet care</div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
