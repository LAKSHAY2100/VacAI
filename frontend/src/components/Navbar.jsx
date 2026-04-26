import React from "react";
import { Compass } from "lucide-react";

export const Navbar = ({ onPlanClick }) => {
  return (
    <header
      data-testid="site-navbar"
      className="sticky top-0 z-40 w-full backdrop-blur-md bg-[#FAF9F6]/75 border-b border-[#E6E4DF]/70"
    >
      <nav className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 h-20 flex items-center justify-between">
        <a
          href="#top"
          data-testid="brand-link"
          className="flex items-center gap-3 group"
        >
          <span className="w-9 h-9 rounded-full bg-[#1C1B1A] text-[#FAF9F6] flex items-center justify-center transition-transform duration-500 group-hover:rotate-[18deg]">
            <Compass className="w-4 h-4" strokeWidth={1.5} />
          </span>
          <div className="leading-none">
            <div className="font-display text-2xl tracking-tight text-[#1C1B1A]">
              VacAIgent
            </div>
            <div className="uppercase-eyebrow mt-0.5">
              Concierge · Intelligently composed
            </div>
          </div>
        </a>

        <div className="hidden md:flex items-center gap-10 text-sm text-[#4A4846]">
          <a
            href="#journeys"
            data-testid="nav-journeys"
            className="hover:text-[#1C1B1A] transition-colors"
          >
            Journeys
          </a>
          <a
            href="#how-it-works"
            data-testid="nav-how"
            className="hover:text-[#1C1B1A] transition-colors"
          >
            How it works
          </a>
          <a
            href="#planner"
            data-testid="nav-planner"
            className="hover:text-[#1C1B1A] transition-colors"
          >
            Planner
          </a>
        </div>

        <button
          data-testid="nav-cta-plan-trip"
          onClick={onPlanClick}
          className="btn-primary text-sm py-2.5 px-5"
        >
          Plan a trip
          <span aria-hidden="true">→</span>
        </button>
      </nav>
    </header>
  );
};

export default Navbar;
