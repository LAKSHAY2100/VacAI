import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Bot,
  CalendarCheck,
  Download,
  Loader2,
  PencilLine,
  RotateCcw,
  Send,
  Sparkles,
  User,
} from "lucide-react";

export const ResultsPanel = ({
  itinerary,
  meta,
  chatMessages = [],
  isRefining = false,
  onRefine,
  onReset,
  clarification = null,
}) => {
  const [input, setInput] = useState("");
  const [actionMode, setActionMode] = useState(null); // null | update | bookings
  const chatEndRef = useRef(null);
  const showUpdateChat = actionMode === "update" || !!clarification?.message;
  const showBookingsPlaceholder = actionMode === "bookings" && !clarification?.message;

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, isRefining]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isRefining) return;
    setInput("");
    onRefine?.(trimmed);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

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
                    <span className="text-[#D9C5B2]">.</span>
                    <span>
                      {meta.start_date} to {meta.end_date}
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
              Composed by VacAIgent. Adjust freely. Bookings sold separately.
            </p>
          </div>

          <div className="border-t border-[#F0EFEB] px-8 sm:px-12 lg:px-16 py-8">
            {!showUpdateChat && !showBookingsPlaceholder ? (
              <div>
                <h3 className="uppercase-eyebrow text-[#7A7671] mb-5 flex items-center gap-2 text-xs tracking-[0.18em]">
                  <Sparkles className="w-3.5 h-3.5 text-[#D36B4A]" strokeWidth={1.6} />
                  What would you like to do next?
                </h3>
                <div className="grid sm:grid-cols-2 gap-3">
                  <button
                    type="button"
                    data-testid="start-bookings"
                    onClick={() => setActionMode("bookings")}
                    className="group flex items-center justify-between gap-4 rounded-2xl border border-[#E6E4DF] bg-[#FAF9F6] px-5 py-4 text-left transition-all hover:border-[#D36B4A]/50 hover:bg-[#FDF0EB]"
                  >
                    <span>
                      <span className="block text-sm font-medium text-[#1C1B1A]">
                        Start with bookings
                      </span>
                      <span className="mt-1 block text-xs leading-relaxed text-[#7A7671]">
                        Flights and stays flow will connect here.
                      </span>
                    </span>
                    <CalendarCheck className="h-5 w-5 flex-shrink-0 text-[#D36B4A]" strokeWidth={1.7} />
                  </button>
                  <button
                    type="button"
                    data-testid="update-itinerary"
                    onClick={() => setActionMode("update")}
                    className="group flex items-center justify-between gap-4 rounded-2xl border border-[#E6E4DF] bg-[#FAF9F6] px-5 py-4 text-left transition-all hover:border-[#D36B4A]/50 hover:bg-[#FDF0EB]"
                  >
                    <span>
                      <span className="block text-sm font-medium text-[#1C1B1A]">
                        Update itinerary
                      </span>
                      <span className="mt-1 block text-xs leading-relaxed text-[#7A7671]">
                        Tell the planner what to change.
                      </span>
                    </span>
                    <PencilLine className="h-5 w-5 flex-shrink-0 text-[#D36B4A]" strokeWidth={1.7} />
                  </button>
                </div>
              </div>
            ) : null}

            {showBookingsPlaceholder ? (
              <div>
                <h3 className="uppercase-eyebrow text-[#7A7671] mb-4 flex items-center gap-2 text-xs tracking-[0.18em]">
                  <CalendarCheck className="w-3.5 h-3.5 text-[#D36B4A]" strokeWidth={1.6} />
                  Start with bookings
                </h3>
                <div className="rounded-2xl border border-[#E6E4DF] bg-[#FAF9F6] px-5 py-4">
                  <p className="text-sm text-[#4A4846]">
                    Booking support is not connected yet. Your itinerary is ready when this flow is added.
                  </p>
                  <button
                    type="button"
                    onClick={() => setActionMode(null)}
                    className="mt-4 text-sm font-medium text-[#BE5E3E] hover:text-[#1C1B1A]"
                  >
                    Back to options
                  </button>
                </div>
              </div>
            ) : null}

            {showUpdateChat ? (
              <div>
                <h3 className="uppercase-eyebrow text-[#7A7671] mb-4 flex items-center gap-2 text-xs tracking-[0.18em]">
                  <Bot className="w-3.5 h-3.5 text-[#D36B4A]" strokeWidth={1.6} />
                  {clarification?.message ? "Answer a quick flight question" : "Update itinerary"}
                </h3>
                <p className="mb-4 text-sm text-[#7A7671] max-w-2xl">
                  {clarification?.message
                    ? "Flight recommendations need one more detail before we can search live inventory."
                    : "Tell us what you want to change, and we will update the itinerary."}
                </p>

                {chatMessages.length > 0 ? (
                  <div className="mb-4 max-h-64 overflow-y-auto space-y-3 pr-1">
                    {chatMessages.map((msg, i) => (
                      <div
                        key={i}
                        className={`flex items-start gap-2.5 ${
                          msg.role === "user" ? "justify-end" : "justify-start"
                        }`}
                      >
                        {msg.role === "assistant" ? (
                          <span className="mt-0.5 flex-shrink-0 w-6 h-6 rounded-full bg-[#FDF0EB] flex items-center justify-center">
                            <Bot className="w-3.5 h-3.5 text-[#D36B4A]" strokeWidth={1.6} />
                          </span>
                        ) : null}
                        <div
                          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed max-w-[80%] ${
                            msg.role === "user"
                              ? "bg-[#1C1B1A] text-white"
                              : "bg-[#F5F4F1] text-[#1C1B1A]"
                          }`}
                        >
                          {msg.content}
                        </div>
                        {msg.role === "user" ? (
                          <span className="mt-0.5 flex-shrink-0 w-6 h-6 rounded-full bg-[#1C1B1A] flex items-center justify-center">
                            <User className="w-3.5 h-3.5 text-white" strokeWidth={1.6} />
                          </span>
                        ) : null}
                      </div>
                    ))}
                    {isRefining ? (
                      <div className="flex items-start gap-2.5 justify-start">
                        <span className="mt-0.5 flex-shrink-0 w-6 h-6 rounded-full bg-[#FDF0EB] flex items-center justify-center">
                          <Bot className="w-3.5 h-3.5 text-[#D36B4A]" strokeWidth={1.6} />
                        </span>
                        <div className="rounded-2xl px-4 py-2.5 text-sm bg-[#F5F4F1] text-[#7A7671] flex items-center gap-2">
                          <Loader2 className="w-3.5 h-3.5 animate-spin" strokeWidth={1.6} />
                          Refining your itinerary...
                        </div>
                      </div>
                    ) : null}
                    <div ref={chatEndRef} />
                  </div>
                ) : null}

                <div className="flex items-center gap-3">
                  <input
                    data-testid="refine-input"
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={isRefining}
                    placeholder={
                      clarification?.message
                        ? "Reply with a city or 3-letter airport code..."
                        : "e.g. Make day 3 more adventurous, add budget restaurants..."
                    }
                    className="flex-1 input-premium text-sm disabled:opacity-50"
                  />
                  <button
                    data-testid="refine-send"
                    onClick={handleSend}
                    disabled={!input.trim() || isRefining}
                    className="flex-shrink-0 w-10 h-10 rounded-xl bg-[#1C1B1A] text-white flex items-center justify-center transition-opacity disabled:opacity-30 hover:opacity-80"
                  >
                    {isRefining ? (
                      <Loader2 className="w-4 h-4 animate-spin" strokeWidth={1.6} />
                    ) : (
                      <Send className="w-4 h-4" strokeWidth={1.6} />
                    )}
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default ResultsPanel;
