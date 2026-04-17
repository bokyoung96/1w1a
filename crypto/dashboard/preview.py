from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib

from crypto.factory import (
    CandidateEvaluation,
    CandidatePerformanceMetrics,
    CandidateRobustnessMetrics,
    SelectionCandidate,
    SelectionPolicy,
    build_allocation_trigger,
    build_portfolio_allocation,
    generate_candidate_pool,
    rank_candidates,
    select_orthogonal_candidates,
)
from crypto.paper import PaperSession
from crypto.reporting import build_factory_overview, build_paper_performance_report
from crypto.strategies import DEFAULT_STRATEGIES
from root import ROOT


_STARTED_AT = datetime(2026, 3, 1, tzinfo=timezone.utc)
_CANDIDATE_POOL_SIZE = 40
_FAMILY_CAP = 3
_MAX_SELECTED = 10


class CryptoDashboardPreviewService:
    def build(self) -> dict[str, object]:
        candidates = generate_candidate_pool(target_count=_CANDIDATE_POOL_SIZE, random_seed=17)
        evaluations = tuple(self._build_evaluation(candidate) for candidate in candidates)
        ranked = rank_candidates(evaluations, turnover_penalty_rate=0.07)
        selection_candidates = tuple(
            SelectionCandidate(
                scorecard=scorecard,
                returns=self._candidate_returns(scorecard.candidate.candidate_id, scorecard.candidate.family),
                signal_strength=self._signal_strength(scorecard.candidate.candidate_id),
                instrument_symbol="BTC/USDT:USDT",
            )
            for scorecard in ranked
        )
        selection = select_orthogonal_candidates(
            selection_candidates,
            policy=SelectionPolicy(
                max_selected=_MAX_SELECTED,
                max_pairwise_correlation=0.70,
                max_per_family=_FAMILY_CAP,
                family_diversity_bonus=0.05,
            ),
        )
        trigger = build_allocation_trigger(
            "hybrid_event_rebalance",
            event_keys=("funding", "momentum", "volatility"),
            triggered_at=_STARTED_AT + timedelta(days=30),
        )
        allocation = build_portfolio_allocation(selection.selected, trigger=trigger)
        overview = build_factory_overview(
            selection,
            allocation,
            candidate_pool_size=len(candidates),
            strategy_definitions=DEFAULT_STRATEGIES,
        )
        report = build_paper_performance_report(
            self._build_paper_session(selection.selected),
            strategy_definitions=DEFAULT_STRATEGIES,
            factory_overview=overview,
        )
        assert report.factory_overview is not None

        selected_ids = {entry.candidate_id for entry in report.factory_overview.selected_basket}
        scores_by_strategy: dict[str, list[float]] = {}
        candidate_counts: dict[str, int] = {}
        for scorecard in ranked:
            scores_by_strategy.setdefault(scorecard.candidate.strategy_name, []).append(scorecard.total_score)
            candidate_counts[scorecard.candidate.strategy_name] = candidate_counts.get(scorecard.candidate.strategy_name, 0) + 1

        return {
            "summary": {
                "candidate_pool_size": report.factory_overview.candidate_pool_size,
                "selected_basket_size": len(report.factory_overview.selected_basket),
                "registered_strategy_count": len(DEFAULT_STRATEGIES),
                "family_cap": _FAMILY_CAP,
                "trigger_reason": report.factory_overview.trigger_reason,
            },
            "performance_summary": {
                "total_return": report.summary.total_return,
                "max_drawdown": report.summary.max_drawdown,
                "paper_sharpe": report.summary.paper_sharpe,
                "paper_days": report.summary.paper_days,
                "realized_fees": report.summary.realized_fees,
                "net_funding": report.summary.net_funding,
            },
            "performance": {
                "equity_curve": self._graph_points(report.graphs, "equity_curve"),
                "drawdown_curve": self._graph_points(report.graphs, "drawdown_curve"),
                "gross_exposure_curve": self._graph_points(report.graphs, "gross_exposure_curve"),
                "net_exposure_curve": self._graph_points(report.graphs, "net_exposure_curve"),
            },
            "selected_basket": [
                {
                    "candidate_id": entry.candidate_id,
                    "strategy_name": entry.strategy_name,
                    "family": entry.family,
                    "primary_cadence": entry.primary_cadence,
                    "feature_cadences": list(entry.feature_cadences),
                    "total_score": entry.total_score,
                    "max_pairwise_correlation": entry.max_pairwise_correlation,
                    "target_weight": entry.target_weight,
                    "documentation_path": self._doc_path(entry.strategy_name),
                    "rationale_excerpt": self._economic_rationale(entry.strategy_name),
                    "execution_stages": [
                        {
                            "stage": stage.stage,
                            "fraction": stage.fraction,
                            "target_weight": stage.target_weight,
                        }
                        for stage in entry.execution_stages
                    ],
                }
                for entry in report.factory_overview.selected_basket
            ],
            "family_allocations": [
                {
                    "family": entry.family,
                    "weight": entry.weight,
                    "strategy_count": entry.strategy_count,
                }
                for entry in report.factory_overview.family_allocations
            ],
            "instrument_allocations": [
                {
                    "instrument_symbol": entry.instrument_symbol,
                    "net_target_weight": entry.net_target_weight,
                    "gross_target_weight": entry.gross_target_weight,
                    "contributor_count": entry.contributor_count,
                }
                for entry in report.factory_overview.instrument_allocations
            ],
            "registry": [
                {
                    "name": strategy.name,
                    "family": strategy.family,
                    "primary_cadence": strategy.primary_cadence,
                    "feature_cadences": list(strategy.feature_cadences),
                    "candidate_count": candidate_counts.get(strategy.name, 0),
                    "selected": any(candidate_id.startswith(f"{strategy.name}:") for candidate_id in selected_ids),
                    "top_score": max(scores_by_strategy.get(strategy.name, [0.0])),
                    "documentation_path": self._doc_path(strategy.name),
                    "rationale_excerpt": self._economic_rationale(strategy.name),
                }
                for strategy in DEFAULT_STRATEGIES
            ],
        }

    def _build_evaluation(self, candidate) -> CandidateEvaluation:
        quality = self._unit_interval(candidate.candidate_id)
        family_bias = 0.01 * (1 + self._family_index(candidate.family))
        gross_return = 0.08 + (quality * 0.12) + family_bias
        turnover = 0.18 + (self._unit_interval(f"{candidate.candidate_id}:turnover") * 0.85)
        transaction_cost = 0.008 + (turnover * 0.012)
        post_cost_return = gross_return - transaction_cost
        return CandidateEvaluation(
            candidate=candidate,
            performance=CandidatePerformanceMetrics(
                gross_return=round(gross_return, 6),
                post_cost_return=round(post_cost_return, 6),
                turnover=round(turnover, 6),
                transaction_cost=round(transaction_cost, 6),
            ),
            robustness=CandidateRobustnessMetrics(
                oos_stability=round(0.48 + (self._unit_interval(f"{candidate.candidate_id}:oos") * 0.44), 6),
                parameter_stability=round(0.42 + (self._unit_interval(f"{candidate.candidate_id}:params") * 0.40), 6),
                regime_stability=round(0.45 + (self._unit_interval(f"{candidate.candidate_id}:regime") * 0.42), 6),
            ),
        )

    def _candidate_returns(self, candidate_id: str, family: str) -> tuple[float, ...]:
        family_index = self._family_index(family)
        anchor = family_index * 3
        noise_scale = 0.0006
        base = [-0.0012 for _ in range(30)]
        base[anchor] = 0.014 + (family_index * 0.0003)
        base[min(anchor + 1, 29)] = 0.007 + (family_index * 0.0002)
        returns: list[float] = []
        for step, basis in enumerate(base):
            noise = (self._unit_interval(f"{candidate_id}:{step}") - 0.5) * noise_scale
            returns.append(round(basis + noise, 6))
        return tuple(returns)

    def _signal_strength(self, candidate_id: str) -> float:
        return 1.0 if self._unit_interval(f"{candidate_id}:signal") >= 0.35 else -1.0

    def _build_paper_session(self, selected) -> PaperSession:
        session = PaperSession(
            session_id="crypto_factory_preview",
            strategy_id="crypto_factory_basket",
            started_at=_STARTED_AT,
            feature_cadences=("15m", "1h", "4h"),
        )
        equity = 100_000.0
        for day in range(30):
            weighted_return = 0.0
            gross_exposure = 0.0
            net_exposure = 0.0
            for strategy in selected:
                weight = abs(strategy.selection_score) / max(len(selected), 1)
                direction = 1.0 if strategy.signal_strength >= 0 else -1.0
                weighted_return += strategy.returns[day] * direction * weight
                gross_exposure += abs(weight)
                net_exposure += weight * direction

            equity *= 1.0 + weighted_return
            session.record_equity(
                at=_STARTED_AT + timedelta(days=day + 1),
                equity=round(equity, 6),
                gross_exposure=round(gross_exposure, 6),
                net_exposure=round(net_exposure, 6),
            )
        return session

    @staticmethod
    def _graph_points(graphs, slug: str) -> list[dict[str, object]]:
        for graph in graphs:
            if graph.slug == slug:
                return [
                    {"date": point.at.date().isoformat(), "value": point.value}
                    for point in graph.points
                ]
        return []

    @staticmethod
    def _unit_interval(value: str) -> float:
        digest = hashlib.sha1(value.encode("utf-8")).hexdigest()
        return int(digest[:12], 16) / float(0xFFFFFFFFFFFF)

    @staticmethod
    def _family_index(family: str) -> int:
        for index, strategy in enumerate(DEFAULT_STRATEGIES):
            if strategy.family == family:
                return index
        return 0

    @staticmethod
    def _doc_path(strategy_name: str) -> str:
        return f"crypto/strategies/docs/{strategy_name}.md"

    @staticmethod
    def _economic_rationale(strategy_name: str) -> str:
        doc_path = ROOT.root / "crypto" / "strategies" / "docs" / f"{strategy_name}.md"
        if not doc_path.is_file():
            return ""
        content = doc_path.read_text(encoding="utf-8")
        capture = False
        lines: list[str] = []
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if line.startswith("## "):
                capture = line.lower() == "## economic rationale"
                continue
            if capture:
                if not line:
                    if lines:
                        break
                    continue
                lines.append(line)
        return " ".join(lines)
