"""Pure funnel, conversion, and dropoff computation logic."""

from dataclasses import dataclass

from app.domain.funnels import FunnelStepDefinition
from app.repositories.analytics_repository import UserEventRecord


@dataclass(frozen=True)
class FunnelStepMetrics:
    key: str
    label: str
    event_name: str
    users: int
    conversion_rate_from_previous: float | None
    conversion_rate_from_start: float


@dataclass(frozen=True)
class FunnelComputationResult:
    funnel_name: str
    steps: list[FunnelStepMetrics]
    total_entered: int
    total_completed: int
    completion_rate: float


@dataclass(frozen=True)
class DropoffStepMetrics:
    from_step: str
    to_step: str
    users_lost: int
    dropoff_rate: float


@dataclass(frozen=True)
class DropoffComputationResult:
    funnel_name: str
    steps: list[DropoffStepMetrics]
    largest_dropoff_step: str | None


class FunnelAnalyticsEngine:
    """Transforms grouped user events into funnel metrics."""

    def compute_funnel(
        self,
        *,
        funnel_name: str,
        step_definitions: list[FunnelStepDefinition],
        grouped_events: dict[str, list[UserEventRecord]],
    ) -> FunnelComputationResult:
        event_sequence = [s.event_name for s in step_definitions]
        depths = [
            self._funnel_depth(events, event_sequence)
            for events in grouped_events.values()
        ]

        step_metrics: list[FunnelStepMetrics] = []
        previous_users = 0

        for index, step_def in enumerate(step_definitions):
            users_at_step = sum(1 for depth in depths if depth >= index + 1)
            conv_from_prev = None
            if index == 0:
                conv_from_start = 100.0 if users_at_step > 0 else 0.0
            else:
                conv_from_prev = (
                    round((users_at_step / previous_users) * 100, 2)
                    if previous_users > 0
                    else 0.0
                )
                conv_from_start = (
                    round((users_at_step / step_metrics[0].users) * 100, 2)
                    if step_metrics[0].users > 0
                    else 0.0
                )

            step_metrics.append(
                FunnelStepMetrics(
                    key=step_def.key,
                    label=step_def.label,
                    event_name=step_def.event_name,
                    users=users_at_step,
                    conversion_rate_from_previous=conv_from_prev,
                    conversion_rate_from_start=conv_from_start,
                )
            )
            previous_users = users_at_step

        total_entered = step_metrics[0].users if step_metrics else 0
        total_completed = step_metrics[-1].users if step_metrics else 0
        completion_rate = (
            round((total_completed / total_entered) * 100, 2) if total_entered > 0 else 0.0
        )

        return FunnelComputationResult(
            funnel_name=funnel_name,
            steps=step_metrics,
            total_entered=total_entered,
            total_completed=total_completed,
            completion_rate=completion_rate,
        )

    def compute_dropoff(
        self,
        funnel_result: FunnelComputationResult,
    ) -> DropoffComputationResult:
        dropoff_steps: list[DropoffStepMetrics] = []
        largest_rate = -1.0
        largest_step: str | None = None

        for index in range(1, len(funnel_result.steps)):
            prev_step = funnel_result.steps[index - 1]
            curr_step = funnel_result.steps[index]
            users_lost = max(prev_step.users - curr_step.users, 0)
            dropoff_rate = (
                round((users_lost / prev_step.users) * 100, 2) if prev_step.users > 0 else 0.0
            )
            dropoff_steps.append(
                DropoffStepMetrics(
                    from_step=prev_step.key,
                    to_step=curr_step.key,
                    users_lost=users_lost,
                    dropoff_rate=dropoff_rate,
                )
            )
            if dropoff_rate > largest_rate:
                largest_rate = dropoff_rate
                largest_step = prev_step.key

        return DropoffComputationResult(
            funnel_name=funnel_result.funnel_name,
            steps=dropoff_steps,
            largest_dropoff_step=largest_step,
        )

    @staticmethod
    def _funnel_depth(events: list[UserEventRecord], steps: list[str]) -> int:
        if not events or not steps:
            return 0

        sorted_events = sorted(events, key=lambda e: e.timestamp)
        depth = 0
        search_from = 0

        for step_event in steps:
            found = False
            for idx in range(search_from, len(sorted_events)):
                if sorted_events[idx].event_name == step_event:
                    depth += 1
                    search_from = idx + 1
                    found = True
                    break
            if not found:
                break
        return depth
