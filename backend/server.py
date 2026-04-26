from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, date


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="VacAIgent API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ---- Models ----
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


class TripRequest(BaseModel):
    origin: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    start_date: str = Field(..., description="ISO date YYYY-MM-DD")
    end_date: str = Field(..., description="ISO date YYYY-MM-DD")
    interests: str = Field(..., min_length=1)


class TripResponse(BaseModel):
    status: str
    message: str
    itinerary: Optional[str] = None
    error: Optional[str] = None


# ---- Status routes (kept for template compatibility) ----
@api_router.get("/")
async def root():
    return {"message": "VacAIgent API is running"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(**input.model_dump())
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check.get('timestamp'), str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks


# ---- Mock Itinerary Generator ----
def _format_long_date(d: date) -> str:
    return d.strftime("%a, %b %d, %Y")


def _interest_tags(interests: str) -> List[str]:
    raw = [t.strip() for t in interests.replace(";", ",").split(",")]
    return [t for t in raw if t][:6]


def _craft_itinerary(req: TripRequest) -> str:
    start = date.fromisoformat(req.start_date)
    end = date.fromisoformat(req.end_date)
    days = (end - start).days + 1

    tags = _interest_tags(req.interests)
    tags_line = " · ".join(tags) if tags else "Curated experiences"

    dest = req.destination.strip()
    origin = req.origin.strip()

    # Day theme rotation
    themes = [
        ("Arrival & First Light", "Settle into your stay and unwind with a slow, golden-hour walk through the heart of the city."),
        ("Cultural Pulse", "Wander through landmark neighborhoods, museums, and hidden lanes filled with stories."),
        ("Coastal & Nature Day", "A guided escape into nature — coastline, cliffs, or quiet trails — with a curated picnic."),
        ("Local Flavors", "Hands-on experience with a local chef, market tour, and a long, lingering tasting menu."),
        ("Adventure Highlight", "A signature adrenaline moment — water sports, climbing, or scenic via ferrata — booked privately."),
        ("Artisan Quarter", "Browse independent makers, galleries, and concept stores with our curated shopping list."),
        ("Hidden Gems", "Step off the map: a sunrise viewpoint, a quiet bay, and a tucked-away wine bar."),
        ("Slow Morning, Sunset Finale", "A leisurely start, spa or pool, and an unforgettable sunset dinner reservation."),
        ("Day Trip Excursion", "A scenic drive or boat ride to a neighboring village — locals only know the way."),
        ("Farewell & Reflection", "Final brunch, last-light photo walk, and seamless airport transfer."),
    ]

    lines: List[str] = []
    lines.append(f"# Your {days}-Day Journey to {dest}")
    lines.append("")
    lines.append(f"*Crafted for travelers departing from **{origin}** · {_format_long_date(start)} → {_format_long_date(end)}*")
    lines.append("")
    lines.append(f"**Trip Themes:** {tags_line}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## At a Glance")
    lines.append("")
    lines.append(f"- **Destination:** {dest}")
    lines.append(f"- **Travelers Departing From:** {origin}")
    lines.append(f"- **Duration:** {days} days · {max(days - 1, 0)} nights")
    lines.append(f"- **Pace:** Balanced — equal parts discovery, indulgence, and rest")
    lines.append(f"- **Best For:** {tags_line}")
    lines.append("")
    lines.append("> *“The best journeys are not measured in miles, but in moments. This itinerary is shaped around yours.”*")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Daily Itinerary")
    lines.append("")

    for i in range(days):
        day_num = i + 1
        d = start.fromordinal(start.toordinal() + i)
        title, blurb = themes[i % len(themes)]
        lines.append(f"### Day {day_num} · {title}")
        lines.append(f"*{_format_long_date(d)}*")
        lines.append("")
        lines.append(blurb)
        lines.append("")
        lines.append("**Morning** — A slow start with specialty coffee at a neighborhood favorite. Light walk to set the tone.")
        lines.append("")
        lines.append(f"**Afternoon** — A signature {dest} experience tailored to your love of *{tags[i % len(tags)] if tags else 'local culture'}*.")
        lines.append("")
        lines.append("**Evening** — Reservation at a quietly celebrated restaurant. Optional nightcap at a rooftop or speakeasy.")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Where to Stay")
    lines.append("")
    lines.append(f"We recommend basing yourself in a boutique stay near the heart of {dest} — small enough to feel personal, refined enough to feel like a retreat. Our team can secure preferred rates on request.")
    lines.append("")
    lines.append("## Insider Tips")
    lines.append("")
    lines.append("- Book signature dinners **at least 10 days in advance** — the most coveted tables go quickly.")
    lines.append("- Travel light on day-trip days — a linen layer, sunscreen, and water are all you truly need.")
    lines.append("- Carry a small notebook. The best memories surface in the quiet moments between plans.")
    lines.append("- Tip discreetly and generously where service is exceptional — it goes a long way.")
    lines.append("")
    lines.append("## What's Included in This Plan")
    lines.append("")
    lines.append("1. Day-by-day pacing tuned to your interests")
    lines.append("2. Curated restaurant and experience shortlists")
    lines.append("3. A balance of marquee sights and quiet local moments")
    lines.append("4. Sunset and golden-hour windows mapped to the best vantage points")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*Prepared by VacAIgent · Concierge-grade itineraries, intelligently composed.*")

    return "\n".join(lines)


@api_router.post("/v1/plan-trip", response_model=TripResponse)
async def plan_trip(req: TripRequest):
    try:
        start = date.fromisoformat(req.start_date)
        end = date.fromisoformat(req.end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if end < start:
        raise HTTPException(status_code=400, detail="end_date cannot be earlier than start_date.")

    itinerary = _craft_itinerary(req)

    # Persist (best-effort, non-blocking on failure)
    try:
        await db.trip_plans.insert_one({
            "id": str(uuid.uuid4()),
            "origin": req.origin,
            "destination": req.destination,
            "start_date": req.start_date,
            "end_date": req.end_date,
            "interests": req.interests,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        logging.getLogger(__name__).warning(f"Persist trip_plans failed: {e}")

    return TripResponse(
        status="success",
        message="Trip plan generated successfully",
        itinerary=itinerary,
        error=None,
    )


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
