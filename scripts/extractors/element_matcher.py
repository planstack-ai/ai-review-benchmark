"""
Element Matcher for AI Review Benchmark.

Matches extracted findings against expected elements (must_find) from meta.json.
Provides element-based evaluation instead of free-text comparison.
"""

from dataclasses import dataclass, field, asdict
from typing import Any

from .finding_extractor import ExtractedFinding, ExtractionResult


@dataclass
class ExpectedElement:
    """An expected finding element from meta.json must_find."""

    id: str  # Unique identifier
    category: str  # Expected category
    keywords: list[str]  # Keywords that should appear
    severity_expected: str  # Expected severity
    description: str = ""  # Human-readable description
    required: bool = True  # Whether this element must be found

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExpectedElement":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            category=data.get("category", "other"),
            keywords=data.get("keywords", []),
            severity_expected=data.get("severity_expected", "major"),
            description=data.get("description", ""),
            required=data.get("required", True),
        )


@dataclass
class ElementMatch:
    """A match between an extracted finding and an expected element."""

    expected_id: str  # ID of the expected element
    finding_index: int  # Index of the matched finding
    keyword_matches: list[str]  # Which keywords matched
    category_match: bool  # Whether category matched
    severity_match: bool  # Whether severity matched
    match_score: float  # Overall match score (0.0-1.0)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class MatchResult:
    """Result of matching extracted findings against expected elements."""

    # Match statistics
    matched_elements: list[ElementMatch] = field(default_factory=list)
    unmatched_expected: list[str] = field(default_factory=list)  # IDs of expected but not found
    extra_findings: list[int] = field(default_factory=list)  # Indices of findings not matching any expected

    # Scores
    element_recall: float = 0.0  # matched / total expected
    element_precision: float = 0.0  # matched / total findings
    severity_accuracy: float = 0.0  # correct severity / matched
    category_accuracy: float = 0.0  # correct category / matched

    # Summary
    total_expected: int = 0
    total_findings: int = 0
    total_matched: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "matched_elements": [m.to_dict() for m in self.matched_elements],
            "unmatched_expected": self.unmatched_expected,
            "extra_findings": self.extra_findings,
            "element_recall": self.element_recall,
            "element_precision": self.element_precision,
            "severity_accuracy": self.severity_accuracy,
            "category_accuracy": self.category_accuracy,
            "total_expected": self.total_expected,
            "total_findings": self.total_findings,
            "total_matched": self.total_matched,
        }

    @property
    def all_required_found(self) -> bool:
        """Check if all required elements were found."""
        return len(self.unmatched_expected) == 0

    @property
    def has_noise(self) -> bool:
        """Check if there are extra findings beyond expected."""
        return len(self.extra_findings) > 0


class ElementMatcher:
    """Matches extracted findings against expected elements."""

    def __init__(
        self,
        keyword_weight: float = 0.5,
        category_weight: float = 0.3,
        severity_weight: float = 0.2,
        match_threshold: float = 0.3,
    ):
        """Initialize the matcher.

        Args:
            keyword_weight: Weight for keyword matching in score
            category_weight: Weight for category matching in score
            severity_weight: Weight for severity matching in score
            match_threshold: Minimum score to consider a match
        """
        self.keyword_weight = keyword_weight
        self.category_weight = category_weight
        self.severity_weight = severity_weight
        self.match_threshold = match_threshold

    def _calculate_keyword_score(
        self,
        finding: ExtractedFinding,
        expected: ExpectedElement,
    ) -> tuple[float, list[str]]:
        """Calculate keyword match score.

        Args:
            finding: The extracted finding
            expected: The expected element

        Returns:
            Tuple of (score, matched_keywords)
        """
        if not expected.keywords:
            return 1.0, []  # No keywords required = automatic match

        search_text = f"{finding.evidence} {finding.impact} {finding.fix_proposal}".lower()
        matched = [kw for kw in expected.keywords if kw.lower() in search_text]

        score = len(matched) / len(expected.keywords)
        return score, matched

    def _calculate_category_score(
        self,
        finding: ExtractedFinding,
        expected: ExpectedElement,
    ) -> tuple[float, bool]:
        """Calculate category match score.

        Args:
            finding: The extracted finding
            expected: The expected element

        Returns:
            Tuple of (score, is_match)
        """
        # Normalize categories
        finding_cat = finding.category.lower().replace(" ", "_").replace("-", "_")
        expected_cat = expected.category.lower().replace(" ", "_").replace("-", "_")

        # Exact match
        if finding_cat == expected_cat:
            return 1.0, True

        # Related categories (partial match)
        related_groups = [
            {"calculation_error", "logic_error", "boundary_condition"},
            {"security", "authorization", "validation"},
            {"performance", "memory_leak", "resource_leak"},
            {"data_integrity", "transaction", "race_condition", "concurrency"},
            {"null_handling", "type_error"},
        ]

        for group in related_groups:
            if finding_cat in group and expected_cat in group:
                return 0.5, False  # Partial match

        return 0.0, False

    def _calculate_severity_score(
        self,
        finding: ExtractedFinding,
        expected: ExpectedElement,
    ) -> tuple[float, bool]:
        """Calculate severity match score.

        Args:
            finding: The extracted finding
            expected: The expected element

        Returns:
            Tuple of (score, is_match)
        """
        severity_order = ["info", "minor", "major", "critical"]

        finding_sev = finding.severity.lower()
        expected_sev = expected.severity_expected.lower()

        # Handle aliases
        if finding_sev == "high":
            finding_sev = "major"
        elif finding_sev == "low":
            finding_sev = "minor"

        if expected_sev == "high":
            expected_sev = "major"
        elif expected_sev == "low":
            expected_sev = "minor"

        if finding_sev == expected_sev:
            return 1.0, True

        # Adjacent severity = partial match
        try:
            finding_idx = severity_order.index(finding_sev)
            expected_idx = severity_order.index(expected_sev)
            if abs(finding_idx - expected_idx) == 1:
                return 0.5, False
        except ValueError:
            pass

        return 0.0, False

    def match_finding_to_element(
        self,
        finding: ExtractedFinding,
        expected: ExpectedElement,
    ) -> ElementMatch | None:
        """Try to match a finding to an expected element.

        Args:
            finding: The extracted finding
            expected: The expected element

        Returns:
            ElementMatch if score >= threshold, None otherwise
        """
        keyword_score, matched_keywords = self._calculate_keyword_score(finding, expected)
        category_score, category_match = self._calculate_category_score(finding, expected)
        severity_score, severity_match = self._calculate_severity_score(finding, expected)

        # Calculate weighted score
        total_score = (
            keyword_score * self.keyword_weight
            + category_score * self.category_weight
            + severity_score * self.severity_weight
        )

        if total_score >= self.match_threshold:
            return ElementMatch(
                expected_id=expected.id,
                finding_index=-1,  # Will be set by caller
                keyword_matches=matched_keywords,
                category_match=category_match,
                severity_match=severity_match,
                match_score=total_score,
            )

        return None

    def match(
        self,
        findings: list[ExtractedFinding],
        expected_elements: list[ExpectedElement],
    ) -> MatchResult:
        """Match all findings against all expected elements.

        Uses greedy matching: for each expected element, find the best matching finding.

        Args:
            findings: List of extracted findings
            expected_elements: List of expected elements

        Returns:
            MatchResult with match statistics
        """
        if not expected_elements:
            # No expected elements = all findings are noise
            return MatchResult(
                extra_findings=list(range(len(findings))),
                total_findings=len(findings),
            )

        matched_elements: list[ElementMatch] = []
        matched_finding_indices: set[int] = set()
        unmatched_expected: list[str] = []

        # For each expected element, find best matching finding
        for expected in expected_elements:
            best_match: ElementMatch | None = None
            best_finding_idx = -1

            for idx, finding in enumerate(findings):
                if idx in matched_finding_indices:
                    continue  # Already matched

                match = self.match_finding_to_element(finding, expected)
                if match and (best_match is None or match.match_score > best_match.match_score):
                    best_match = match
                    best_finding_idx = idx

            if best_match:
                best_match.finding_index = best_finding_idx
                matched_elements.append(best_match)
                matched_finding_indices.add(best_finding_idx)
            elif expected.required:
                unmatched_expected.append(expected.id)

        # Find extra findings (not matched to any expected)
        extra_findings = [i for i in range(len(findings)) if i not in matched_finding_indices]

        # Calculate scores
        total_expected = len([e for e in expected_elements if e.required])
        total_matched = len(matched_elements)
        total_findings = len(findings)

        element_recall = total_matched / total_expected if total_expected > 0 else 1.0
        element_precision = total_matched / total_findings if total_findings > 0 else 1.0

        severity_correct = sum(1 for m in matched_elements if m.severity_match)
        severity_accuracy = severity_correct / total_matched if total_matched > 0 else 0.0

        category_correct = sum(1 for m in matched_elements if m.category_match)
        category_accuracy = category_correct / total_matched if total_matched > 0 else 0.0

        return MatchResult(
            matched_elements=matched_elements,
            unmatched_expected=unmatched_expected,
            extra_findings=extra_findings,
            element_recall=element_recall,
            element_precision=element_precision,
            severity_accuracy=severity_accuracy,
            category_accuracy=category_accuracy,
            total_expected=total_expected,
            total_findings=total_findings,
            total_matched=total_matched,
        )


def match_findings(
    extraction_result: ExtractionResult,
    must_find: list[dict[str, Any]],
) -> MatchResult:
    """Convenience function to match extraction results against must_find list.

    Args:
        extraction_result: Result from FindingExtractor
        must_find: List of expected elements from meta.json

    Returns:
        MatchResult with match statistics
    """
    # Convert must_find to ExpectedElement objects
    expected_elements = [ExpectedElement.from_dict(e) for e in must_find]

    # Match
    matcher = ElementMatcher()
    return matcher.match(extraction_result.findings, expected_elements)


def evaluate_with_elements(
    review_result: dict[str, Any],
    must_find: list[dict[str, Any]],
    use_llm_extraction: bool = False,
) -> dict[str, Any]:
    """Full element-based evaluation pipeline.

    Args:
        review_result: AI review result with parsed_response
        must_find: List of expected elements from meta.json
        use_llm_extraction: Whether to use LLM for extraction

    Returns:
        Evaluation result dict compatible with existing evaluator
    """
    from .finding_extractor import FindingExtractor

    # Extract findings
    extractor = FindingExtractor()
    extraction = extractor.extract(review_result, use_llm=use_llm_extraction)

    # Match against expected
    match_result = match_findings(extraction, must_find)

    # Convert to evaluation-compatible format
    detected = match_result.element_recall >= 0.5  # At least half of expected found
    detection_score = match_result.element_recall

    # Map to accuracy (0-100)
    accuracy = int(match_result.element_recall * 100)

    return {
        "detected": detected,
        "detection_score": detection_score,
        "accuracy": accuracy,
        "noise_count": len(match_result.extra_findings),
        "reasoning": f"Element match: {match_result.total_matched}/{match_result.total_expected} required elements found",
        "evaluation_mode": "element",
        # Element-specific fields
        "element_recall": match_result.element_recall,
        "element_precision": match_result.element_precision,
        "severity_accuracy": match_result.severity_accuracy,
        "category_accuracy": match_result.category_accuracy,
        "matched_elements": [m.expected_id for m in match_result.matched_elements],
        "unmatched_elements": match_result.unmatched_expected,
        "extra_finding_count": len(match_result.extra_findings),
        # Cost tracking
        "extraction_cost": extraction.extraction_cost,
        "extraction_time": extraction.extraction_time,
    }
