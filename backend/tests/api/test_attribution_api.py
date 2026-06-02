"""API tests for Phase 4 attribution endpoints."""


def _track(client, user_id: str, event: str, msg: str, properties: dict) -> None:
    client.post(
        "/api/v1/track",
        json={
            "userId": user_id,
            "event": event,
            "messageId": msg,
            "properties": properties,
        },
    )


def _seed_attribution_data(client) -> None:
    _track(
        client,
        "attr_user_a",
        "landing_page_viewed",
        "msg-attr-a-landing",
        {
            "source": "google",
            "medium": "cpc",
            "campaign": "summer_push",
            "deep_link": "app://trade/BTCUSDT",
        },
    )
    _track(
        client,
        "attr_user_a",
        "campaign_clicked",
        "msg-attr-a-campaign",
        {
            "source": "twitter",
            "medium": "social",
            "campaign": "tweet_wave",
            "referral_code": "REF_A1",
        },
    )
    _track(
        client,
        "attr_user_b",
        "referral_clicked",
        "msg-attr-b-referral",
        {
            "referral_code": "REF_B1",
            "deep_link": "app://signup?ref=REF_B1",
        },
    )
    _track(
        client,
        "attr_user_b",
        "signup_from_campaign",
        "msg-attr-b-signup",
        {
            "source": "telegram",
            "campaign": "alpha_channel",
        },
    )


class TestAttributionAPI:
    def test_sources(self, client) -> None:
        _seed_attribution_data(client)
        response = client.get("/api/v1/attribution/sources")
        assert response.status_code == 200
        body = response.json()
        assert "metrics" in body
        assert body["top_source"] is not None
        assert any(item["touch_type"] == "first_touch" for item in body["metrics"])

    def test_campaigns(self, client) -> None:
        _seed_attribution_data(client)
        response = client.get("/api/v1/attribution/campaigns")
        assert response.status_code == 200
        body = response.json()
        assert len(body["metrics"]) >= 1
        assert "campaign_name" in body["metrics"][0]

    def test_top_source(self, client) -> None:
        _seed_attribution_data(client)
        response = client.get("/api/v1/attribution/top-source")
        assert response.status_code == 200
        body = response.json()
        assert "source" in body
        assert "users" in body

    def test_deep_links(self, client) -> None:
        _seed_attribution_data(client)
        response = client.get("/api/v1/attribution/deep-links")
        assert response.status_code == 200
        body = response.json()
        assert len(body["metrics"]) >= 1
        assert body["metrics"][0]["users"] >= 1

    def test_referrals(self, client) -> None:
        _seed_attribution_data(client)
        response = client.get("/api/v1/attribution/referrals")
        assert response.status_code == 200
        body = response.json()
        assert len(body["metrics"]) >= 1
        assert "referral_code" in body["metrics"][0]
