import json
import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl
from dotenv import load_dotenv

from utils.auth import create_auth0_verifier

MCP_SERVER_DIR = os.path.dirname(__file__)
MCP_ENV_PATH = os.getenv("MCP_ENV_FILE", os.path.join(MCP_SERVER_DIR, ".env"))

load_dotenv(MCP_ENV_PATH)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
BROWSERLESS_API_KEY = os.getenv("BROWSERLESS_API_KEY", "")

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
RESOURCE_SERVER_URL = os.getenv("RESOURCE_SERVER_URL")

SERVER_HOST = "0.0.0.0"
SERVER_PORT = int(os.getenv("PORT", 8000))

if AUTH0_DOMAIN and RESOURCE_SERVER_URL:
    mcp = FastMCP(
        "VacAIgent",
        json_response=True,
        host=SERVER_HOST,
        port=SERVER_PORT,
        token_verifier=create_auth0_verifier(),
        auth=AuthSettings(
            issuer_url=AnyHttpUrl(f"https://{AUTH0_DOMAIN}/"),
            resource_server_url=AnyHttpUrl(RESOURCE_SERVER_URL),
            required_scopes=["openid", "profile", "email"],
        ),
    )
else:
    mcp = FastMCP("VacAIgent", json_response=True, host=SERVER_HOST, port=SERVER_PORT)

# ──────────────────────────────────────────────
#  TOOLS
# ──────────────────────────────────────────────

@mcp.tool()
async def plan_trip(
    origin: str,
    destination: str,
    start_date: str,
    end_date: str,
    interests: str,
) -> dict:
    """Plan a complete trip using the AI travel crew.

    Runs the full CrewAI pipeline (city selection → local guide → itinerary)
    and returns a detailed travel plan.

    Args:
        origin: Your current city, e.g. "Bangalore, India"
        destination: Destination city and country, e.g. "Krabi, Thailand"
        start_date: Trip start date in YYYY-MM-DD format
        end_date: Trip end date in YYYY-MM-DD format
        interests: Description of travelers and their interests
    """
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            f"{BACKEND_URL}/api/v1/plan-trip",
            json={
                "origin": origin,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "interests": interests,
            },
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def refine_trip(
    origin: str,
    destination: str,
    start_date: str,
    end_date: str,
    interests: str,
    previous_itinerary: str,
    refinement_request: str,
    trip_id: str | None = None,
) -> dict:
    """Refine an existing trip itinerary based on traveler feedback.

    Sends the previous itinerary and the change request through the
    travel concierge agent to produce an updated plan.

    Args:
        origin: Departure city
        destination: Destination city and country
        start_date: Trip start date in YYYY-MM-DD format
        end_date: Trip end date in YYYY-MM-DD format
        interests: Description of travelers and their interests
        previous_itinerary: The full markdown of the previously generated itinerary
        refinement_request: What the traveler wants changed, e.g. "Make day 3 more adventurous"
        trip_id: Optional saved trip ID so the refinement is persisted
    """
    payload = {
        "origin": origin,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "interests": interests,
        "previous_itinerary": previous_itinerary,
        "refinement_request": refinement_request,
    }
    if trip_id:
        payload["trip_id"] = trip_id

    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            f"{BACKEND_URL}/api/v1/refine-trip",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def search_travel_inventory(
    origin: str,
    destination: str,
    start_date: str,
    end_date: str,
    travelers: int = 1,
    notes: str = "",
    trip_id: str | None = None,
) -> dict:
    """Find flight and hotel recommendations with booking links.

    Uses the backend travel inventory workflow. Results are recommendation-only:
    the traveler makes any final booking externally.

    Args:
        origin: Origin city or 3-letter airport code
        destination: Destination city or 3-letter airport code
        start_date: Trip start date in YYYY-MM-DD format
        end_date: Trip end date in YYYY-MM-DD format
        travelers: Total number of travelers
        notes: Budget, timing, hotel, or flight preferences
        trip_id: Optional saved trip ID so inventory can be attached to the trip
    """
    payload = {
        "origin": origin,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "travelers": travelers,
        "notes": notes,
    }
    if trip_id:
        payload["trip_id"] = trip_id

    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            f"{BACKEND_URL}/api/v1/search-travel-inventory",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def refine_travel_inventory(
    origin: str,
    destination: str,
    start_date: str,
    end_date: str,
    refinement_request: str,
    travelers: int = 1,
    previous_summary: str = "",
    trip_id: str | None = None,
) -> dict:
    """Refine flight and hotel recommendations based on traveler feedback.

    Use this after search_travel_inventory when the traveler wants cheaper,
    faster, more convenient, or otherwise adjusted booking options.

    Args:
        origin: Origin city or 3-letter airport code
        destination: Destination city or 3-letter airport code
        start_date: Trip start date in YYYY-MM-DD format
        end_date: Trip end date in YYYY-MM-DD format
        refinement_request: What should change in the flight/hotel options
        travelers: Total number of travelers
        previous_summary: Previous travel inventory recommendation text
        trip_id: Optional saved trip ID so the refinement can be attached
    """
    payload = {
        "origin": origin,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "travelers": travelers,
        "previous_summary": previous_summary,
        "refinement_request": refinement_request,
    }
    if trip_id:
        payload["trip_id"] = trip_id

    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            f"{BACKEND_URL}/api/v1/refine-travel-inventory",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def search_web(query: str) -> Any:
    """Search the internet for travel-related information using Serper API.

    Args:
        query: The search query, e.g. "best restaurants in Kyoto"
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": SERPER_API_KEY,
                "Content-Type": "application/json",
            },
            json={"q": query},
        )
        if resp.status_code != 200:
            return f"Search API error: {resp.status_code}"

        data = resp.json()
        results = data.get("organic", [])[:5]
        lines = []
        for r in results:
            lines.append(
                f"Title: {r.get('title', '')}\n"
                f"Link: {r.get('link', '')}\n"
                f"Snippet: {r.get('snippet', '')}\n"
                f"-----------------"
            )
        return "\n".join(lines) if lines else "No results found."


@mcp.tool()
async def scrape_website(url: str) -> Any:
    """Scrape and return the text content of a webpage.

    Args:
        url: The full URL to scrape, e.g. "https://example.com/guide"
    """
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"https://chrome.browserless.io/content?token={BROWSERLESS_API_KEY}",
            headers={
                "Cache-Control": "no-cache",
                "Content-Type": "application/json",
            },
            json={"url": url},
        )
        if resp.status_code != 200:
            return f"Scrape error: {resp.status_code}"

        from unstructured.partition.html import partition_html

        elements = partition_html(text=resp.text)
        content = "\n\n".join(str(el) for el in elements)
        # Truncate to ~8000 chars to keep context manageable
        return content[:8000]


@mcp.tool()
def calculate(expression: str) -> Any:
    """Evaluate a mathematical expression for budget calculations, currency conversions, etc.

    Only supports basic arithmetic: +, -, *, /, (), **.

    Args:
        expression: A math expression, e.g. "1200 * 0.85 + 350"
    """
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return "Error: only basic arithmetic operators are allowed."
    try:
        result = eval(expression)  # safe: input is restricted to digits + operators
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"


@mcp.tool()
async def health_check() -> dict:
    """Check whether the VacAIgent backend is running and healthy."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{BACKEND_URL}/api/v1/health")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@mcp.tool()
async def get_trip(trip_id: str) -> dict:
    """Retrieve a previously generated trip by its ID.

    Use this to load a saved trip including its itinerary and refinement history.

    Args:
        trip_id: The 24-character hex trip ID
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BACKEND_URL}/api/v1/trips/{trip_id}")
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def list_trips(limit: int = 10) -> list:
    """List recently generated trips (without full itinerary text).

    Args:
        limit: Maximum number of trips to return (default 10, max 50)
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{BACKEND_URL}/api/v1/trips", params={"limit": limit}
        )
        resp.raise_for_status()
        return resp.json()


# ──────────────────────────────────────────────
#  RESOURCES
# ──────────────────────────────────────────────

SAMPLE_TRIPS = [
    {
        "id": "amalfi",
        "title": "Amalfi Coast",
        "region": "Italy",
        "nights": "7 nights",
        "tagline": "Lemon groves, lazy lunches, cliffside sunsets.",
        "prefill": {
            "origin": "London, United Kingdom",
            "destination": "Amalfi Coast, Italy",
            "interests": "2 adults who love coastal walks, slow food, boat days, espresso bars and lingering sunsets",
            "duration": 7,
        },
    },
    {
        "id": "kyoto",
        "title": "Kyoto in Autumn",
        "region": "Japan",
        "nights": "8 nights",
        "tagline": "Maple light, tea ceremonies, quiet temples.",
        "prefill": {
            "origin": "San Francisco, USA",
            "destination": "Kyoto, Japan",
            "interests": "Couple seeking traditional tea ceremonies, autumn foliage walks, kaiseki dinners, indie galleries and craft markets",
            "duration": 8,
        },
    },
    {
        "id": "sahara",
        "title": "Sahara & Marrakech",
        "region": "Morocco",
        "nights": "9 nights",
        "tagline": "Riads, dune camps, mint tea under stars.",
        "prefill": {
            "origin": "Berlin, Germany",
            "destination": "Marrakech & Merzouga, Morocco",
            "interests": "Two travelers who love souks, riad design, desert camping, hiking the Atlas Mountains and sunrise photography",
            "duration": 9,
        },
    },
]


@mcp.resource("vacaigent://sample-trips")
def get_sample_trips() -> Any:
    """Curated sample trips with pre-filled parameters for inspiration."""
    return json.dumps(SAMPLE_TRIPS, indent=2)


@mcp.resource("vacaigent://config")
def get_config() -> Any:
    """Current server configuration and API key availability (keys are not exposed)."""
    return json.dumps(
        {
            "backend_url": BACKEND_URL,
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "keys_configured": {
                "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
                "SERPER_API_KEY": bool(SERPER_API_KEY),
                "BROWSERLESS_API_KEY": bool(BROWSERLESS_API_KEY),
            },
        },
        indent=2,
    )


# ──────────────────────────────────────────────
#  PROMPTS
# ──────────────────────────────────────────────

@mcp.prompt()
def plan_trip_prompt(
    origin: str,
    destination: str,
    start_date: str,
    end_date: str,
    interests: str,
) -> Any:
    """Generate a prompt to plan a full trip itinerary.

    Args:
        origin: Departure city
        destination: Destination city
        start_date: YYYY-MM-DD
        end_date: YYYY-MM-DD
        interests: Traveler interests
    """
    return (
        f"Plan a detailed trip for me.\n\n"
        f"- Traveling from: {origin}\n"
        f"- Destination: {destination}\n"
        f"- Dates: {start_date} to {end_date}\n"
        f"- Interests: {interests}\n\n"
        f"Use the plan_trip tool to generate the full itinerary, then present "
        f"it in a clear, day-by-day format with budget and packing suggestions."
    )


@mcp.prompt()
def city_comparison(origin: str, cities: str, travel_dates: str) -> Any:
    """Compare multiple destination cities on weather, cost, and events.

    Args:
        origin: Departure city
        cities: Comma-separated list of cities to compare
        travel_dates: Intended travel dates
    """
    return (
        f"I'm traveling from {origin} during {travel_dates}. "
        f"Compare these destination cities: {cities}.\n\n"
        f"For each city provide:\n"
        f"1. Expected weather during my dates\n"
        f"2. Approximate flight cost from {origin}\n"
        f"3. Notable events or festivals happening then\n"
        f"4. Pros and cons for each\n\n"
        f"Use the search_web tool to find current information, "
        f"then recommend the best option with reasoning."
    )


@mcp.prompt()
def local_guide(city: str, interests: str, travel_dates: str) -> Any:
    """Generate an in-depth local guide for a specific city.

    Args:
        city: The city to create a guide for
        interests: Traveler interests and preferences
        travel_dates: When the traveler will visit
    """
    return (
        f"Create a comprehensive local guide for {city} during {travel_dates}.\n\n"
        f"Traveler interests: {interests}\n\n"
        f"Cover:\n"
        f"- Must-visit attractions and hidden gems\n"
        f"- Local customs and cultural tips\n"
        f"- Best neighborhoods and areas to explore\n"
        f"- Food and restaurant recommendations\n"
        f"- Safety tips and local etiquette\n\n"
        f"Use the search_web tool to find up-to-date local information."
    )


@mcp.prompt()
def budget_breakdown(
    destination: str, duration_days: int, travel_style: str = "moderate"
) -> Any:
    """Estimate and break down the trip budget.

    Args:
        destination: Trip destination
        duration_days: Number of days
        travel_style: Budget level — budget, moderate, or luxury
    """
    return (
        f"Create a detailed budget breakdown for a {duration_days}-day trip to "
        f"{destination} with a {travel_style} travel style.\n\n"
        f"Include:\n"
        f"- Accommodation (per night and total)\n"
        f"- Food and dining\n"
        f"- Transportation (flights, local transit)\n"
        f"- Activities and excursions\n"
        f"- Miscellaneous and emergency fund\n\n"
        f"Use the search_web tool for current prices and the calculate tool "
        f"for totals. Present a clear summary table."
    )


@mcp.prompt()
def refine_trip_prompt(
    refinement_request: str,
    destination: str = "",
) -> Any:
    """Generate a prompt to refine an existing trip itinerary.

    Args:
        refinement_request: What the traveler wants changed
        destination: The destination (optional, for context)
    """
    dest_ctx = f" for {destination}" if destination else ""
    return (
        f"I have an existing trip plan{dest_ctx} and I'd like some changes:\n\n"
        f"{refinement_request}\n\n"
        f"Use the refine_trip tool with the current itinerary and this change "
        f"request. Return the full updated itinerary."
    )


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
