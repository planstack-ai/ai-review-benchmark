"""
Gemini Judge implementation.

Uses Google's Gemini models for semantic evaluation.
"""

import os
import sys
import time
from pathlib import Path
from typing import Any

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Handle imports for both package and direct execution
try:
    from .base import BaseJudge, JudgeResult
    from ..config import JudgeConfig, get_judge_config
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from judges.base import BaseJudge, JudgeResult
    from config import JudgeConfig, get_judge_config


class GeminiJudge(BaseJudge):
    """Judge implementation using Gemini (Google) models."""

    def __init__(self, config: JudgeConfig | None = None):
        """Initialize Gemini judge.

        Args:
            config: Optional JudgeConfig. If None, uses default gemini config.

        Raises:
            ImportError: If google-generativeai package is not installed
            ValueError: If GOOGLE_API_KEY is not set
        """
        if not GENAI_AVAILABLE:
            raise ImportError(
                "google-generativeai package required for Gemini judge. "
                "Install with: pip install google-generativeai"
            )

        if config is None:
            config = get_judge_config("gemini")
        super().__init__(config)

        # Initialize Gemini client
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=self.config.model_id,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            ),
        )

    def evaluate_semantic(
        self,
        review_result: dict[str, Any],
        expected_critique: str,
        expected_detection: bool,
    ) -> JudgeResult:
        """Perform semantic evaluation using Gemini.

        Args:
            review_result: AI reviewer's output (parsed and raw)
            expected_critique: Human-written expected critique (ground truth)
            expected_detection: True for bug cases, False for FP cases

        Returns:
            JudgeResult with evaluation details
        """
        prompt = self._build_prompt(review_result, expected_critique, expected_detection)

        start_time = time.time()
        response = self.model.generate_content(prompt)
        elapsed_time = time.time() - start_time

        response_text = response.text

        # Extract token counts from usage metadata
        input_tokens = 0
        output_tokens = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
            output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)

        cost = self.calculate_cost(input_tokens, output_tokens)

        return self._parse_response(
            response_text,
            expected_detection,
            cost,
            elapsed_time,
        )

    @classmethod
    def from_default(cls) -> "GeminiJudge":
        """Create a GeminiJudge with default configuration.

        Returns:
            GeminiJudge instance with default settings
        """
        return cls(get_judge_config("gemini"))
