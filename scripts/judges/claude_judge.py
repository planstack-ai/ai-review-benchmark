"""
Claude Judge implementation.

Uses Anthropic's Claude models for semantic evaluation.
"""

import os
import sys
import time
from pathlib import Path
from typing import Any

import anthropic

# Handle imports for both package and direct execution
try:
    from .base import BaseJudge, JudgeResult
    from ..config import JudgeConfig, get_judge_config
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from judges.base import BaseJudge, JudgeResult
    from config import JudgeConfig, get_judge_config


class ClaudeJudge(BaseJudge):
    """Judge implementation using Claude (Anthropic) models."""

    def __init__(self, config: JudgeConfig | None = None):
        """Initialize Claude judge.

        Args:
            config: Optional JudgeConfig. If None, uses default claude config.
        """
        if config is None:
            config = get_judge_config("claude")
        super().__init__(config)

        # Initialize Anthropic client
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)

    def evaluate_semantic(
        self,
        review_result: dict[str, Any],
        expected_critique: str,
        expected_detection: bool,
    ) -> JudgeResult:
        """Perform semantic evaluation using Claude.

        Args:
            review_result: AI reviewer's output (parsed and raw)
            expected_critique: Human-written expected critique (ground truth)
            expected_detection: True for bug cases, False for FP cases

        Returns:
            JudgeResult with evaluation details
        """
        prompt = self._build_prompt(review_result, expected_critique, expected_detection)

        start_time = time.time()
        message = self.client.messages.create(
            model=self.config.model_id,
            max_tokens=self.config.max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        elapsed_time = time.time() - start_time

        response_text = message.content[0].text
        cost = self.calculate_cost(
            message.usage.input_tokens,
            message.usage.output_tokens,
        )

        return self._parse_response(
            response_text,
            expected_detection,
            cost,
            elapsed_time,
        )

    @classmethod
    def from_default(cls) -> "ClaudeJudge":
        """Create a ClaudeJudge with default configuration.

        Returns:
            ClaudeJudge instance with default settings
        """
        return cls(get_judge_config("claude"))
