import json
import os
import uuid
from typing import Any, Optional

import requests
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class JinkoTravelSearchInput(BaseModel):
    origin: str = Field(..., description="Origin location or IATA code")
    destination: str = Field(..., description="Destination location or IATA code")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD")
    end_date: str = Field(..., description="End date in YYYY-MM-DD")
    travelers: int = Field(1, description="Total travelers")
    budget_notes: str = Field("", description="Budget notes and preference hints")


class JinkoTravelRefineInput(BaseModel):
    origin: str = Field(..., description="Origin location or IATA code")
    destination: str = Field(..., description="Destination location or IATA code")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD")
    end_date: str = Field(..., description="End date in YYYY-MM-DD")
    travelers: int = Field(1, description="Total travelers")
    refinement_request: str = Field(..., description="Requested changes to flights/hotels")
    previous_summary: str = Field("", description="Previous recommendation summary")


def _extract_iata_code(value: str) -> Optional[str]:
    if not value:
        return None

    cleaned = value.strip().upper()
    if len(cleaned) == 3 and cleaned.isalpha():
        return cleaned

    for token in cleaned.replace("(", " ").replace(")", " ").replace(",", " ").split():
        if len(token) == 3 and token.isalpha():
            return token

    return None


def _llm_model_name() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"


def _resolve_airport_code_with_llm(value: str, field_name: str) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or not value.strip():
        return {}

    prompt = (
        "Convert a travel place into the best 3-letter IATA airport code for flight search.\n"
        "Return JSON only with keys: airport_code, normalized_place, is_airport_exact, is_broad_region, confidence, rationale.\n"
        "Rules:\n"
        "- airport_code must be a 3-letter uppercase IATA code or null.\n"
        "- If the input is a non-airport destination, choose the nearest practical commercial airport.\n"
        "- If the input is too broad, like a country or large region, set airport_code to null and is_broad_region to true.\n"
        "- confidence must be a number between 0 and 1.\n"
        "- Do not include markdown.\n\n"
        f"Field: {field_name}\n"
        f"Input: {value}"
    )

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": _llm_model_name(),
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a travel normalization assistant that returns strict JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        message = payload["choices"][0]["message"]["content"]
        parsed = json.loads(message) if isinstance(message, str) else {}
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def resolve_flight_endpoint_details(value: str, field_name: str) -> dict[str, Any]:
    code = _extract_iata_code(value)
    if code:
        return {
            "airport_code": code,
            "normalized_place": value,
            "needs_clarification": False,
            "is_broad_region": False,
            "confidence": 1.0,
            "field": field_name,
        }

    llm_resolution = _resolve_airport_code_with_llm(value, field_name)
    llm_code = str(llm_resolution.get("airport_code", "")).strip().upper()
    llm_confidence = llm_resolution.get("confidence", 0)
    is_broad_region = bool(llm_resolution.get("is_broad_region"))

    if len(llm_code) == 3 and llm_code.isalpha() and not is_broad_region and llm_confidence >= 0.6:
        return {
            "airport_code": llm_code,
            "normalized_place": llm_resolution.get("normalized_place") or value,
            "needs_clarification": False,
            "is_broad_region": False,
            "confidence": llm_confidence,
            "field": field_name,
            "rationale": llm_resolution.get("rationale", ""),
        }

    return {
        "airport_code": None,
        "normalized_place": llm_resolution.get("normalized_place") or value,
        "needs_clarification": is_broad_region,
        "is_broad_region": is_broad_region,
        "confidence": llm_confidence if isinstance(llm_confidence, (int, float)) else 0,
        "field": field_name,
        "rationale": llm_resolution.get("rationale", ""),
    }


def _normalize_flight_endpoint(value: str, field_name: str) -> tuple[Optional[str], Optional[str]]:
    resolution = resolve_flight_endpoint_details(value, field_name)
    code = resolution.get("airport_code")
    if isinstance(code, str) and len(code) == 3 and code.isalpha():
        return code, None

    if resolution.get("needs_clarification"):
        return None, (
            f"Flight search needs a city or 3-letter airport code for {field_name}, not a broad region like '{value}'."
        )

    return None, (
        f"Flight search requires a 3-letter IATA airport code for {field_name}. "
        f"Received '{value}'. Use values like 'IXC', 'JFK', or 'DED'."
    )


class _JinkoMCPClient:
    """MCP client for Jinko's Streamable HTTP transport.

    Jinko uses the MCP Streamable HTTP spec which requires:
    - Accept: application/json, text/event-stream  on every POST
    - Session established via initialize; Mcp-Session-Id header on subsequent calls
    - Responses may be plain JSON or SSE (data: <json> lines)
    """

    def __init__(self):
        self.server_url = os.getenv("JINKO_MCP_SERVER_URL", "https://mcp.builders.gojinko.com/mcp")
        self.timeout_sec = int(os.getenv("JINKO_MCP_TIMEOUT_SEC", "60"))
        self.oauth_bearer_token = os.getenv("JINKO_MCP_OAUTH_BEARER_TOKEN", "")
        self._session_id: Optional[str] = None

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.oauth_bearer_token:
            headers["Authorization"] = f"Bearer {self.oauth_bearer_token}"
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        return headers

    def _parse_response(self, resp: requests.Response) -> dict[str, Any]:
        """Parse either a plain JSON or SSE response body into a JSON-RPC result."""
        ct = resp.headers.get("Content-Type", "")
        text = resp.text.strip()

        if "text/event-stream" in ct or text.startswith("data:"):
            # SSE: collect all data: lines and take the last valid JSON-RPC message
            last: dict[str, Any] = {}
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("data:"):
                    payload_str = line[5:].strip()
                    if payload_str:
                        try:
                            last = json.loads(payload_str)
                        except Exception:
                            pass
            data = last
        else:
            data = json.loads(text) if text else {}

        if "error" in data and data["error"] is not None:
            raise RuntimeError(str(data["error"]))
        return data.get("result", {})

    def _rpc(self, method: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params or {},
        }
        resp = requests.post(
            self.server_url,
            headers=self._headers(),
            data=json.dumps(payload),
            timeout=self.timeout_sec,
        )
        resp.raise_for_status()
        # Capture session id if server returns one
        session_id = resp.headers.get("Mcp-Session-Id")
        if session_id:
            self._session_id = session_id
        return self._parse_response(resp)

    def initialize(self) -> None:
        try:
            self._rpc(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "vacaigent-backend", "version": "1.0.0"},
                },
            )
            # Send initialized notification (fire-and-forget, ignore errors)
            try:
                notif = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
                requests.post(
                    self.server_url,
                    headers=self._headers(),
                    data=json.dumps(notif),
                    timeout=10,
                )
            except Exception:
                pass
        except Exception:
            pass

    def list_tools(self) -> list[dict[str, Any]]:
        result = self._rpc("tools/list", {})
        tools = result.get("tools", [])
        return tools if isinstance(tools, list) else []

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return self._rpc("tools/call", {"name": name, "arguments": arguments})


def _extract_result_payload(result: dict[str, Any]) -> dict[str, Any]:
    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        return structured

    content = result.get("content", [])
    if isinstance(content, list):
        text_items = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                text_items.append(item["text"])
        if text_items:
            text = "\n".join(text_items).strip()
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                return {"text": text}

    return {"raw": result}


def _compact_hotel_result(result: dict[str, Any], limit: int = 5) -> dict[str, Any]:
    hotels = result.get("hotels")
    if not isinstance(hotels, list):
        return result

    compact_hotels = []
    for hotel in hotels[:limit]:
        if not isinstance(hotel, dict):
            continue

        rates = []
        for room in hotel.get("rooms", []) or []:
            if not isinstance(room, dict):
                continue
            for rate in room.get("rates", []) or []:
                if not isinstance(rate, dict):
                    continue
                rates.append({
                    "offer_id": rate.get("offer_id"),
                    "room_name": room.get("room_name") or None,
                    "board_name": rate.get("board_name"),
                    "total_amount": rate.get("total_amount"),
                    "currency": rate.get("currency"),
                    "is_refundable": rate.get("is_refundable"),
                })

        rates = sorted(
            rates,
            key=lambda r: (
                r.get("total_amount") is None,
                r.get("total_amount") if r.get("total_amount") is not None else 0,
            ),
        )

        compact_hotels.append({
            "hotel_id": hotel.get("hotel_id"),
            "name": hotel.get("name"),
            "address": hotel.get("address"),
            "city": hotel.get("city"),
            "country": hotel.get("country"),
            "star_rating": hotel.get("star_rating"),
            "rating": hotel.get("rating"),
            "review_count": hotel.get("review_count"),
            "thumbnail": hotel.get("thumbnail"),
            "best_rates": rates[:2],
        })

    return {
        "hotels": compact_hotels,
        "total_hotels_returned": len(hotels),
        "note": "Hotel result compacted for recommendation. Full booking details should be fetched or checked before final booking.",
    }


def _compact_flight_result(result: dict[str, Any], limit: int = 5) -> dict[str, Any]:
    if result.get("status") == "empty":
        return result

    for key in ("flights", "results", "itineraries", "offers"):
        items = result.get(key)
        if isinstance(items, list):
            return {
                **{k: v for k, v in result.items() if k != key},
                key: items[:limit],
                f"total_{key}_returned": len(items),
                "note": "Flight result compacted for recommendation.",
            }

    return result


def _pick_tool_name(tools: list[dict[str, Any]], preferred_env: str, keywords: list[str]) -> Optional[str]:
    forced = os.getenv(preferred_env, "").strip()
    if forced:
        return forced

    available = {str(t.get("name", "")) for t in tools}

    # Prefer exact known Jinko names first
    for candidate in keywords:
        if candidate in available:
            return candidate

    # Fallback: keyword substring match
    for tool in tools:
        name = str(tool.get("name", ""))
        lowered = name.lower()
        if all(k.lower() in lowered for k in keywords):
            return name

    return None


def _policy_disclaimer() -> str:
    return "Recommendations may include booking links for user handoff. Autonomous booking is disabled."


class JinkoTravelSearchTool(BaseTool):
    name: str = "Search flights and hotels with Jinko MCP"
    description: str = "Find flight and hotel recommendations plus booking links using Jinko remote MCP"
    args_schema: type[BaseModel] = JinkoTravelSearchInput

    def _run(
        self,
        origin: str,
        destination: str,
        start_date: str,
        end_date: str,
        travelers: int = 1,
        budget_notes: str = "",
    ) -> str:
        try:
            client = _JinkoMCPClient()
            client.initialize()
            tools = client.list_tools()

            # Use known Jinko tool names; env overrides allow pinning
            flight_tool = _pick_tool_name(
                tools, "JINKO_FLIGHT_SEARCH_TOOL",
                ["flight_calendar"]
            )
            hotel_tool = _pick_tool_name(
                tools, "JINKO_HOTEL_SEARCH_TOOL",
                ["hotel_search"]
            )

            payload: dict[str, Any] = {
                "source": "jinko",
                "disclaimer": _policy_disclaimer(),
                "flight_result": None,
                "hotel_result": None,
            }

            if not flight_tool and not hotel_tool:
                payload["error"] = "No flight or hotel tools found on Jinko MCP."
                payload["available_tools"] = [t.get("name") for t in tools]
                return json.dumps(payload)

            # Flight search — flight_calendar uses cached pricing, ideal for recommendations
            if flight_tool:
                try:
                    flight_origin, origin_error = _normalize_flight_endpoint(origin, "origin")
                    flight_destination, destination_error = _normalize_flight_endpoint(destination, "destination")
                    if origin_error or destination_error:
                        errors = [msg for msg in [origin_error, destination_error] if msg]
                        payload["flight_result"] = {
                            "error": " ".join(errors),
                            "input_requirements": (
                                "Provide airport codes for flights. For non-airport destinations, "
                                "use the nearest airport for flights and keep the original city for hotels."
                            ),
                        }
                        return json.dumps(payload)

                    flight_args: dict[str, Any] = {
                        "origin": flight_origin,
                        "destination": flight_destination,
                        "adults": travelers,
                        "trip_type": "roundtrip",
                        "month": start_date[:7],  # YYYY-MM
                    }
                    flight_call = client.call_tool(flight_tool, flight_args)
                    payload["flight_result"] = _compact_flight_result(_extract_result_payload(flight_call))
                except Exception as fe:
                    payload["flight_result"] = {"error": str(fe)}

            # Hotel search — hotel_search returns live rates with offer_ids
            if hotel_tool:
                try:
                    hotel_args: dict[str, Any] = {
                        "destination": {"query": destination},
                        "checkin": start_date,
                        "checkout": end_date,
                        "adults": travelers,
                    }
                    hotel_call = client.call_tool(hotel_tool, hotel_args)
                    payload["hotel_result"] = _compact_hotel_result(_extract_result_payload(hotel_call))
                except Exception as he:
                    payload["hotel_result"] = {"error": str(he)}

            return json.dumps(payload)
        except Exception as e:
            return json.dumps({"error": str(e), "source": "jinko", "disclaimer": _policy_disclaimer()})

    async def _arun(self, **kwargs):
        raise NotImplementedError("Async not implemented")


class JinkoTravelRefineTool(BaseTool):
    name: str = "Refine flights and hotels with Jinko MCP"
    description: str = "Refine prior flight/hotel recommendations based on traveler changes"
    args_schema: type[BaseModel] = JinkoTravelRefineInput

    def _run(
        self,
        origin: str,
        destination: str,
        start_date: str,
        end_date: str,
        travelers: int = 1,
        refinement_request: str = "",
        previous_summary: str = "",
    ) -> str:
        try:
            client = _JinkoMCPClient()
            client.initialize()
            tools = client.list_tools()

            # Refinement uses flight_search to re-price with updated dates
            refine_tool = _pick_tool_name(
                tools, "JINKO_TRAVEL_REFINE_TOOL",
                ["flight_search", "flight_calendar"]
            )

            if not refine_tool:
                return json.dumps({
                    "error": "No suitable Jinko refinement tool found.",
                    "source": "jinko",
                    "disclaimer": _policy_disclaimer(),
                    "available_tools": [t.get("name") for t in tools],
                })

            flight_origin, origin_error = _normalize_flight_endpoint(origin, "origin")
            flight_destination, destination_error = _normalize_flight_endpoint(destination, "destination")
            if origin_error or destination_error:
                return json.dumps({
                    "error": " ".join(msg for msg in [origin_error, destination_error] if msg),
                    "source": "jinko",
                    "disclaimer": _policy_disclaimer(),
                    "refinement_request": refinement_request,
                })

            args: dict[str, Any] = {
                "origin": flight_origin,
                "destination": flight_destination,
                "adults": travelers,
                "trip_type": "roundtrip",
                "action": "search",
            }
            if refine_tool == "flight_search":
                # Re-price with updated dates/parameters
                args["departure_date"] = start_date
                args["return_date"] = end_date
            else:
                # flight_calendar for month-based discovery
                args["month"] = start_date[:7]

            result = client.call_tool(refine_tool, args)
            payload = _extract_result_payload(result)
            payload["source"] = "jinko"
            payload["disclaimer"] = _policy_disclaimer()
            payload["refinement_request"] = refinement_request
            return json.dumps(payload)
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "source": "jinko",
                "disclaimer": _policy_disclaimer(),
                "refinement_request": refinement_request,
            })

    async def _arun(self, **kwargs):
        raise NotImplementedError("Async not implemented")
