from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from crewai import Crew, LLM
from trip_agents import TripAgents
from trip_tasks import TripTasks
from tools.jinko_mcp_tools import resolve_flight_endpoint_details
import os
from dotenv import load_dotenv
from functools import lru_cache
from bson import ObjectId
from database import get_trips_collection, close_client

# Load environment variables
load_dotenv()


def _clean_env(name: str, default: str = None):
    value = os.getenv(name, default)
    if value is None:
        return None
    # Normalize common .env formatting issues (extra quotes/newlines/spaces)
    return value.strip().strip('"').strip("'")

app = FastAPI(
    title="VacAIgent API",
    description="AI-powered travel planning API using CrewAI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripRequest(BaseModel):
    origin: str = Field(..., 
        json_schema_extra={"example": "Bangalore, India"},
        description="Your current location")
    destination: str = Field(..., 
        json_schema_extra={"example": "Krabi, Thailand"},
        description="City options (comma-separated) or single destination to plan")
    start_date: date = Field(..., 
        json_schema_extra={"example": "2025-06-01"},
        description="Start date of your trip")
    end_date: date = Field(..., 
        json_schema_extra={"example": "2025-06-10"},
        description="End date of your trip")
    interests: str = Field(..., 
        json_schema_extra={"example": "2 adults who love swimming, dancing, hiking, shopping, local food, water sports adventures and rock climbing"},
        description="Your interests and trip details")

class TripResponse(BaseModel):
    status: str
    message: str
    trip_id: Optional[str] = None
    itinerary: Optional[str] = None
    error: Optional[str] = None
    clarification_field: Optional[str] = None
    clarification_message: Optional[str] = None
    clarification_options: List[str] = []

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class TripDetail(BaseModel):
    trip_id: str
    origin: str
    destination: str
    start_date: str
    end_date: str
    interests: str
    itinerary: str
    refinements: List[ChatMessage] = []
    created_at: str
    updated_at: str

class RefineRequest(BaseModel):
    origin: str = Field(..., description="Your current location")
    destination: str = Field(..., description="Destination city and country")
    start_date: date = Field(..., description="Start date of your trip")
    end_date: date = Field(..., description="End date of your trip")
    interests: str = Field(..., description="Your interests and trip details")
    previous_itinerary: str = Field(..., description="The previously generated itinerary markdown")
    refinement_request: str = Field(..., description="What changes the traveler wants")
    trip_id: Optional[str] = Field(None, description="Trip ID for persistence")


class TravelInventoryRequest(BaseModel):
    origin: str = Field(..., description="Origin city or airport")
    destination: str = Field(..., description="Destination city or airport")
    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    travelers: int = Field(1, ge=1, description="Total travelers")
    notes: str = Field("", description="Budget or preferences")
    trip_id: Optional[str] = Field(None, description="Trip ID for persistence")


class RefineTravelInventoryRequest(BaseModel):
    origin: str = Field(..., description="Origin city or airport")
    destination: str = Field(..., description="Destination city or airport")
    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    travelers: int = Field(1, ge=1, description="Total travelers")
    previous_summary: str = Field("", description="Previous recommendation text")
    refinement_request: str = Field(..., description="Requested changes")
    trip_id: Optional[str] = Field(None, description="Trip ID for persistence")


class TravelInventoryResponse(BaseModel):
    status: str
    message: str
    trip_id: Optional[str] = None
    recommendation: Optional[str] = None
    disclaimer: Optional[str] = None
    source: Optional[str] = None
    error: Optional[str] = None
    clarification_field: Optional[str] = None
    clarification_message: Optional[str] = None
    clarification_options: List[str] = []


def _clarification_response_for_flights(origin: str, destination: str) -> Optional[dict]:
    checks = [
        (resolve_flight_endpoint_details(origin, "origin"), origin),
        (resolve_flight_endpoint_details(destination, "destination"), destination),
    ]
    for resolution, raw_value in checks:
        if resolution.get("needs_clarification"):
            field_name = str(resolution.get("field", "location"))
            label = "departure" if field_name == "origin" else "arrival"
            return {
                "field": field_name,
                "message": (
                    f"Flight search needs a {label} city or 3-letter airport code instead of '{raw_value}'. "
                    f"Reply with something like 'Indianapolis' or 'IND'."
                ),
                "options": [],
            }
    return None

class Settings:
    def __init__(self):
        self.OPENAI_API_KEY = _clean_env("OPENAI_API_KEY")
        self.OPENAI_MODEL = _clean_env("OPENAI_MODEL", "gpt-4o-mini")
        self.SERPER_API_KEY = _clean_env("SERPER_API_KEY")
        self.BROWSERLESS_API_KEY = _clean_env("BROWSERLESS_API_KEY")
        self.JINKO_MCP_SERVER_URL = _clean_env("JINKO_MCP_SERVER_URL", "https://mcp.builders.gojinko.com/mcp")
        self.JINKO_MCP_OAUTH_BEARER_TOKEN = _clean_env("JINKO_MCP_OAUTH_BEARER_TOKEN")

@lru_cache()
def get_settings():
    return Settings()

def validate_api_keys(settings: Settings = Depends(get_settings)):
    required_keys = {
        'OPENAI_API_KEY': settings.OPENAI_API_KEY,
        'SERPER_API_KEY': settings.SERPER_API_KEY,
        'BROWSERLESS_API_KEY': settings.BROWSERLESS_API_KEY
    }
    
    missing_keys = [key for key, value in required_keys.items() if not value]
    if missing_keys:
        raise HTTPException(
            status_code=500,
            detail=f"Missing required API keys: {', '.join(missing_keys)}"
        )
    return settings

class TripCrew:
    def __init__(self, origin, destination, date_range, interests, model_name):
        self.destination = destination
        self.origin = origin
        self.interests = interests
        self.date_range = date_range
        self.llm = LLM(model=model_name)

    async def run(self):
        try:
            agents = TripAgents(llm=self.llm)
            tasks = TripTasks()

            city_selector_agent = agents.city_selection_agent()
            local_expert_agent = agents.local_expert()
            travel_concierge_agent = agents.travel_concierge()

            identify_task = tasks.identify_task(
                city_selector_agent,
                self.origin,
                self.destination,
                self.interests,
                self.date_range
            )

            gather_task = tasks.gather_task(
                local_expert_agent,
                self.origin,
                self.interests,
                self.date_range
            )

            plan_task = tasks.plan_task(
                travel_concierge_agent,
                self.origin,
                self.interests,
                self.date_range
            )

            crew = Crew(
                agents=[
                    city_selector_agent, local_expert_agent, travel_concierge_agent
                ],
                tasks=[identify_task, gather_task, plan_task],
                verbose=True
            )

            result = await crew.kickoff_async()
            # Convert CrewOutput to string and ensure it's properly formatted
            return result.raw if hasattr(result, 'raw') else str(result)
        except Exception as x:
            raise HTTPException(
                status_code=500,
                detail=str(x)
            )

class RefineCrew:
    def __init__(self, origin, destination, date_range, interests, previous_itinerary, refinement_request, model_name):
        self.origin = origin
        self.destination = destination
        self.date_range = date_range
        self.interests = interests
        self.previous_itinerary = previous_itinerary
        self.refinement_request = refinement_request
        self.llm = LLM(model=model_name)

    async def run(self):
        try:
            agents = TripAgents(llm=self.llm)
            tasks = TripTasks()

            travel_concierge_agent = agents.travel_concierge()

            refine_task = tasks.refine_task(
                travel_concierge_agent,
                self.origin,
                self.interests,
                self.date_range,
                self.previous_itinerary,
                self.refinement_request,
            )

            crew = Crew(
                agents=[travel_concierge_agent],
                tasks=[refine_task],
                verbose=True,
            )

            result = await crew.kickoff_async()
            return result.raw if hasattr(result, 'raw') else str(result)
        except Exception as x:
            raise HTTPException(
                status_code=500,
                detail=str(x),
            )


class TravelInventoryCrew:
    def __init__(self, origin, destination, start_date, end_date, travelers, notes, model_name):
        self.origin = origin
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        self.travelers = travelers
        self.notes = notes
        self.llm = LLM(model=model_name)

    async def run(self):
        try:
            agents = TripAgents(llm=self.llm)
            tasks = TripTasks()
            inventory_agent = agents.transport_stay_concierge()
            inventory_task = tasks.travel_inventory_task(
                inventory_agent,
                self.origin,
                self.destination,
                self.start_date,
                self.end_date,
                self.travelers,
                self.notes,
            )
            crew = Crew(agents=[inventory_agent], tasks=[inventory_task], verbose=True)
            result = await crew.kickoff_async()
            return result.raw if hasattr(result, "raw") else str(result)
        except Exception as x:
            raise HTTPException(status_code=500, detail=str(x))


class RefineTravelInventoryCrew:
    def __init__(
        self,
        origin,
        destination,
        start_date,
        end_date,
        travelers,
        previous_summary,
        refinement_request,
        model_name,
    ):
        self.origin = origin
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        self.travelers = travelers
        self.previous_summary = previous_summary
        self.refinement_request = refinement_request
        self.llm = LLM(model=model_name)

    async def run(self):
        try:
            agents = TripAgents(llm=self.llm)
            tasks = TripTasks()
            inventory_agent = agents.transport_stay_concierge()
            inventory_task = tasks.refine_travel_inventory_task(
                inventory_agent,
                self.origin,
                self.destination,
                self.start_date,
                self.end_date,
                self.travelers,
                self.refinement_request,
                self.previous_summary,
            )
            crew = Crew(agents=[inventory_agent], tasks=[inventory_task], verbose=True)
            result = await crew.kickoff_async()
            return result.raw if hasattr(result, "raw") else str(result)
        except Exception as x:
            raise HTTPException(status_code=500, detail=str(x))

@app.on_event("shutdown")
async def shutdown_db():
    await close_client()

@app.get("/")
async def root():
    return {
        "message": "Welcome to VacAIgent API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.post("/api/v1/plan-trip", response_model=TripResponse)
async def plan_trip(
    trip_request: TripRequest,
    settings: Settings = Depends(validate_api_keys)
):
    # Validate dates
    if trip_request.end_date <= trip_request.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    # Format date range
    date_range = f"{trip_request.start_date} to {trip_request.end_date}"

    try:
        trip_crew = TripCrew(
            trip_request.origin,
            trip_request.destination,
            date_range,
            trip_request.interests,
            f"openai/{settings.OPENAI_MODEL}",
        )
        
        itinerary = await trip_crew.run()
        
        # Ensure itinerary is a string
        if not isinstance(itinerary, str):
            itinerary = str(itinerary)

        clarification = _clarification_response_for_flights(
            trip_request.origin,
            trip_request.destination,
        )

        # Enrich the itinerary with flights/hotels recommendations from Jinko MCP.
        travel_inventory = None
        if not clarification:
            try:
                inventory_crew = TravelInventoryCrew(
                    trip_request.origin,
                    trip_request.destination,
                    str(trip_request.start_date),
                    str(trip_request.end_date),
                    1,
                    "",  # Budget/preference notes (empty if not specified)
                    f"openai/{settings.OPENAI_MODEL}",
                )
                travel_inventory = await inventory_crew.run()
                if travel_inventory and not isinstance(travel_inventory, str):
                    travel_inventory = str(travel_inventory)
            except Exception:
                # Keep plan-trip resilient even when remote MCP integration is unavailable.
                travel_inventory = None

        if travel_inventory:
            itinerary = (
                f"{itinerary}\n\n"
                "## Flights and Hotels\n"
                f"{travel_inventory}"
            )

        # Save to MongoDB
        now = datetime.now().isoformat()
        trip_doc = {
            "origin": trip_request.origin,
            "destination": trip_request.destination,
            "start_date": str(trip_request.start_date),
            "end_date": str(trip_request.end_date),
            "interests": trip_request.interests,
            "itinerary": itinerary,
            "travel_inventory": travel_inventory,
            "travel_inventory_source": "jinko" if travel_inventory else None,
            "refinements": [],
            "created_at": now,
            "updated_at": now,
        }
        result = await get_trips_collection().insert_one(trip_doc)
        trip_id = str(result.inserted_id)

        if clarification:
            return TripResponse(
                status="needs_clarification",
                message="Trip plan generated, but flight search needs more specific route details.",
                trip_id=trip_id,
                itinerary=itinerary,
                clarification_field=clarification["field"],
                clarification_message=clarification["message"],
                clarification_options=clarification["options"],
            )

        return TripResponse(
            status="success",
            message="Trip plan generated successfully",
            trip_id=trip_id,
            itinerary=itinerary
        )
    
    except Exception as e:
        return TripResponse(
            status="error",
            message="Failed to generate trip plan",
            error=str(e)
        )

@app.post("/api/v1/refine-trip", response_model=TripResponse)
async def refine_trip(
    refine_request: RefineRequest,
    settings: Settings = Depends(validate_api_keys),
):
    if refine_request.end_date <= refine_request.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date",
        )

    date_range = f"{refine_request.start_date} to {refine_request.end_date}"

    try:
        refine_crew = RefineCrew(
            refine_request.origin,
            refine_request.destination,
            date_range,
            refine_request.interests,
            refine_request.previous_itinerary,
            refine_request.refinement_request,
            f"openai/{settings.OPENAI_MODEL}",
        )

        itinerary = await refine_crew.run()

        if not isinstance(itinerary, str):
            itinerary = str(itinerary)

        # Update trip in MongoDB if trip_id provided
        trip_id = getattr(refine_request, "trip_id", None)
        if trip_id:
            now = datetime.now().isoformat()
            await get_trips_collection().update_one(
                {"_id": ObjectId(trip_id)},
                {
                    "$set": {"itinerary": itinerary, "updated_at": now},
                    "$push": {
                        "refinements": {
                            "$each": [
                                {"role": "user", "content": refine_request.refinement_request, "timestamp": now},
                                {"role": "assistant", "content": "Itinerary updated with your changes.", "timestamp": now},
                            ]
                        }
                    },
                },
            )

        return TripResponse(
            status="success",
            message="Trip plan refined successfully",
            trip_id=trip_id,
            itinerary=itinerary,
        )
    except Exception as e:
        return TripResponse(
            status="error",
            message="Failed to refine trip plan",
            error=str(e),
        )

@app.get("/api/v1/trips/{trip_id}", response_model=TripDetail)
async def get_trip(trip_id: str):
    try:
        doc = await get_trips_collection().find_one({"_id": ObjectId(trip_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid trip ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Trip not found")
    return TripDetail(
        trip_id=str(doc["_id"]),
        origin=doc["origin"],
        destination=doc["destination"],
        start_date=doc["start_date"],
        end_date=doc["end_date"],
        interests=doc.get("interests", ""),
        itinerary=doc["itinerary"],
        refinements=[ChatMessage(**r) for r in doc.get("refinements", [])],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )

@app.get("/api/v1/trips")
async def list_trips(limit: int = 10):
    cursor = get_trips_collection().find(
        {}, {"itinerary": 0}
    ).sort("created_at", -1).limit(min(limit, 50))
    trips = []
    async for doc in cursor:
        trips.append({
            "trip_id": str(doc["_id"]),
            "origin": doc["origin"],
            "destination": doc["destination"],
            "start_date": doc["start_date"],
            "end_date": doc["end_date"],
            "created_at": doc["created_at"],
        })
    return trips

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/search-travel-inventory", response_model=TravelInventoryResponse)
async def search_travel_inventory(
    request: TravelInventoryRequest,
    settings: Settings = Depends(get_settings),
):
    if request.end_date <= request.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing required API key: OPENAI_API_KEY")

    try:
        clarification = _clarification_response_for_flights(request.origin, request.destination)
        if clarification:
            return TravelInventoryResponse(
                status="needs_clarification",
                message="Travel inventory needs more specific route details.",
                trip_id=request.trip_id,
                clarification_field=clarification["field"],
                clarification_message=clarification["message"],
                clarification_options=clarification["options"],
            )

        crew = TravelInventoryCrew(
            request.origin,
            request.destination,
            str(request.start_date),
            str(request.end_date),
            request.travelers,
            request.notes,
            f"openai/{settings.OPENAI_MODEL}",
        )
        recommendation = await crew.run()
        recommendation = recommendation if isinstance(recommendation, str) else str(recommendation)
        disclaimer = "Recommendations include booking links for user handoff only. Autonomous booking is disabled."

        if request.trip_id:
            now = datetime.now().isoformat()
            await get_trips_collection().update_one(
                {"_id": ObjectId(request.trip_id)},
                {
                    "$set": {
                        "travel_inventory": recommendation,
                        "travel_inventory_source": "jinko",
                        "updated_at": now,
                    }
                },
            )
        
        return TravelInventoryResponse(
            status="success",
            message="Travel inventory generated successfully",
            trip_id=request.trip_id,
            recommendation=recommendation,
            disclaimer=disclaimer,
            source="jinko",
        )
    except Exception as e:
        return TravelInventoryResponse(
            status="error",
            message="Failed to generate travel inventory",
            trip_id=request.trip_id,
            error=str(e),
        )


@app.post("/api/v1/refine-travel-inventory", response_model=TravelInventoryResponse)
async def refine_travel_inventory(
    request: RefineTravelInventoryRequest,
    settings: Settings = Depends(get_settings),
):
    if request.end_date <= request.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing required API key: OPENAI_API_KEY")

    try:
        clarification = _clarification_response_for_flights(request.origin, request.destination)
        if clarification:
            return TravelInventoryResponse(
                status="needs_clarification",
                message="Travel inventory refinement needs more specific route details.",
                trip_id=request.trip_id,
                clarification_field=clarification["field"],
                clarification_message=clarification["message"],
                clarification_options=clarification["options"],
            )

        crew = RefineTravelInventoryCrew(
            request.origin,
            request.destination,
            str(request.start_date),
            str(request.end_date),
            request.travelers,
            request.previous_summary,
            request.refinement_request,
            f"openai/{settings.OPENAI_MODEL}",
        )
        recommendation = await crew.run()
        recommendation = recommendation if isinstance(recommendation, str) else str(recommendation)
        disclaimer = "Recommendations include booking links for user handoff only. Autonomous booking is disabled."

        if request.trip_id:
            now = datetime.now().isoformat()
            await get_trips_collection().update_one(
                {"_id": ObjectId(request.trip_id)},
                {
                    "$set": {
                        "travel_inventory": recommendation,
                        "travel_inventory_source": "jinko",
                        "updated_at": now,
                    },
                    "$push": {
                        "travel_inventory_refinements": {
                            "request": request.refinement_request,
                            "timestamp": now,
                        }
                    },
                },
            )

        return TravelInventoryResponse(
            status="success",
            message="Travel inventory refined successfully",
            trip_id=request.trip_id,
            recommendation=recommendation,
            disclaimer=disclaimer,
            source="jinko",
        )
    except Exception as e:
        return TravelInventoryResponse(
            status="error",
            message="Failed to refine travel inventory",
            trip_id=request.trip_id,
            error=str(e),
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
