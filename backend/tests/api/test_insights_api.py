"""API tests for Phase 6 AI insights endpoints."""


class TestInsightsAPI:
    def test_generate_and_list_insights_without_gemini_key(self, client) -> None:
        response = client.post(
            "/api/v1/insights/generate",
            json={"insight_types": ["executive", "quality"]},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["generated_count"] == 2
        assert {item["insight_type"] for item in body["insights"]} == {"executive", "quality"}
        assert all(item["model_name"] == "local-rules" for item in body["insights"])
        assert all(item["recommendations"] for item in body["insights"])

        list_response = client.get("/api/v1/insights")
        assert list_response.status_code == 200
        assert len(list_response.json()["insights"]) == 2

    def test_get_insight_by_id(self, client) -> None:
        generated = client.post(
            "/api/v1/insights/generate",
            json={"insight_types": ["funnel"]},
        ).json()
        insight_id = generated["insights"][0]["id"]

        response = client.get(f"/api/v1/insights/{insight_id}")

        assert response.status_code == 200
        assert response.json()["insight_type"] == "funnel"

    def test_executive_summary_generates_when_missing(self, client) -> None:
        response = client.get("/api/v1/insights/executive-summary")

        assert response.status_code == 200
        body = response.json()
        assert body["title"] == "Executive growth summary"
        assert body["recommendations"]
