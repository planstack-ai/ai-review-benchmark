"""
Structured Finding Extractor.

Extracts structured findings from AI review outputs using LLM-based parsing.
Converts free-text or semi-structured review output into standardized ExtractedFinding objects.
"""

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

# Handle imports
try:
    from ..config import JudgeConfig, get_judge_config
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import JudgeConfig, get_judge_config


# Valid categories for findings (allowlist to prevent hallucination)
VALID_CATEGORIES = {
    "calculation_error",
    "logic_error",
    "security",
    "performance",
    "data_integrity",
    "race_condition",
    "null_handling",
    "boundary_condition",
    "state_management",
    "authorization",
    "validation",
    "external_api",
    "transaction",
    "concurrency",
    "memory_leak",
    "resource_leak",
    "type_error",
    "encoding",
    "time_handling",
    "notification",
    "other",
}

# Valid severities
VALID_SEVERITIES = {"critical", "major", "minor", "info"}


@dataclass
class ExtractedFinding:
    """A structured finding extracted from an AI review."""

    category: str  # calculation_error, security, performance, etc.
    evidence: str  # Code snippet or quote from review
    impact: str  # Description of the impact
    severity: str  # critical, major, minor, info
    fix_proposal: str  # Suggested fix
    confidence: float = 1.0  # Extraction confidence (0.0-1.0)
    raw_text: str = ""  # Original text this was extracted from

    def __post_init__(self):
        """Validate and normalize fields."""
        # Normalize category
        self.category = self.category.lower().replace(" ", "_").replace("-", "_")
        if self.category not in VALID_CATEGORIES:
            self.category = "other"

        # Normalize severity
        self.severity = self.severity.lower()
        if self.severity in ("high",):
            self.severity = "major"
        elif self.severity in ("low",):
            self.severity = "minor"
        if self.severity not in VALID_SEVERITIES:
            self.severity = "minor"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def matches_keywords(self, keywords: list[str]) -> bool:
        """Check if finding matches any of the given keywords.

        Args:
            keywords: List of keywords to match against

        Returns:
            True if any keyword is found in evidence, impact, or fix_proposal
        """
        search_text = f"{self.evidence} {self.impact} {self.fix_proposal}".lower()
        return any(kw.lower() in search_text for kw in keywords)


@dataclass
class ExtractionResult:
    """Result of extracting findings from a review."""

    findings: list[ExtractedFinding] = field(default_factory=list)
    extraction_cost: float = 0.0
    extraction_time: float = 0.0
    raw_response: str = ""
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "findings": [f.to_dict() for f in self.findings],
            "extraction_cost": self.extraction_cost,
            "extraction_time": self.extraction_time,
            "success": self.success,
            "error": self.error,
        }

    @property
    def finding_count(self) -> int:
        """Number of findings extracted."""
        return len(self.findings)

    def by_severity(self, severity: str) -> list[ExtractedFinding]:
        """Get findings filtered by severity."""
        return [f for f in self.findings if f.severity == severity]

    def by_category(self, category: str) -> list[ExtractedFinding]:
        """Get findings filtered by category."""
        return [f for f in self.findings if f.category == category]


# Extraction prompt template
EXTRACTION_PROMPT_TEMPLATE = """You are an expert at analyzing code review outputs.

## Task
Extract structured findings from the following AI code review output.
For each distinct issue mentioned, extract the structured information.

## AI Review Output
```json
{review_output}
```

## Original Code Being Reviewed (for context)
```
{code_snippet}
```

## Instructions
1. Identify each distinct issue/finding mentioned in the review
2. For each finding, extract:
   - **category**: One of: calculation_error, logic_error, security, performance, data_integrity, race_condition, null_handling, boundary_condition, state_management, authorization, validation, external_api, transaction, concurrency, time_handling, notification, other
   - **evidence**: The specific code or behavior that indicates the issue
   - **impact**: What could go wrong because of this issue
   - **severity**: critical (data loss/security breach), major (incorrect behavior), minor (code quality), info (suggestion)
   - **fix_proposal**: How to fix the issue

3. If the review says "LGTM" or "no issues", return an empty findings array
4. Do NOT invent issues not mentioned in the review
5. Each distinct problem should be a separate finding

## Output Format
Respond with ONLY valid JSON:
```json
{{
  "findings": [
    {{
      "category": "category_name",
      "evidence": "specific code or behavior",
      "impact": "what could go wrong",
      "severity": "critical|major|minor|info",
      "fix_proposal": "how to fix"
    }}
  ]
}}
```
"""


def extract_json(text: str) -> dict[str, Any] | None:
    """Extract JSON from response text."""
    # ```json ... ``` blocks
    json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # ``` ... ``` blocks
    code_match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if code_match:
        try:
            return json.loads(code_match.group(1))
        except json.JSONDecodeError:
            pass

    # Direct JSON parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Brace-based extraction
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def extract_from_parsed_response(parsed_response: dict[str, Any]) -> list[ExtractedFinding]:
    """Extract findings directly from already-parsed AI review response.

    This is a lightweight extraction that doesn't require an LLM call.
    It converts the structured issues[] array into ExtractedFinding objects.

    Args:
        parsed_response: Parsed JSON response from AI reviewer

    Returns:
        List of ExtractedFinding objects
    """
    findings = []

    if not parsed_response:
        return findings

    issues = parsed_response.get("issues", [])
    for issue in issues:
        # Map issue type to category
        issue_type = issue.get("type", "other").lower()
        category_map = {
            "plan_mismatch": "logic_error",
            "logic_bug": "logic_error",
            "security": "security",
            "performance": "performance",
            "data_integrity": "data_integrity",
            "validation": "validation",
            "error_handling": "null_handling",
        }
        category = category_map.get(issue_type, "other")

        finding = ExtractedFinding(
            category=category,
            evidence=issue.get("location", ""),
            impact=issue.get("description", ""),
            severity=issue.get("severity", "minor"),
            fix_proposal=issue.get("suggestion", ""),
            confidence=0.9,  # High confidence since it's from structured output
            raw_text=json.dumps(issue, ensure_ascii=False),
        )
        findings.append(finding)

    return findings


class FindingExtractor:
    """Extracts structured findings from AI review outputs using LLM."""

    def __init__(self, model_config: JudgeConfig | None = None):
        """Initialize the extractor.

        Args:
            model_config: Configuration for the extraction model.
                         If None, uses default Claude config.
        """
        if model_config is None:
            model_config = get_judge_config("claude")
        self.config = model_config
        self._client = None

    def _get_client(self):
        """Lazily initialize the API client."""
        if self._client is not None:
            return self._client

        if self.config.provider == "anthropic":
            import anthropic
            self._client = anthropic.Anthropic()
        elif self.config.provider == "google":
            import google.generativeai as genai
            import os
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
            self._client = genai.GenerativeModel(self.config.model_id)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

        return self._client

    def extract(
        self,
        review_result: dict[str, Any],
        code_snippet: str = "",
        use_llm: bool = True,
    ) -> ExtractionResult:
        """Extract structured findings from a review result.

        Args:
            review_result: The AI review result containing parsed_response and/or raw_response
            code_snippet: Optional code snippet for context
            use_llm: If True, uses LLM for extraction. If False, uses direct parsing.

        Returns:
            ExtractionResult with extracted findings
        """
        import time

        # Try direct extraction from parsed response first
        parsed_response = review_result.get("parsed_response")
        if parsed_response and not use_llm:
            findings = extract_from_parsed_response(parsed_response)
            return ExtractionResult(
                findings=findings,
                extraction_cost=0.0,
                extraction_time=0.0,
                success=True,
            )

        # Use LLM for more sophisticated extraction
        if not use_llm:
            return ExtractionResult(
                findings=extract_from_parsed_response(parsed_response) if parsed_response else [],
                success=True,
            )

        # Prepare review output for LLM
        if parsed_response:
            review_output = json.dumps(parsed_response, indent=2, ensure_ascii=False)
        else:
            review_output = review_result.get("raw_response", "")

        if not review_output:
            return ExtractionResult(
                findings=[],
                success=True,
            )

        # Build prompt
        prompt = EXTRACTION_PROMPT_TEMPLATE.format(
            review_output=review_output,
            code_snippet=code_snippet[:2000] if code_snippet else "Not provided",
        )

        # Call LLM
        start_time = time.time()
        try:
            if self.config.provider == "anthropic":
                client = self._get_client()
                message = client.messages.create(
                    model=self.config.model_id,
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt}],
                )
                response_text = message.content[0].text
                cost = (
                    message.usage.input_tokens * self.config.input_cost_per_1m / 1_000_000
                    + message.usage.output_tokens * self.config.output_cost_per_1m / 1_000_000
                )
            elif self.config.provider == "google":
                client = self._get_client()
                response = client.generate_content(prompt)
                response_text = response.text
                # Estimate cost for Gemini
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) if hasattr(response, "usage_metadata") else 0
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) if hasattr(response, "usage_metadata") else 0
                cost = (
                    input_tokens * self.config.input_cost_per_1m / 1_000_000
                    + output_tokens * self.config.output_cost_per_1m / 1_000_000
                )
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")

            elapsed_time = time.time() - start_time

        except Exception as e:
            return ExtractionResult(
                findings=[],
                success=False,
                error=str(e),
            )

        # Parse response
        parsed = extract_json(response_text)
        if not parsed:
            # Fallback to direct parsing
            findings = extract_from_parsed_response(parsed_response) if parsed_response else []
            return ExtractionResult(
                findings=findings,
                extraction_cost=cost,
                extraction_time=elapsed_time,
                raw_response=response_text,
                success=True,
                error="LLM response parsing failed, used fallback",
            )

        # Convert to ExtractedFinding objects
        findings = []
        for f in parsed.get("findings", []):
            try:
                finding = ExtractedFinding(
                    category=f.get("category", "other"),
                    evidence=f.get("evidence", ""),
                    impact=f.get("impact", ""),
                    severity=f.get("severity", "minor"),
                    fix_proposal=f.get("fix_proposal", ""),
                    confidence=1.0,
                    raw_text=json.dumps(f, ensure_ascii=False),
                )
                findings.append(finding)
            except Exception:
                continue

        return ExtractionResult(
            findings=findings,
            extraction_cost=cost,
            extraction_time=elapsed_time,
            raw_response=response_text,
            success=True,
        )

    def extract_batch(
        self,
        review_results: list[dict[str, Any]],
        code_snippets: list[str] | None = None,
        use_llm: bool = False,
    ) -> list[ExtractionResult]:
        """Extract findings from multiple review results.

        Args:
            review_results: List of AI review results
            code_snippets: Optional list of code snippets (same length as review_results)
            use_llm: If True, uses LLM for extraction

        Returns:
            List of ExtractionResult objects
        """
        if code_snippets is None:
            code_snippets = [""] * len(review_results)

        results = []
        for review, code in zip(review_results, code_snippets):
            result = self.extract(review, code, use_llm=use_llm)
            results.append(result)

        return results
