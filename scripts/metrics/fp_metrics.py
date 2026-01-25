"""
False Positive and Noise Metrics.

Provides two-stage FP/noise measurement:
1. Case-level FPR: How many FP test cases had false positives
2. Finding-level FPR: Total count of false findings in FP cases
3. TP Noise Rate: Extra findings in true positive cases
"""

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class FPMetrics:
    """False Positive metrics at both case and finding levels."""

    # Case-level metrics (existing)
    total_fp_cases: int = 0  # Total FP test cases (expected_detection=False)
    fp_cases_with_critical: int = 0  # FP cases where critical was flagged
    fp_cases_with_major: int = 0  # FP cases where major was flagged
    fp_cases_with_any: int = 0  # FP cases with any issue flagged
    case_fpr: float = 0.0  # fp_cases_with_critical / total_fp_cases

    # Finding-level metrics (new)
    total_findings_in_fp: int = 0  # All findings across all FP cases
    critical_findings_in_fp: int = 0  # Critical findings in FP cases
    major_findings_in_fp: int = 0  # Major findings in FP cases
    minor_findings_in_fp: int = 0  # Minor findings in FP cases
    finding_fpr: float = 0.0  # total_findings_in_fp / total_fp_cases

    # Breakdown by severity
    fp_breakdown: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class TPNoiseMetrics:
    """Noise metrics for True Positive cases."""

    # Totals
    total_tp_cases: int = 0  # Cases with expected_detection=True
    detected_tp_cases: int = 0  # TP cases where bug was actually detected

    # Finding counts
    total_findings_in_tp: int = 0  # All findings in TP cases
    expected_findings_in_tp: int = 0  # Findings matching expected bug (approximated as 1 per detected case)
    noise_findings_in_tp: int = 0  # total - expected

    # Noise rate
    noise_rate_in_tp: float = 0.0  # noise_findings / total_findings

    # By severity breakdown
    noise_breakdown: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


def calculate_fp_metrics(evaluations: list[dict[str, Any]]) -> FPMetrics:
    """Calculate false positive metrics from evaluations.

    Args:
        evaluations: List of evaluation result dictionaries

    Returns:
        FPMetrics with case-level and finding-level FP analysis
    """
    # Filter to FP cases (expected_detection=False)
    fp_evals = [e for e in evaluations if not e.get("expected_detection", True)]

    if not fp_evals:
        return FPMetrics()

    total_fp_cases = len(fp_evals)

    # Case-level counts
    fp_cases_with_critical = 0
    fp_cases_with_major = 0
    fp_cases_with_any = 0

    # Finding-level counts
    total_findings = 0
    critical_findings = 0
    major_findings = 0
    minor_findings = 0

    for e in fp_evals:
        critical = e.get("critical_count", 0)
        major = e.get("major_count", 0)
        minor = e.get("minor_count", 0)
        issue_count = e.get("review_issue_count", critical + major + minor)

        # Case-level
        if critical > 0:
            fp_cases_with_critical += 1
        if major > 0:
            fp_cases_with_major += 1
        if issue_count > 0:
            fp_cases_with_any += 1

        # Finding-level
        total_findings += issue_count
        critical_findings += critical
        major_findings += major
        minor_findings += minor

    # Calculate rates
    case_fpr = fp_cases_with_critical / total_fp_cases if total_fp_cases > 0 else 0.0
    finding_fpr = total_findings / total_fp_cases if total_fp_cases > 0 else 0.0

    return FPMetrics(
        total_fp_cases=total_fp_cases,
        fp_cases_with_critical=fp_cases_with_critical,
        fp_cases_with_major=fp_cases_with_major,
        fp_cases_with_any=fp_cases_with_any,
        case_fpr=case_fpr,
        total_findings_in_fp=total_findings,
        critical_findings_in_fp=critical_findings,
        major_findings_in_fp=major_findings,
        minor_findings_in_fp=minor_findings,
        finding_fpr=finding_fpr,
        fp_breakdown={
            "critical": critical_findings,
            "major": major_findings,
            "minor": minor_findings,
        },
    )


def calculate_tp_noise_metrics(evaluations: list[dict[str, Any]]) -> TPNoiseMetrics:
    """Calculate noise metrics for True Positive cases.

    Noise = findings beyond the expected bug detection.

    Args:
        evaluations: List of evaluation result dictionaries

    Returns:
        TPNoiseMetrics with noise analysis for TP cases
    """
    # Filter to TP cases (expected_detection=True)
    tp_evals = [e for e in evaluations if e.get("expected_detection", True)]

    if not tp_evals:
        return TPNoiseMetrics()

    total_tp_cases = len(tp_evals)
    detected_tp_cases = sum(1 for e in tp_evals if e.get("detected", False))

    # Finding counts
    total_findings = 0
    critical_findings = 0
    major_findings = 0
    minor_findings = 0

    for e in tp_evals:
        critical = e.get("critical_count", 0)
        major = e.get("major_count", 0)
        minor = e.get("minor_count", 0)
        issue_count = e.get("review_issue_count", critical + major + minor)

        total_findings += issue_count
        critical_findings += critical
        major_findings += major
        minor_findings += minor

    # Expected findings = 1 per detected case (the actual bug)
    expected_findings = detected_tp_cases
    noise_findings = max(0, total_findings - expected_findings)

    # Noise rate
    noise_rate = noise_findings / total_findings if total_findings > 0 else 0.0

    # Noise breakdown: findings beyond expected
    # Approximation: if detected, 1 finding is valid, rest is noise
    # For more precise tracking, we'd need to match findings to expected bugs
    noise_critical = max(0, critical_findings - detected_tp_cases)
    noise_major = major_findings if critical_findings >= detected_tp_cases else max(0, major_findings - (detected_tp_cases - critical_findings))
    noise_minor = minor_findings

    return TPNoiseMetrics(
        total_tp_cases=total_tp_cases,
        detected_tp_cases=detected_tp_cases,
        total_findings_in_tp=total_findings,
        expected_findings_in_tp=expected_findings,
        noise_findings_in_tp=noise_findings,
        noise_rate_in_tp=noise_rate,
        noise_breakdown={
            "critical_noise": noise_critical,
            "major_noise": noise_major,
            "minor_noise": noise_minor,
        },
    )


def calculate_all_fp_noise_metrics(
    evaluations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate all FP and noise metrics.

    Combines both FP metrics and TP noise metrics into a single result.

    Args:
        evaluations: List of evaluation result dictionaries

    Returns:
        Dict with fp_metrics and tp_noise_metrics
    """
    fp_metrics = calculate_fp_metrics(evaluations)
    tp_noise_metrics = calculate_tp_noise_metrics(evaluations)

    return {
        "fp_metrics": fp_metrics.to_dict(),
        "tp_noise_metrics": tp_noise_metrics.to_dict(),
    }
