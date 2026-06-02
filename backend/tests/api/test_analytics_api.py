"""API tests for Phase 3 analytics endpoints."""

from datetime import UTC, datetime, timedelta


def _track(client, user_id: str, event: str, msg_suffix: str) -> None:
    client.post(
        "/api/v1/track",
        json={
            "userId": user_id,
            "event": event,
            "messageId": f"msg-{user_id}-{event}-{msg_suffix}",
        },
    )


def _seed_funnel_data(client) -> None:
    """User A completes full funnel; User B stops at signup."""
    steps_a = [
        "landing_page_viewed",
        "user_signed_up",
        "kyc_completed",
        "deposit_completed",
        "trade_opened",
    ]
    for event in steps_a:
        _track(client, "funnel_user_a", event, "a")

    _track(client, "funnel_user_b", "landing_page_viewed", "b")
    _track(client, "funnel_user_b", "user_signed_up", "b")


def _seed_retention_data(client) -> None:
    _track(client, "ret_user_a", "user_signed_up", "signup-a")
    _track(client, "ret_user_a", "user_logged_in", "login-a")
    _track(client, "ret_user_b", "user_signed_up", "signup-b")


class TestAnalyticsAPI:
    def test_funnel_analytics(self, client) -> None:
        _seed_funnel_data(client)
        now = datetime.now(UTC)
        response = client.get(
            "/api/v1/analytics/funnel",
            params={
                "from": (now - timedelta(days=7)).isoformat(),
                "to": now.isoformat(),
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["funnel_name"] == "growth_default"
        assert body["total_entered"] == 2
        assert body["total_completed"] == 1
        assert body["completion_rate"] == 50.0
        assert body["snapshot_id"] is not None
        assert len(body["steps"]) == 5

    def test_conversion_analytics(self, client) -> None:
        _seed_funnel_data(client)
        response = client.get("/api/v1/analytics/conversion")
        assert response.status_code == 200
        body = response.json()
        assert len(body["conversions"]) == 4
        assert body["overall_conversion_rate"] == 50.0

    def test_dropoff_analytics(self, client) -> None:
        _seed_funnel_data(client)
        response = client.get("/api/v1/analytics/dropoff")
        assert response.status_code == 200
        body = response.json()
        assert len(body["steps"]) == 4
        assert body["largest_dropoff_step"] is not None

    def test_retention_analytics(self, client) -> None:
        _seed_retention_data(client)
        response = client.get("/api/v1/analytics/retention")
        assert response.status_code == 200
        body = response.json()
        assert body["cohort_size"] >= 2
        assert len(body["periods"]) == 3
        period_days = {p["day"] for p in body["periods"]}
        assert period_days == {1, 7, 30}

    def test_cohort_analytics(self, client) -> None:
        _seed_retention_data(client)
        response = client.get("/api/v1/analytics/cohorts")
        assert response.status_code == 200
        body = response.json()
        assert "cohorts" in body
        assert body["snapshot_id"] is not None

    def test_unknown_funnel_returns_404(self, client) -> None:
        response = client.get("/api/v1/analytics/funnel", params={"funnel": "nonexistent"})
        assert response.status_code == 404
