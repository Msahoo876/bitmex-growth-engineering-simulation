"""Unit tests for attribution repository helpers."""

from app.repositories.attribution_repository import AttributionRepository


def test_pick_source_prefers_properties() -> None:
    source = AttributionRepository._pick_source(
        event_name="landing_page_viewed",
        properties={"source": "Google"},
    )
    assert source == "google"


def test_pick_source_referral_default() -> None:
    source = AttributionRepository._pick_source(
        event_name="referral_clicked",
        properties={},
    )
    assert source == "referral"


def test_pick_referral_and_deep_link() -> None:
    referral = AttributionRepository._pick_referral({"referral_code": "ABC123"})
    deep_link = AttributionRepository._pick_deep_link({"deep_link": "app://markets"})
    assert referral == "ABC123"
    assert deep_link == "app://markets"
