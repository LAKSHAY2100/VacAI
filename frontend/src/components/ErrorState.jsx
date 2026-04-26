import React from "react";
import { motion } from "framer-motion";
import { AlertTriangle, RotateCcw } from "lucide-react";

export const ErrorState = ({ message, onRetry }) => {
  return (
    <section data-testid="error-state" className="bg-[#FAF9F6]">
      <div className="max-w-4xl mx-auto px-6 sm:px-10 lg:px-14 py-20 lg:py-28">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          className="bg-white rounded-[2rem] border border-[#E6E4DF] p-10 sm:p-14 shadow-soft text-center"
        >
          <div className="mx-auto w-14 h-14 rounded-full bg-[#F9EAE5] text-[#BE5E3E] flex items-center justify-center">
            <AlertTriangle className="w-5 h-5" strokeWidth={1.6} />
          </div>
          <h2 className="mt-7 font-display text-4xl sm:text-5xl tracking-tight text-[#1C1B1A] leading-[1.05]">
            We hit a quiet detour.
          </h2>
          <p className="mt-5 text-[#4A4846] text-lg font-light leading-relaxed max-w-xl mx-auto">
            {message ||
              "Your itinerary couldn't be composed just now. Take a breath and try again — the plan will be worth it."}
          </p>
          <div className="mt-9 flex justify-center">
            <button
              data-testid="error-retry"
              onClick={onRetry}
              className="btn-primary"
            >
              <RotateCcw className="w-4 h-4" strokeWidth={1.8} />
              Try again
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default ErrorState;
