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
const API = `${BACKEND_URL}api`;
const INVENTORY_HEADING = "## Flights and Hotels (Jinko MCP)";

const upsertTravelInventorySection = (currentItinerary, recommendation) => {
  const trimmedItinerary = (currentItinerary || "").trimEnd();
  const trimmedRecommendation = (recommendation || "").trim();

  if (!trimmedRecommendation) return trimmedItinerary;

  const section = `${INVENTORY_HEADING}\n${trimmedRecommendation}`;
  const headingIndex = trimmedItinerary.indexOf(INVENTORY_HEADING);

  if (headingIndex === -1) {
    return trimmedItinerary ? `${trimmedItinerary}\n\n${section}` : section;
  }

  const before = trimmedItinerary.slice(0, headingIndex).trimEnd();
  return before ? `${before}\n\n${section}` : section;
};

const App = () => {
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [itinerary, setItinerary] = useState("");
  const [meta, setMeta] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [initialValues, setInitialValues] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [isRefining, setIsRefining] = useState(false);
  const [tripId, setTripId] = useState(null);
  const [clarification, setClarification] = useState(null);

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
    setChatMessages([]);
    setTripId(null);
    setClarification(null);
    window.history.replaceState(null, "", window.location.pathname);
    setTimeout(() => scrollTo("planner"), 80);
  };

  const handleSubmit = async (payload) => {
    setStatus("loading");
    setErrorMessage("");
    setItinerary("");
    setChatMessages([]);
    setTripId(null);
    setClarification(null);
    setMeta({
      origin: payload.origin,
      destination: payload.destination,
      start_date: payload.start_date,
      end_date: payload.end_date,
      interests: payload.interests,
    });
    setTimeout(() => scrollTo("results"), 100);
    try {
      const res = await axios.post(`${API}/v1/plan-trip`, payload, {
        headers: { "Content-Type": "application/json" },
      });
      const data = res.data;
      // simulate elegant minimum compose duration
      await new Promise((r) => setTimeout(r, 1400));
      if ((data.status === "success" || data.status === "needs_clarification") && data.itinerary) {
        setItinerary(data.itinerary);
        setStatus("success");
        if (data.status === "needs_clarification" && data.clarification_message) {
          setClarification({
            field: data.clarification_field || null,
            message: data.clarification_message,
            options: data.clarification_options || [],
          });
          setChatMessages([
            {
              role: "assistant",
              content: data.clarification_message,
            },
          ]);
        } else {
          setClarification(null);
        }
        if (data.trip_id) {
          setTripId(data.trip_id);
          window.history.replaceState(null, "", `#/trip/${data.trip_id}`);
        }
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

  const handleRefine = async (message) => {
    if (!meta || !itinerary || isRefining) return;
    setIsRefining(true);
    setChatMessages((prev) => [...prev, { role: "user", content: message }]);
    try {
      if (clarification?.field) {
        const nextPayload = {
          origin: clarification.field === "origin" ? message : meta.origin,
          destination: clarification.field === "destination" ? message : meta.destination,
          start_date: meta.start_date,
          end_date: meta.end_date,
          travelers: 1,
          notes: "",
          trip_id: tripId || undefined,
        };
        const res = await axios.post(`${API}/v1/search-travel-inventory`, nextPayload, {
          headers: { "Content-Type": "application/json" },
        });
        const data = res.data;
        if (data.status === "success" && data.recommendation) {
          setItinerary((prev) => upsertTravelInventorySection(prev, data.recommendation));
          setMeta((prev) => ({
            ...(prev || {}),
            origin: nextPayload.origin,
            destination: nextPayload.destination,
          }));
          if (data.trip_id) {
            setTripId(data.trip_id);
            window.history.replaceState(null, "", `#/trip/${data.trip_id}`);
          }
          setClarification(null);
          setChatMessages((prev) => [
            ...prev,
            { role: "assistant", content: "Flight search is now using your updated route details." },
          ]);
        } else if (data.status === "needs_clarification" && data.clarification_message) {
          setMeta((prev) => ({
            ...(prev || {}),
            origin: nextPayload.origin,
            destination: nextPayload.destination,
          }));
          if (data.trip_id) {
            setTripId(data.trip_id);
            window.history.replaceState(null, "", `#/trip/${data.trip_id}`);
          }
          setClarification({
            field: data.clarification_field || null,
            message: data.clarification_message,
            options: data.clarification_options || [],
          });
          setChatMessages((prev) => [
            ...prev,
            { role: "assistant", content: data.clarification_message },
          ]);
        } else {
          setChatMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: `Could not update the route details: ${data.error || data.message || "Unknown error"}`,
            },
          ]);
        }
        return;
      }

      const res = await axios.post(
        `${API}/v1/refine-trip`,
        {
          origin: meta.origin,
          destination: meta.destination,
          start_date: meta.start_date,
          end_date: meta.end_date,
          interests: meta.interests || "",
          previous_itinerary: itinerary,
          refinement_request: message,
          trip_id: tripId || undefined,
        },
        { headers: { "Content-Type": "application/json" } }
      );
      const data = res.data;
      if (data.status === "success" && data.itinerary) {
        setItinerary(data.itinerary);
        if (data.trip_id) setTripId(data.trip_id);
        setChatMessages((prev) => [
          ...prev,
          { role: "assistant", content: "Itinerary updated with your changes." },
        ]);
      } else {
        setChatMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Could not refine: ${data.error || data.message || "Unknown error"}`,
          },
        ]);
      }
    } catch (e) {
      const detail =
        e?.response?.data?.detail ||
        e?.response?.data?.error ||
        e?.message ||
        "Something went wrong.";
      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${typeof detail === "string" ? detail : "Unable to refine."}` },
      ]);
    } finally {
      setIsRefining(false);
    }
  };

  // Load trip from URL hash on mount
  useEffect(() => {
    const loadTripFromHash = async () => {
      const hash = window.location.hash;
      const match = hash.match(/^#\/trip\/([a-f0-9]{24})$/);
      if (!match) return;
      const id = match[1];
      try {
        const res = await axios.get(`${API}/v1/trips/${id}`);
        const t = res.data;
        setTripId(t.trip_id);
        setItinerary(t.itinerary);
        setMeta({
          origin: t.origin,
          destination: t.destination,
          start_date: t.start_date,
          end_date: t.end_date,
          interests: t.interests,
        });
        setChatMessages(t.refinements || []);
        setClarification(null);
        setStatus("success");
        setTimeout(() => scrollTo("results"), 200);
      } catch {
        // Trip not found — stay on landing page
      }
    };
    loadTripFromHash();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

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
              chatMessages={chatMessages}
              isRefining={isRefining}
              onRefine={handleRefine}
              onReset={() => {
                setStatus("idle");
                setItinerary("");
                setMeta(null);
                setChatMessages([]);
                setTripId(null);
                setClarification(null);
                window.history.replaceState(null, "", window.location.pathname);
                scrollTo("planner");
              }}
              clarification={clarification}
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
