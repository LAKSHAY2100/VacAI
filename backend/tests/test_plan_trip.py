"""Backend tests for VacAIgent /api/v1/plan-trip endpoint."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://voyage-design-9.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# -- Health check --
class TestHealth:
    def test_root(self, client):
        r = client.get(f"{API}/")
        assert r.status_code == 200
        data = r.json()
        assert "message" in data
        assert isinstance(data["message"], str) and len(data["message"]) > 0


# -- /v1/plan-trip happy path & validation --
class TestPlanTrip:
    SPEC_PAYLOAD = {
        "origin": "Bangalore, India",
        "destination": "Krabi, Thailand",
        "start_date": "2025-06-01",
        "end_date": "2025-06-10",
        "interests": "2 adults who love swimming, dancing, hiking, shopping, local food, water sports adventures and rock climbing",
    }

    def test_plan_trip_success_spec(self, client):
        r = client.post(f"{API}/v1/plan-trip", json=self.SPEC_PAYLOAD, timeout=30)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["status"] == "success"
        assert data["error"] is None
        assert isinstance(data["message"], str) and len(data["message"]) > 0
        itin = data["itinerary"]
        assert isinstance(itin, str) and len(itin) > 500

        # Markdown headings present
        assert "# " in itin
        assert "## " in itin
        assert "### " in itin

        # References destination & origin
        assert "Krabi, Thailand" in itin
        assert "Bangalore, India" in itin

        # 10 days expected (Jun 01 -> Jun 10 inclusive = 10)
        assert "10-Day Journey" in itin
        # Verify Day 10 section exists
        assert "Day 10" in itin

    def test_plan_trip_end_before_start_returns_400(self, client):
        payload = dict(self.SPEC_PAYLOAD)
        payload["start_date"] = "2025-06-10"
        payload["end_date"] = "2025-06-01"
        r = client.post(f"{API}/v1/plan-trip", json=payload, timeout=15)
        assert r.status_code == 400
        body = r.json()
        assert "detail" in body
        assert "end_date" in body["detail"].lower() or "earlier" in body["detail"].lower()

    def test_plan_trip_invalid_date_format_returns_400(self, client):
        payload = dict(self.SPEC_PAYLOAD)
        payload["start_date"] = "06/01/2025"
        r = client.post(f"{API}/v1/plan-trip", json=payload, timeout=15)
        # Pydantic v2 may reject earlier; FastAPI will surface either 400 or 422
        assert r.status_code in (400, 422), r.text

    def test_plan_trip_missing_fields_returns_422(self, client):
        # missing destination, interests
        r = client.post(f"{API}/v1/plan-trip", json={"origin": "X", "start_date": "2025-06-01", "end_date": "2025-06-02"}, timeout=15)
        assert r.status_code == 422

    def test_plan_trip_single_day_trip(self, client):
        payload = dict(self.SPEC_PAYLOAD)
        payload["start_date"] = "2025-07-01"
        payload["end_date"] = "2025-07-01"
        r = client.post(f"{API}/v1/plan-trip", json=payload, timeout=20)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "1-Day Journey" in data["itinerary"]
        assert "Day 1" in data["itinerary"]
