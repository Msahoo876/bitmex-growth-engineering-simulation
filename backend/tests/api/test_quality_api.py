"""API tests for Phase 5 data quality endpoints."""

def _track(client, user_id: str, event: str, msg: str, properties: dict | None = None) -> None:
    payload = {
        "userId": user_id,
        "event": event,
        "messageId": msg,
    }
    if properties is not None:
        payload["properties"] = properties
    client.post("/api/v1/track", json=payload)


def _seed_quality_data(client) -> None:
    _track(client, "dq_user_a", "landing_page_viewed", "dq-a-landing", {"source": "google"})
    _track(client, "dq_user_a", "user_signed_up", "dq-a-signup")
    _track(client, "dq_user_a", "kyc_completed", "dq-a-kyc")
    _track(client, "dq_user_b", "landing_page_viewed", "dq-b-landing", {"source": "twitter"})
    _track(
        client,
        "dq_user_c",
        "trade_opened",
        "dq-c-trade-missing-symbol",
        {},
    )


class TestQualityAPI:
    def test_health_endpoint(self, client) -> None:
        _seed_quality_data(client)
        response = client.get("/api/v1/quality/health")
        assert response.status_code == 200
        body = response.json()
        assert 0 <= body["health_score"] <= 100
        assert body["snapshot_id"] is not None
        assert "summary" in body

    def test_duplicates_endpoint(self, client) -> None:
        payload = {
            "userId": "dup_user",
            "event": "user_signed_up",
            "messageId": "dup-message-shared",
        }
        client.post("/api/v1/track", json=payload)
        client.post("/api/v1/track", json=payload)
        response = client.get("/api/v1/quality/duplicates")
        assert response.status_code == 200
        body = response.json()
        assert body["total_duplicate_groups"] >= 1

    def test_schema_errors_endpoint(self, client) -> None:
        client.post(
            "/api/v1/track",
            json={
                "userId": "schema_user",
                "event": "not_a_real_event",
                "messageId": "dq-schema-invalid",
            },
        )
        response = client.get("/api/v1/quality/schema-errors")
        assert response.status_code == 200
        assert "errors" in response.json()

    def test_funnel_integrity_endpoint(self, client) -> None:
        _track(client, "dq_skip", "landing_page_viewed", "dq-skip-landing")
        _track(client, "dq_skip", "deposit_completed", "dq-skip-deposit")
        response = client.get("/api/v1/quality/funnel-integrity")
        assert response.status_code == 200
        body = response.json()
        assert body["total_broken_paths"] >= 1

    def test_anomalies_endpoint(self, client) -> None:
        _seed_quality_data(client)
        response = client.get("/api/v1/quality/anomalies")
        assert response.status_code == 200
        body = response.json()
        assert "daily_volume" in body
        assert "anomalies" in body
