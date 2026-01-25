"""
Extractors module for AI Review Benchmark.

Provides structured extraction of findings from AI review outputs
and element-based matching against expected findings.
"""

from .finding_extractor import (
    ExtractedFinding,
    ExtractionResult,
    FindingExtractor,
)
from .element_matcher import (
    MatchResult,
    ElementMatcher,
    match_findings,
)

__all__ = [
    "ExtractedFinding",
    "ExtractionResult",
    "FindingExtractor",
    "MatchResult",
    "ElementMatcher",
    "match_findings",
]
