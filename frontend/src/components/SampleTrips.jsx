import React from "react";
import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import { sampleTrips } from "../lib/sample-trips";

export const SampleTrips = ({ onSelect }) => {
  return (
    <section
      id="journeys"
      data-testid="sample-trips-section"
      className="relative bg-[#FAF9F6]"
    >
      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-24 lg:py-32">
        <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-8 mb-14">
          <div className="max-w-2xl">
            <div className="uppercase-eyebrow">Curated example journeys</div>
            <h2 className="mt-4 font-display text-4xl sm:text-5xl lg:text-6xl tracking-tight text-[#1C1B1A] leading-[1.05] text-balance">
              A starting point,
              <br />
              not a template.
            </h2>
          </div>
          <p className="lg:max-w-md text-[#4A4846] text-lg font-light leading-relaxed">
            Pick a journey that resonates and we’ll prefill the planner — then
            shape it to your own pace, taste, and travelers.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-7 lg:gap-9">
          {sampleTrips.map((trip, i) => (
            <motion.button
              key={trip.id}
              data-testid={`sample-trip-${trip.id}`}
              onClick={() => onSelect(trip)}
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{
                duration: 0.7,
                ease: [0.22, 1, 0.36, 1],
                delay: i * 0.1,
              }}
              whileHover={{ y: -6 }}
              className="group text-left bg-white rounded-3xl border border-[#E6E4DF] p-5 shadow-soft hover:shadow-soft-lg transition-shadow duration-500 cursor-pointer"
            >
              <div className="overflow-hidden rounded-2xl">
                <img
                  src={trip.image}
                  alt={trip.title}
                  className="w-full h-64 object-cover transition-transform duration-[1.4s] group-hover:scale-[1.06]"
                />
              </div>
              <div className="px-2 pt-6 pb-2">
                <div className="flex items-center justify-between">
                  <div className="uppercase-eyebrow">{trip.region}</div>
                  <div className="text-[#7A7671] text-xs">{trip.nights}</div>
                </div>
                <h3 className="font-display text-3xl text-[#1C1B1A] mt-3 leading-tight">
                  {trip.title}
                </h3>
                <p className="text-[#4A4846] mt-3 leading-relaxed font-light">
                  {trip.tagline}
                </p>
                <div className="mt-6 flex items-center gap-2 text-[#D36B4A] font-medium text-sm group-hover:gap-3 transition-all duration-300">
                  Use this as a draft
                  <ArrowUpRight className="w-4 h-4" strokeWidth={1.8} />
                </div>
              </div>
            </motion.button>
          ))}
        </div>
      </div>
    </section>
  );
};

export default SampleTrips;
