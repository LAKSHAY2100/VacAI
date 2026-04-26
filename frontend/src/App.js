import React, { useEffect, useRef, useState } from "react";
import "@/App.css";
import axios from "axios";
import { addDays } from "date-fns";

import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import SampleTrips from "./components/SampleTrips";
import FeatureStrip from "./components/FeatureStrip";
import PlannerForm from "./components/PlannerForm";
import LoadingState from "./components/LoadingState";
import ResultsPanel from "./components/ResultsPanel";
import ErrorState from "./components/ErrorState";
import Footer from "./components/Footer";
import { Toaster } from "./components/ui/sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [itinerary, setItinerary] = useState("");
  const [meta, setMeta] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [initialValues, setInitialValues] = useState(null);

  const plannerRef = useRef(null);
  const resultsRef = useRef(null);
  const journeysRef = useRef(null);

  const scrollTo = (target) => {
    const el = document.getElementById(target);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const handleSelectSample = (trip) => {
    const start = addDays(new Date(), 21);
    const end = addDays(start, trip.prefill.duration - 1);
    setInitialValues({
      origin: trip.prefill.origin,
      destination: trip.prefill.destination,
      interests: trip.prefill.interests,
      startDate: start,
      endDate: end,
    });
    setStatus("idle");
    setItinerary("");
    setTimeout(() => scrollTo("planner"), 80);
  };

  const handleSubmit = async (payload) => {
    setStatus("loading");
    setErrorMessage("");
    setItinerary("");
    setMeta({
      origin: payload.origin,
      destination: payload.destination,
      start_date: payload.start_date,
      end_date: payload.end_date,
    });
    setTimeout(() => scrollTo("results"), 100);
    try {
      const res = await axios.post(`${API}/v1/plan-trip`, payload, {
        headers: { "Content-Type": "application/json" },
      });
      const data = res.data;
      // simulate elegant minimum compose duration
      await new Promise((r) => setTimeout(r, 1400));
      if (data.status === "success" && data.itinerary) {
        setItinerary(data.itinerary);
        setStatus("success");
        setTimeout(() => scrollTo("results"), 80);
      } else {
        setErrorMessage(data.error || data.message || "Unable to compose your itinerary.");
        setStatus("error");
      }
    } catch (e) {
      const detail =
        e?.response?.data?.detail ||
        e?.response?.data?.error ||
        e?.message ||
        "Network hiccup. Please try again.";
      setErrorMessage(typeof detail === "string" ? detail : "Unable to compose your itinerary.");
      setStatus("error");
    }
  };

  useEffect(() => {
    // Lightweight ping (kept from template)
    axios.get(`${API}/`).catch(() => {});
  }, []);

  return (
    <div className="App min-h-screen bg-[#FAF9F6] text-[#1C1B1A]">
      <Navbar onPlanClick={() => scrollTo("planner")} />

      <main>
        <Hero
          onPlanClick={() => scrollTo("planner")}
          onExploreClick={() => scrollTo("journeys")}
        />

        <div ref={journeysRef}>
          <SampleTrips onSelect={handleSelectSample} />
        </div>

        <FeatureStrip />

        <div ref={plannerRef}>
          <PlannerForm
            initialValues={initialValues}
            onSubmit={handleSubmit}
            isLoading={status === "loading"}
          />
        </div>

        <div ref={resultsRef} id="results-anchor">
          {status === "loading" ? <LoadingState /> : null}
          {status === "success" && itinerary ? (
            <ResultsPanel
              itinerary={itinerary}
              meta={meta}
              onReset={() => {
                setStatus("idle");
                setItinerary("");
                setMeta(null);
                scrollTo("planner");
              }}
            />
          ) : null}
          {status === "error" ? (
            <ErrorState
              message={errorMessage}
              onRetry={() => {
                setStatus("idle");
                setErrorMessage("");
                scrollTo("planner");
              }}
            />
          ) : null}
        </div>
      </main>

      <Footer />
      <Toaster richColors position="top-center" />
    </div>
  );
};

export default App;
