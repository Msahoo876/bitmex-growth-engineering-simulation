"""Seed a realistic BitMEX growth demo dataset into PostgreSQL.

Run from the backend directory:

    python seed_demo_data.py
"""

from __future__ import annotations

import random
import uuid
from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.analytics_snapshot import AnalyticsSnapshot
from app.models.attribution import Attribution
from app.models.campaign import Campaign
from app.models.event import Event
from app.models.health_score import HealthScore
from app.models.user import User

SEED = 42
TOTAL_USERS = 10_000
MIN_EVENTS = 50_000
SOURCE_COUNTS = {
    "Google": 3600,
    "Twitter": 1800,
    "Telegram": 1700,
    "Discord": 1200,
    "Referral": 800,
    "Direct": 900,
}
FUNNEL_TARGETS = {
    "landing_page_viewed": 10_000,
    "user_signed_up": 5_000,
    "kyc_started": 4_200,
    "kyc_completed": 3_100,
    "deposit_started": 2_400,
    "deposit_completed": 1_800,
    "trade_opened": 950,
}
SOURCE_STAGE_TARGETS = {
    "Google": {
        "user_signed_up": 1550,
        "kyc_started": 1260,
        "kyc_completed": 830,
        "deposit_started": 590,
        "deposit_completed": 405,
        "trade_opened": 180,
    },
    "Twitter": {
        "user_signed_up": 760,
        "kyc_started": 620,
        "kyc_completed": 430,
        "deposit_started": 300,
        "deposit_completed": 210,
        "trade_opened": 90,
    },
    "Telegram": {
        "user_signed_up": 1050,
        "kyc_started": 930,
        "kyc_completed": 780,
        "deposit_started": 670,
        "deposit_completed": 560,
        "trade_opened": 410,
    },
    "Discord": {
        "user_signed_up": 520,
        "kyc_started": 430,
        "kyc_completed": 280,
        "deposit_started": 200,
        "deposit_completed": 130,
        "trade_opened": 55,
    },
    "Referral": {
        "user_signed_up": 560,
        "kyc_started": 500,
        "kyc_completed": 445,
        "deposit_started": 370,
        "deposit_completed": 300,
        "trade_opened": 145,
    },
    "Direct": {
        "user_signed_up": 560,
        "kyc_started": 460,
        "kyc_completed": 335,
        "deposit_started": 270,
        "deposit_completed": 195,
        "trade_opened": 70,
    },
}
CAMPAIGNS = {
    "Google": ("demo_google_search_alpha", "paid_search"),
    "Twitter": ("demo_twitter_perps_push", "paid_social"),
    "Telegram": ("demo_telegram_trader_community", "community"),
    "Discord": ("demo_discord_market_makers", "community"),
    "Referral": ("demo_referral_vip_program", "referral"),
    "Direct": ("demo_direct_brand", "direct"),
}
COUNTRIES = ["IN", "SG", "HK", "AE", "GB", "DE", "BR", "TR", "VN", "US"]
DEVICES = ["desktop", "mobile", "tablet"]
SYMBOLS = ["XBTUSD", "ETHUSD", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BMEXUSDT"]
SOURCE_DEPOSIT_MULTIPLIER = {
    "Google": 1.0,
    "Twitter": 0.9,
    "Telegram": 1.35,
    "Discord": 1.1,
    "Referral": 2.25,
    "Direct": 1.15,
}


def main() -> None:
    random.seed(SEED)
    now = datetime.now(UTC)
    period_start = now - timedelta(days=90)

    with SessionLocal() as session:
        clear_existing_demo_data(session)
        campaign_ids = create_campaigns(session, period_start, now)
        users, source_users = create_users(period_start)
        session.bulk_save_objects(users)
        session.flush()

        stage_users = allocate_funnel_users(source_users)
        events = create_events(users, stage_users, period_start, now)
        attributions = create_attributions(users, stage_users, campaign_ids)
        snapshots = create_snapshots(events, stage_users, period_start, now)
        health_scores = create_health_scores(period_start, now)

        session.bulk_save_objects(events)
        session.bulk_save_objects(attributions)
        session.bulk_save_objects(snapshots)
        session.bulk_save_objects(health_scores)
        session.commit()

    event_counts = Counter(event.event_name for event in events)
    print("Demo dataset generated")
    print(f"Users: {len(users):,}")
    print(f"Events: {len(events):,}")
    print(f"Attributions: {len(attributions):,}")
    print(f"Analytics snapshots: {len(snapshots):,}")
    print(f"Health scores: {len(health_scores):,}")
    print("Funnel unique users:")
    for event_name in FUNNEL_TARGETS:
        print(f"  {event_name}: {len(stage_users[event_name]):,}")
    print("Event rows:")
    for event_name, count in sorted(event_counts.items()):
        print(f"  {event_name}: {count:,}")


def clear_existing_demo_data(session: Session) -> None:
    """Remove only prior demo-seed records so the script is repeatable."""
    session.execute(delete(Event).where(Event.event_id.like("demo_evt_%")))
    session.execute(delete(Attribution).where(Attribution.campaign_name.like("demo_%")))
    session.execute(delete(AnalyticsSnapshot).where(AnalyticsSnapshot.snapshot_type.like("demo_%")))
    session.execute(delete(HealthScore).where(HealthScore.check_type == "demo_data_quality"))
    session.execute(delete(Campaign).where(Campaign.name.like("demo_%")))
    session.execute(delete(User).where(User.external_id.like("demo_user_%")))
    session.commit()


def create_campaigns(
    session: Session,
    period_start: datetime,
    period_end: datetime,
) -> dict[str, uuid.UUID]:
    campaigns: list[Campaign] = []
    campaign_ids: dict[str, uuid.UUID] = {}
    for source, (name, medium) in CAMPAIGNS.items():
        campaign_id = uuid.uuid4()
        campaign_ids[source] = campaign_id
        campaigns.append(
            Campaign(
                id=campaign_id,
                name=name,
                source=source,
                medium=medium,
                description=f"Demo acquisition campaign for {source}",
                metadata_={"demo_seed": True, "quality_goal": source == "Referral"},
                starts_at=period_start,
                ends_at=period_end,
                is_active=True,
            )
        )
    session.bulk_save_objects(campaigns)
    session.flush()
    return campaign_ids


def create_users(period_start: datetime) -> tuple[list[User], dict[str, list[User]]]:
    users: list[User] = []
    source_users: dict[str, list[User]] = {source: [] for source in SOURCE_COUNTS}
    counter = 1
    for source, count in SOURCE_COUNTS.items():
        for _ in range(count):
            user_id = uuid.uuid4()
            created_at = period_start + timedelta(
                seconds=random.randint(0, 90 * 24 * 60 * 60 - 1)
            )
            user = User(
                id=user_id,
                external_id=f"demo_user_{counter:05d}",
                email=f"demo.user.{counter:05d}@example.com",
                anonymous_id=f"demo_anon_{counter:05d}",
                traits={
                    "country": random.choice(COUNTRIES),
                    "device": random.choices(DEVICES, weights=[58, 38, 4], k=1)[0],
                    "acquisition_source": source,
                    "risk_segment": random.choices(
                        ["retail", "pro", "vip"], weights=[78, 18, 4], k=1
                    )[0],
                },
                created_at=created_at,
                updated_at=created_at,
            )
            users.append(user)
            source_users[source].append(user)
            counter += 1

    for source in source_users:
        random.shuffle(source_users[source])
    random.shuffle(users)
    return users, source_users


def allocate_funnel_users(source_users: dict[str, list[User]]) -> dict[str, set[uuid.UUID]]:
    stage_users: dict[str, set[uuid.UUID]] = {
        "landing_page_viewed": {user.id for users in source_users.values() for user in users}
    }
    for event_name in FUNNEL_TARGETS:
        if event_name == "landing_page_viewed":
            continue
        users_for_stage: set[uuid.UUID] = set()
        for source, targets in SOURCE_STAGE_TARGETS.items():
            users_for_stage.update(user.id for user in source_users[source][: targets[event_name]])
        stage_users[event_name] = users_for_stage

    for event_name, expected in FUNNEL_TARGETS.items():
        actual = len(stage_users[event_name])
        if actual != expected:
            raise RuntimeError(f"{event_name} target mismatch: expected {expected}, got {actual}")
    return stage_users


def create_events(
    users: list[User],
    stage_users: dict[str, set[uuid.UUID]],
    period_start: datetime,
    period_end: datetime,
) -> list[Event]:
    events: list[Event] = []
    event_counter = 1
    first_trade_at: dict[uuid.UUID, datetime] = {}
    user_by_id = {user.id: user for user in users}

    for user in users:
        source = user.traits["acquisition_source"] if user.traits else "Direct"
        landing_at = random_time(period_start, period_end - timedelta(days=2))
        timestamps = {
            "landing_page_viewed": landing_at,
            "user_signed_up": landing_at + timedelta(minutes=random.randint(3, 180)),
            "kyc_started": landing_at + timedelta(hours=random.randint(2, 16)),
            "kyc_completed": landing_at + timedelta(hours=random.randint(8, 72)),
            "deposit_started": landing_at + timedelta(days=random.randint(1, 7)),
            "deposit_completed": landing_at + timedelta(days=random.randint(2, 12)),
            "trade_opened": landing_at + timedelta(days=random.randint(3, 21)),
        }

        for event_name in FUNNEL_TARGETS:
            if user.id not in stage_users[event_name]:
                continue
            timestamp = min(timestamps[event_name], period_end - timedelta(minutes=15))
            if event_name == "trade_opened":
                first_trade_at[user.id] = timestamp
            events.append(
                build_event(
                    event_counter,
                    user,
                    event_name,
                    timestamp,
                    source,
                    properties_for(event_name, source),
                )
            )
            event_counter += 1

    for user_id, opened_at in first_trade_at.items():
        if random.random() <= 0.9:
            user = user_by_id[user_id]
            source = user.traits["acquisition_source"] if user.traits else "Direct"
            events.append(
                build_event(
                    event_counter,
                    user,
                    "trade_closed",
                    min(opened_at + timedelta(minutes=random.randint(12, 240)), period_end),
                    source,
                    trade_properties(source, closed=True),
                )
            )
            event_counter += 1

    trader_ids = list(first_trade_at)
    trader_index = 0
    while len(events) < MIN_EVENTS:
        user = user_by_id[trader_ids[trader_index % len(trader_ids)]]
        source = user.traits["acquisition_source"] if user.traits else "Direct"
        opened_at = random_time(
            first_trade_at[user.id] + timedelta(hours=1),
            period_end - timedelta(minutes=30),
        )
        closed_at = min(opened_at + timedelta(minutes=random.randint(5, 360)), period_end)
        events.append(
            build_event(
                event_counter,
                user,
                "trade_opened",
                opened_at,
                source,
                trade_properties(source, closed=False),
            )
        )
        event_counter += 1
        events.append(
            build_event(
                event_counter,
                user,
                "trade_closed",
                closed_at,
                source,
                trade_properties(source, closed=True),
            )
        )
        event_counter += 1
        trader_index += 1

    events.sort(key=lambda event: event.timestamp)
    return events


def build_event(
    counter: int,
    user: User,
    event_name: str,
    timestamp: datetime,
    source: str,
    properties: dict[str, Any],
) -> Event:
    event_type = "page" if event_name == "landing_page_viewed" else "track"
    return Event(
        id=uuid.uuid4(),
        event_id=f"demo_evt_{counter:07d}",
        event_name=event_name,
        event_type=event_type,
        user_id=user.id,
        anonymous_id=user.anonymous_id,
        properties={
            **properties,
            "source": source,
            "campaign": CAMPAIGNS[source][0],
            "demo_seed": True,
        },
        context={
            "ip_country": user.traits.get("country") if user.traits else None,
            "device": user.traits.get("device") if user.traits else None,
            "library": "demo-seed",
        },
        timestamp=timestamp,
        received_at=timestamp + timedelta(seconds=random.randint(1, 30)),
        message_id=f"demo_msg_{counter:07d}",
        page_name="BitMEX Growth Landing" if event_type == "page" else None,
        page_url="https://demo.bitmex.com/growth" if event_type == "page" else None,
        created_at=timestamp,
        updated_at=timestamp,
    )


def properties_for(event_name: str, source: str) -> dict[str, Any]:
    if event_name == "landing_page_viewed":
        return {
            "utm_source": source.lower(),
            "utm_medium": CAMPAIGNS[source][1],
            "landing_variant": random.choice(["perps", "copy_trading", "bonus", "security"]),
        }
    if event_name == "user_signed_up":
        return {"signup_method": random.choice(["email", "google", "apple"])}
    if event_name.startswith("kyc"):
        return {"kyc_provider": "sumsub", "region": random.choice(COUNTRIES)}
    if event_name.startswith("deposit"):
        return {"asset": random.choice(["USDT", "BTC", "ETH"]), "amount_usd": deposit_amount(source)}
    if event_name == "trade_opened":
        return trade_properties(source, closed=False)
    return {}


def trade_properties(source: str, *, closed: bool) -> dict[str, Any]:
    notional = round(deposit_amount(source) * random.uniform(1.2, 6.0), 2)
    properties: dict[str, Any] = {
        "symbol": random.choice(SYMBOLS),
        "side": random.choice(["long", "short"]),
        "leverage": random.choice([2, 3, 5, 10, 20]),
        "notional_usd": notional,
    }
    if closed:
        quality_bias = 1.35 if source == "Referral" else 1.0
        properties["pnl_usd"] = round(random.uniform(-0.08, 0.14) * notional * quality_bias, 2)
        properties["close_reason"] = random.choice(["take_profit", "stop_loss", "manual"])
    return properties


def deposit_amount(source: str) -> float:
    base = random.lognormvariate(7.0, 0.65)
    return round(max(25.0, min(base * SOURCE_DEPOSIT_MULTIPLIER[source], 50_000.0)), 2)


def create_attributions(
    users: list[User],
    stage_users: dict[str, set[uuid.UUID]],
    campaign_ids: dict[str, uuid.UUID],
) -> list[Attribution]:
    attributions: list[Attribution] = []
    signup_users = stage_users["user_signed_up"]
    for user in users:
        source = user.traits["acquisition_source"] if user.traits else "Direct"
        campaign_name = CAMPAIGNS[source][0]
        first_touch_at = user.created_at
        attributions.append(
            Attribution(
                id=uuid.uuid4(),
                user_id=user.id,
                campaign_id=campaign_ids[source],
                source=source,
                medium=CAMPAIGNS[source][1],
                campaign_name=campaign_name,
                touch_type="first_touch",
                attributed_at=first_touch_at,
                created_at=first_touch_at,
                updated_at=first_touch_at,
            )
        )
        if user.id in signup_users:
            last_source = source if random.random() < 0.82 else random.choice(list(SOURCE_COUNTS))
            last_touch_at = first_touch_at + timedelta(minutes=random.randint(5, 240))
            attributions.append(
                Attribution(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    campaign_id=campaign_ids[last_source],
                    source=last_source,
                    medium=CAMPAIGNS[last_source][1],
                    campaign_name=CAMPAIGNS[last_source][0],
                    touch_type="last_touch",
                    attributed_at=last_touch_at,
                    created_at=last_touch_at,
                    updated_at=last_touch_at,
                )
            )
    return attributions


def create_snapshots(
    events: list[Event],
    stage_users: dict[str, set[uuid.UUID]],
    period_start: datetime,
    period_end: datetime,
) -> list[AnalyticsSnapshot]:
    source_by_user = {
        event.user_id: event.properties["source"]
        for event in events
        if event.event_name == "landing_page_viewed" and event.user_id
    }
    trade_users = stage_users["trade_opened"]
    deposit_users = stage_users["deposit_completed"]
    source_metrics = []
    for source, landing_count in SOURCE_COUNTS.items():
        source_user_ids = {user_id for user_id, item_source in source_by_user.items() if item_source == source}
        source_metrics.append(
            {
                "source": source,
                "landing_users": landing_count,
                "signup_users": len(stage_users["user_signed_up"] & source_user_ids),
                "deposit_users": len(deposit_users & source_user_ids),
                "trade_users": len(trade_users & source_user_ids),
                "trade_conversion_rate": round((len(trade_users & source_user_ids) / landing_count) * 100, 2),
                "quality_score": 98 if source == "Referral" else 92 if source == "Telegram" else 84,
            }
        )

    funnel_steps = [
        {
            "event_name": event_name,
            "label": event_name.replace("_", " ").title(),
            "users": len(stage_users[event_name]),
            "conversion_from_landing": round(
                (len(stage_users[event_name]) / FUNNEL_TARGETS["landing_page_viewed"]) * 100, 2
            ),
        }
        for event_name in FUNNEL_TARGETS
    ]
    dropoffs = []
    previous_event = None
    for event_name in FUNNEL_TARGETS:
        if previous_event:
            previous_count = len(stage_users[previous_event])
            current_count = len(stage_users[event_name])
            dropoffs.append(
                {
                    "from": previous_event,
                    "to": event_name,
                    "users_lost": previous_count - current_count,
                    "dropoff_rate": round(((previous_count - current_count) / previous_count) * 100, 2),
                }
            )
        previous_event = event_name

    return [
        snapshot(
            "demo_funnel",
            period_start,
            period_end,
            {
                "demo_seed": True,
                "funnel_name": "demo_full_crypto_activation",
                "steps": funnel_steps,
                "total_entered": 10_000,
                "total_completed": 950,
                "completion_rate": 9.5,
            },
        ),
        snapshot(
            "demo_dropoff",
            period_start,
            period_end,
            {"demo_seed": True, "largest_dropoff": "landing_page_viewed_to_user_signed_up", "dropoffs": dropoffs},
        ),
        snapshot(
            "demo_attribution",
            period_start,
            period_end,
            {
                "demo_seed": True,
                "top_traffic_source": "Google",
                "highest_converting_source": "Telegram",
                "highest_quality_source": "Referral",
                "sources": source_metrics,
            },
        ),
        snapshot(
            "demo_retention",
            period_start,
            period_end,
            {
                "demo_seed": True,
                "cohort_size": 5000,
                "d1_retention": 42.8,
                "d7_retention": 24.6,
                "d30_retention": 11.9,
            },
        ),
        snapshot(
            "demo_event_volume",
            period_start,
            period_end,
            {
                "demo_seed": True,
                "total_events": len(events),
                "events_by_name": dict(Counter(event.event_name for event in events)),
            },
        ),
    ]


def snapshot(
    snapshot_type: str,
    period_start: datetime,
    period_end: datetime,
    metrics: dict[str, Any],
) -> AnalyticsSnapshot:
    return AnalyticsSnapshot(
        id=uuid.uuid4(),
        snapshot_type=snapshot_type,
        period_start=period_start,
        period_end=period_end,
        metrics=metrics,
        created_at=period_end,
        updated_at=period_end,
    )


def create_health_scores(period_start: datetime, period_end: datetime) -> list[HealthScore]:
    scores: list[HealthScore] = []
    cursor = period_start
    while cursor < period_end:
        window_end = min(cursor + timedelta(days=7), period_end)
        score = round(random.uniform(94.0, 98.8), 2)
        scores.append(
            HealthScore(
                id=uuid.uuid4(),
                score=score,
                period_start=cursor,
                period_end=window_end,
                breakdown={
                    "demo_seed": True,
                    "summary": {
                        "duplicate_groups": random.randint(0, 3),
                        "duplicate_events": random.randint(0, 8),
                        "schema_error_count": random.randint(0, 6),
                        "missing_property_count": random.randint(0, 10),
                        "volume_anomaly_count": random.randint(0, 1),
                        "broken_funnel_paths": random.randint(0, 5),
                    },
                    "penalties": {
                        "duplicate_penalty": round(random.uniform(0.0, 0.8), 2),
                        "schema_penalty": round(random.uniform(0.0, 1.1), 2),
                        "missing_property_penalty": round(random.uniform(0.0, 0.7), 2),
                        "anomaly_penalty": round(random.uniform(0.0, 0.6), 2),
                        "funnel_integrity_penalty": round(random.uniform(0.0, 0.9), 2),
                    },
                },
                check_type="demo_data_quality",
                created_at=window_end,
                updated_at=window_end,
            )
        )
        cursor = window_end
    return scores


def random_time(start: datetime, end: datetime) -> datetime:
    if end <= start:
        return start
    delta_seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, delta_seconds))


if __name__ == "__main__":
    main()
