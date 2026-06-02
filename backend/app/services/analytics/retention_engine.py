"""Retention and cohort computation logic."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from app.repositories.analytics_repository import UserEventRecord


@dataclass(frozen=True)
class RetentionPeriodMetrics:
    day: int
    retained_users: int
    retention_rate: float


@dataclass(frozen=True)
class RetentionComputationResult:
    anchor_event: str
    cohort_size: int
    periods: list[RetentionPeriodMetrics]


@dataclass(frozen=True)
class CohortRetentionRow:
    cohort_date: date
    cohort_size: int
    d1_retention: float
    d7_retention: float
    d30_retention: float


@dataclass(frozen=True)
class CohortComputationResult:
    anchor_event: str
    cohorts: list[CohortRetentionRow]


class RetentionAnalyticsEngine:
    """D1 / D7 / D30 retention from anchor and activity events."""

    def compute_retention(
        self,
        *,
        anchor_event: str,
        activity_events: frozenset[str],
        anchor_records: list[UserEventRecord],
        activity_records: list[UserEventRecord],
        retention_days: tuple[int, ...] = (1, 7, 30),
    ) -> RetentionComputationResult:
        cohort = self._first_anchor_by_identity(anchor_records)
        activity_by_identity = self._group_activity_dates(activity_records, activity_events)

        periods: list[RetentionPeriodMetrics] = []
        cohort_size = len(cohort)

        for day in retention_days:
            retained = 0
            for identity, anchor_dt in cohort.items():
                target_day = anchor_dt.date() + timedelta(days=day)
                activity_dates = activity_by_identity.get(identity, set())
                if target_day in activity_dates:
                    retained += 1
            rate = round((retained / cohort_size) * 100, 2) if cohort_size > 0 else 0.0
            periods.append(
                RetentionPeriodMetrics(day=day, retained_users=retained, retention_rate=rate)
            )

        return RetentionComputationResult(
            anchor_event=anchor_event,
            cohort_size=cohort_size,
            periods=periods,
        )

    def compute_cohorts(
        self,
        *,
        anchor_event: str,
        activity_events: frozenset[str],
        anchor_records: list[UserEventRecord],
        activity_records: list[UserEventRecord],
    ) -> CohortComputationResult:
        cohort = self._first_anchor_by_identity(anchor_records)
        activity_by_identity = self._group_activity_dates(activity_records, activity_events)

        cohorts_by_date: dict[date, list[str]] = {}
        for identity, anchor_dt in cohort.items():
            cohorts_by_date.setdefault(anchor_dt.date(), []).append(identity)

        rows: list[CohortRetentionRow] = []
        for cohort_date in sorted(cohorts_by_date):
            identities = cohorts_by_date[cohort_date]
            size = len(identities)
            rows.append(
                CohortRetentionRow(
                    cohort_date=cohort_date,
                    cohort_size=size,
                    d1_retention=self._retention_for_day(
                        identities, cohort_date, 1, activity_by_identity
                    ),
                    d7_retention=self._retention_for_day(
                        identities, cohort_date, 7, activity_by_identity
                    ),
                    d30_retention=self._retention_for_day(
                        identities, cohort_date, 30, activity_by_identity
                    ),
                )
            )

        return CohortComputationResult(anchor_event=anchor_event, cohorts=rows)

    @staticmethod
    def _first_anchor_by_identity(
        records: list[UserEventRecord],
    ) -> dict[str, datetime]:
        cohort: dict[str, datetime] = {}
        for record in sorted(records, key=lambda r: r.timestamp):
            if record.identity not in cohort:
                ts = record.timestamp
                cohort[record.identity] = ts if ts.tzinfo else ts.replace(tzinfo=UTC)
        return cohort

    @staticmethod
    def _group_activity_dates(
        records: list[UserEventRecord],
        activity_events: frozenset[str],
    ) -> dict[str, set[date]]:
        grouped: dict[str, set[date]] = {}
        for record in records:
            if record.event_name not in activity_events:
                continue
            ts = record.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
            grouped.setdefault(record.identity, set()).add(ts.date())
        return grouped

    @staticmethod
    def _retention_for_day(
        identities: list[str],
        cohort_date: date,
        day: int,
        activity_by_identity: dict[str, set[date]],
    ) -> float:
        if not identities:
            return 0.0
        target = cohort_date + timedelta(days=day)
        retained = sum(1 for i in identities if target in activity_by_identity.get(i, set()))
        return round((retained / len(identities)) * 100, 2)
