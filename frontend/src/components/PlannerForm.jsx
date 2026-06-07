import React, { useState, useEffect, forwardRef } from "react";
import { motion } from "framer-motion";
import { format } from "date-fns";
import { CalendarIcon, ArrowRight, MapPin, Plane, Heart } from "lucide-react";
import { Calendar } from "./ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import { cn } from "../lib/utils";

const Field = ({ label, hint, icon: Icon, children, testId }) => (
  <div data-testid={testId} className="flex flex-col gap-2.5">
    <label className="flex items-center gap-2 uppercase-eyebrow text-[#7A7671]">
      {Icon ? <Icon className="w-3.5 h-3.5 text-[#D36B4A]" strokeWidth={1.6} /> : null}
      {label}
      {hint ? (
        <span className="ml-2 text-[10px] tracking-normal text-[#9C9892] normal-case">
          {hint}
        </span>
      ) : null}
    </label>
    {children}
  </div>
);

const DateButton = forwardRef(function DateButton(
  { value, placeholder, error, ...rest },
  ref
) {
  return (
    <button
      type="button"
      ref={ref}
      {...rest}
      className={cn(
        "input-premium w-full flex items-center justify-between text-left",
        error && "border-[#BE5E3E] ring-2 ring-[#D36B4A]/15"
      )}
    >
      <span className={cn(value ? "text-[#1C1B1A]" : "text-[#9C9892]")}>
        {value ? format(value, "EEE, MMM d, yyyy") : placeholder}
      </span>
      <CalendarIcon className="w-4 h-4 text-[#7A7671]" strokeWidth={1.6} />
    </button>
  );
});

export const PlannerForm = ({ initialValues, onSubmit, isLoading }) => {
  const maptilerApiKey = process.env.REACT_APP_MAPTILER_API_KEY || "";
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [startDate, setStartDate] = useState(undefined);
  const [endDate, setEndDate] = useState(undefined);
  const [interests, setInterests] = useState("");
  const [errors, setErrors] = useState({});
  const [originSuggestions, setOriginSuggestions] = useState([]);
  const [destinationSuggestions, setDestinationSuggestions] = useState([]);

  useEffect(() => {
    if (!initialValues) return;
    if (initialValues.origin !== undefined) setOrigin(initialValues.origin);
    if (initialValues.destination !== undefined)
      setDestination(initialValues.destination);
    if (initialValues.interests !== undefined)
      setInterests(initialValues.interests);
    if (initialValues.startDate) setStartDate(initialValues.startDate);
    if (initialValues.endDate) setEndDate(initialValues.endDate);
  }, [initialValues]);

  useEffect(() => {
    if (!maptilerApiKey || origin.trim().length < 2) {
      setOriginSuggestions([]);
      return undefined;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(async () => {
      try {
        const endpoint = `https://api.maptiler.com/geocoding/${encodeURIComponent(
          origin.trim()
        )}.json?key=${maptilerApiKey}&autocomplete=true&limit=5&language=en`;
        const response = await fetch(endpoint, { signal: controller.signal });
        if (!response.ok) return;
        const data = await response.json();
        const suggestions = (data?.features || [])
          .map((feature) => feature.place_name || feature.text || "")
          .filter(Boolean);
        setOriginSuggestions(suggestions);
      } catch (error) {
        if (error.name !== "AbortError") {
          setOriginSuggestions([]);
        }
      }
    }, 250);

    return () => {
      controller.abort();
      clearTimeout(timeoutId);
    };
  }, [origin, maptilerApiKey]);

  useEffect(() => {
    if (!maptilerApiKey || destination.trim().length < 2) {
      setDestinationSuggestions([]);
      return undefined;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(async () => {
      try {
        const endpoint = `https://api.maptiler.com/geocoding/${encodeURIComponent(
          destination.trim()
        )}.json?key=${maptilerApiKey}&autocomplete=true&limit=5&language=en`;
        const response = await fetch(endpoint, { signal: controller.signal });
        if (!response.ok) return;
        const data = await response.json();
        const suggestions = (data?.features || [])
          .map((feature) => feature.place_name || feature.text || "")
          .filter(Boolean);
        setDestinationSuggestions(suggestions);
      } catch (error) {
        if (error.name !== "AbortError") {
          setDestinationSuggestions([]);
        }
      }
    }, 250);

    return () => {
      controller.abort();
      clearTimeout(timeoutId);
    };
  }, [destination, maptilerApiKey]);

  const validate = () => {
    const e = {};
    if (!origin.trim()) e.origin = "Tell us where you're flying from.";
    if (!destination.trim()) e.destination = "A destination, please.";
    if (!startDate) e.startDate = "Pick a start date.";
    if (!endDate) e.endDate = "Pick an end date.";
    if (startDate && endDate && endDate < startDate)
      e.endDate = "End date can't be before the start date.";
    if (!interests.trim() || interests.trim().length < 8)
      e.interests = "A short note on interests helps us craft your trip.";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!validate()) return;
    onSubmit({
      origin: origin.trim(),
      destination: destination.trim(),
      start_date: format(startDate, "yyyy-MM-dd"),
      end_date: format(endDate, "yyyy-MM-dd"),
      interests: interests.trim(),
    });
  };

  return (
    <section
      id="planner"
      data-testid="planner-section"
      className="bg-[#FAF9F6] relative"
    >
      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-24 lg:py-32">
        <div className="grid lg:grid-cols-12 gap-12 lg:gap-16 items-start">
          <motion.div
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="lg:col-span-4 lg:sticky lg:top-28"
          >
            <div className="uppercase-eyebrow">Plan your trip</div>
            <h2 className="mt-4 font-display text-4xl sm:text-5xl lg:text-[3.6rem] tracking-tight text-[#1C1B1A] leading-[1.05] text-balance">
              Tell us a little.
              <br />
              <span className="italic font-light text-[#BE5E3E]">
                We'll do the rest.
              </span>
            </h2>
            <p className="mt-6 text-[#4A4846] text-lg font-light leading-relaxed">
              Five quiet inputs. One beautifully composed plan. No accounts, no
              clutter — just the journey.
            </p>

            <div className="mt-10 hidden lg:flex flex-col gap-3 text-[#4A4846] text-sm">
              {[
                "Validated dates & destinations",
                "Interest-aware day pacing",
                "Markdown-ready travel brief",
              ].map((line) => (
                <div key={line} className="flex items-center gap-3">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#D36B4A]" />
                  {line}
                </div>
              ))}
            </div>
          </motion.div>

          <motion.form
            data-testid="planner-form"
            onSubmit={handleSubmit}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{
              duration: 0.8,
              delay: 0.1,
              ease: [0.22, 1, 0.36, 1],
            }}
            className="lg:col-span-8 bg-white border border-[#E6E4DF] rounded-[2rem] p-8 sm:p-10 lg:p-12 shadow-soft"
          >
            <div className="grid sm:grid-cols-2 gap-6 lg:gap-7">
              <Field label="Origin" icon={Plane} testId="field-origin">
                <input
                  data-testid="input-origin"
                  type="text"
                  list="origin-location-suggestions"
                  value={origin}
                  onChange={(e) => setOrigin(e.target.value)}
                  placeholder="Bangalore, India"
                  className={cn(
                    "input-premium w-full",
                    errors.origin && "border-[#BE5E3E] ring-2 ring-[#D36B4A]/15"
                  )}
                  autoComplete="off"
                />
                <datalist id="origin-location-suggestions">
                  {originSuggestions.map((item) => (
                    <option key={item} value={item} />
                  ))}
                </datalist>
                {maptilerApiKey ? (
                  <span className="text-[11px] text-[#9C9892]">
                    Search with MapTiler location suggestions.
                  </span>
                ) : (
                  <span className="text-[11px] text-[#9C9892]">
                    Add `REACT_APP_MAPTILER_API_KEY` in `.env` to enable map suggestions.
                  </span>
                )}
                {errors.origin ? (
                  <span data-testid="error-origin" className="text-xs text-[#BE5E3E]">
                    {errors.origin}
                  </span>
                ) : null}
              </Field>

              <Field label="Destination" icon={MapPin} testId="field-destination">
                <input
                  data-testid="input-destination"
                  type="text"
                  list="destination-location-suggestions"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  placeholder="Krabi, Thailand"
                  className={cn(
                    "input-premium w-full",
                    errors.destination &&
                      "border-[#BE5E3E] ring-2 ring-[#D36B4A]/15"
                  )}
                  autoComplete="off"
                />
                <datalist id="destination-location-suggestions">
                  {destinationSuggestions.map((item) => (
                    <option key={item} value={item} />
                  ))}
                </datalist>
                {maptilerApiKey ? (
                  <span className="text-[11px] text-[#9C9892]">
                    Search with MapTiler location suggestions.
                  </span>
                ) : (
                  <span className="text-[11px] text-[#9C9892]">
                    Add `REACT_APP_MAPTILER_API_KEY` in `.env` to enable map suggestions.
                  </span>
                )}
                {errors.destination ? (
                  <span data-testid="error-destination" className="text-xs text-[#BE5E3E]">
                    {errors.destination}
                  </span>
                ) : null}
              </Field>

              <Field
                label="Start date"
                icon={CalendarIcon}
                testId="field-start-date"
              >
                <Popover>
                  <PopoverTrigger asChild>
                    <DateButton
                      data-testid="input-start-date"
                      value={startDate}
                      placeholder="Select departure"
                      error={!!errors.startDate}
                    />
                  </PopoverTrigger>
                  <PopoverContent
                    align="start"
                    className="w-auto p-0 rounded-2xl border-[#E6E4DF] shadow-soft-lg"
                  >
                    <Calendar
                      mode="single"
                      selected={startDate}
                      onSelect={(d) => {
                        setStartDate(d);
                        if (endDate && d && endDate < d) setEndDate(undefined);
                      }}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
                {errors.startDate ? (
                  <span
                    data-testid="error-start-date"
                    className="text-xs text-[#BE5E3E]"
                  >
                    {errors.startDate}
                  </span>
                ) : null}
              </Field>

              <Field
                label="End date"
                icon={CalendarIcon}
                testId="field-end-date"
              >
                <Popover>
                  <PopoverTrigger asChild>
                    <DateButton
                      data-testid="input-end-date"
                      value={endDate}
                      placeholder="Select return"
                      error={!!errors.endDate}
                    />
                  </PopoverTrigger>
                  <PopoverContent
                    align="start"
                    className="w-auto p-0 rounded-2xl border-[#E6E4DF] shadow-soft-lg"
                  >
                    <Calendar
                      mode="single"
                      selected={endDate}
                      onSelect={setEndDate}
                      disabled={(d) => (startDate ? d < startDate : false)}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
                {errors.endDate ? (
                  <span
                    data-testid="error-end-date"
                    className="text-xs text-[#BE5E3E]"
                  >
                    {errors.endDate}
                  </span>
                ) : null}
              </Field>

              <div className="sm:col-span-2">
                <Field
                  label="Interests & travelers"
                  icon={Heart}
                  hint="The more we know, the better the brief."
                  testId="field-interests"
                >
                  <textarea
                    data-testid="input-interests"
                    value={interests}
                    onChange={(e) => setInterests(e.target.value)}
                    placeholder="2 adults who love swimming, dancing, hiking, shopping, local food, water sports adventures and rock climbing"
                    rows={5}
                    className={cn(
                      "w-full bg-white border border-[#E6E4DF] rounded-2xl px-5 py-4 text-[#1C1B1A] placeholder:text-[#9C9892] focus:outline-none focus:border-[#D36B4A] focus:ring-4 focus:ring-[#D36B4A]/15 transition-all duration-300 resize-none font-light",
                      errors.interests &&
                        "border-[#BE5E3E] ring-2 ring-[#D36B4A]/15"
                    )}
                  />
                  {errors.interests ? (
                    <span
                      data-testid="error-interests"
                      className="text-xs text-[#BE5E3E]"
                    >
                      {errors.interests}
                    </span>
                  ) : null}
                </Field>
              </div>
            </div>

            <div className="mt-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-5 pt-8 border-t border-[#F0EFEB]">
              <p className="text-[#7A7671] text-sm leading-relaxed max-w-md">
                Composing usually takes about{" "}
                <span className="text-[#1C1B1A] font-medium">8 seconds</span>.
                Your draft is fully editable.
              </p>
              <button
                type="submit"
                data-testid="submit-trip-btn"
                disabled={isLoading}
                className="btn-primary disabled:opacity-60 disabled:cursor-wait"
              >
                {isLoading ? "Composing..." : "Compose my itinerary"}
                <ArrowRight className="w-4 h-4" strokeWidth={1.8} />
              </button>
            </div>
          </motion.form>
        </div>
      </div>
    </section>
  );
};

export default PlannerForm;
