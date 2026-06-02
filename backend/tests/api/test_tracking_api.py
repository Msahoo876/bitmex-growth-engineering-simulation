"""API integration tests for event tracking (SQLite in-memory)."""

from datetime import UTC, datetime


class TestTrackingAPI:
    def test_track_valid_event(self, client) -> None:
        response = client.post(
            "/api/v1/track",
            json={
                "userId": "user_123",
                "event": "trade_opened",
                "properties": {"symbol": "BTCUSDT", "amount": 500},
                "messageId": "msg-track-001",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )
        assert response.status_code == 202
        body = response.json()
        assert body["success"] is True
        assert body["eventId"] is not None
        assert body["messageId"] == "msg-track-001"

    def test_track_unknown_event_rejected(self, client) -> None:
        response = client.post(
            "/api/v1/track",
            json={
                "userId": "user_123",
                "event": "not_in_taxonomy",
                "messageId": "msg-track-002",
            },
        )
        assert response.status_code == 202
        assert response.json()["success"] is False
        assert response.json()["validation"]

    def test_track_duplicate_message_id(self, client) -> None:
        payload = {
            "userId": "user_dup",
            "event": "user_signed_up",
            "messageId": "msg-dup-001",
        }
        first = client.post("/api/v1/track", json=payload)
        second = client.post("/api/v1/track", json=payload)
        assert first.json()["success"] is True
        assert second.json()["success"] is False

    def test_identify_user(self, client) -> None:
        response = client.post(
            "/api/v1/identify",
            json={
                "userId": "user_identify_1",
                "traits": {"email": "trader@bitmex.test", "plan": "pro"},
                "messageId": "msg-identify-001",
            },
        )
        assert response.status_code == 202
        assert response.json()["success"] is True

    def test_page_view(self, client) -> None:
        response = client.post(
            "/api/v1/page",
            json={
                "userId": "user_page_1",
                "name": "Markets",
                "url": "/markets",
                "messageId": "msg-page-001",
            },
        )
        assert response.status_code == 202
        assert response.json()["success"] is True

    def test_unified_events_endpoint_track(self, client) -> None:
        response = client.post(
            "/api/v1/events",
            json={
                "type": "track",
                "payload": {
                    "userId": "user_unified",
                    "event": "deposit_completed",
                    "messageId": "msg-unified-001",
                },
            },
        )
        assert response.status_code == 202
        assert response.json()["success"] is True


class TestEventExplorerAPI:
    def test_list_and_get_event(self, client) -> None:
        track = client.post(
            "/api/v1/track",
            json={
                "userId": "explorer_user",
                "event": "kyc_started",
                "messageId": "msg-explorer-001",
            },
        )
        event_id = track.json()["eventId"]

        listing = client.get("/api/v1/events", params={"event_name": "kyc_started"})
        assert listing.status_code == 200
        data = listing.json()
        assert data["total"] >= 1
        assert len(data["events"]) >= 1

        detail = client.get(f"/api/v1/events/{event_id}")
        assert detail.status_code == 200
        assert detail.json()["event_id"] == event_id or detail.json().get("eventId") == event_id

    def test_get_missing_event_returns_404(self, client) -> None:
        response = client.get("/api/v1/events/does-not-exist")
        assert response.status_code == 404


class TestEventHealthAPI:
    def test_event_health_metrics(self, client) -> None:
        client.post(
            "/api/v1/track",
            json={
                "userId": "health_user",
                "event": "user_logged_in",
                "messageId": "msg-health-001",
            },
        )
        response = client.get("/api/v1/events/health", params={"period_hours": 24})
        assert response.status_code == 200
        body = response.json()
        assert "health_score" in body
        assert "acceptance_rate" in body
        assert body["total_ingested"] >= 1
