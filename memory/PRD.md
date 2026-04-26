# VacAIgent — Product Requirements

## Original Problem Statement
Design and build a premium, editorial-quality light-theme frontend for an AI travel planner called "VacAIgent". The experience should feel like a high-end travel brand meets a polished SaaS product — Dribbble-level presentation, practical, readable, production-ready. Users enter origin, destination, dates, and interests; the app calls a backend API that returns a personalized itinerary.

## User Choices (gathered Feb 2026)
- AI provider: **Mock backend only** — no real LLM calls (template-based markdown generator)
- Accent color: **Sunset terracotta / sand**
- Itinerary format: **Markdown** (rich formatting in results panel)
- Hero includes **sample example trips** that prefill the planner

## Brand & Aesthetic
- Archetype: Organic & Earthy + High-End Editorial Elegance
- Palette: Ivory (#FAF9F6), deep charcoal (#1C1B1A), terracotta (#D36B4A), sand (#D9C5B2)
- Typography: Cormorant Garamond (serif headings) + Outfit (sans body / UI)
- Motion: staggered fade-up entrances, hover lift, cycling text loader (no spinner)

## Core Requirements
- Single-page experience: Navbar, Hero, Sample Trips, Feature Strip, Planner, Loading, Results, Error, Footer
- Form validation: required fields + end_date >= start_date + interests min length
- API: `POST /api/v1/plan-trip` returns `{status, message, itinerary, error}`
- Markdown rendering with editorial typography, download as .md
- Light theme only, fully responsive (desktop/tablet/mobile)

## What's Been Implemented (Feb 2026)
- ✅ FastAPI mock endpoint `/api/v1/plan-trip` with personalized day-by-day markdown generator (themes rotate over up to 10 days)
- ✅ Date validation (400) + missing fields (422) + 200 happy path
- ✅ Premium hero with floating "Day 03 Positano" card, dark "Pace" tag, framed villa image, decorative blobs
- ✅ Three sample trip cards (Amalfi, Kyoto, Sahara) with hover scale, prefill into form (date prefill = today + 21d)
- ✅ Feature strip with 3 numbered cards on muted ivory band
- ✅ Premium planner form using shadcn Calendar + Popover, custom inputs, inline validation, sticky left column on desktop
- ✅ Editorial loading state with cycling phrases and animated step bars (no default spinner)
- ✅ Results panel with `prose prose-editorial` markdown rendering, download .md, plan-another reset
- ✅ Graceful error state with retry CTA
- ✅ Custom Tailwind typography variant `editorial` (terracotta marker bullets, serif headings, italic blockquote)
- ✅ Backend persists trip plans to MongoDB (best-effort)
- ✅ All interactive + critical elements have `data-testid`
- ✅ Tests: 6/6 backend, 16/16 frontend (testing agent iteration 1)

## Tech
- Frontend: React 19, Tailwind, shadcn/ui (Calendar, Popover, Sonner), framer-motion, react-markdown + remark-gfm, @tailwindcss/typography
- Backend: FastAPI, Motor (MongoDB), Pydantic v2
- Fonts: Cormorant Garamond + Outfit (Google Fonts)

## Backlog / Next
- P1: Replace mock with real LLM (Claude/GPT-5.2/Gemini via Emergent LLM key) — keep mock as fallback
- P1: Trip history endpoint + UI (data already persisted)
- P2: Save/share itinerary by URL, print stylesheet
- P2: Currency, weather forecast, flight time placeholders inside the brief
- P2: Multi-traveler personas (separate interests per traveler)
- P2: PDF export of itinerary
