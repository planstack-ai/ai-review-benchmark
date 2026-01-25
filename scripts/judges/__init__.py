"""
Judges module for AI Review Benchmark.

Provides multi-judge evaluation capability with ensemble support.
"""

import sys
from pathlib import Path

# Handle imports for both package and direct execution
_parent = str(Path(__file__).parent.parent)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from judges.base import BaseJudge, JudgeResult

# Import judges with graceful handling for missing dependencies
ClaudeJudge = None
GeminiJudge = None
EnsembleJudge = None
EnsembleResult = None

try:
    from judges.claude_judge import ClaudeJudge
except ImportError:
    pass

try:
    from judges.gemini_judge import GeminiJudge
except ImportError:
    pass

try:
    from judges.ensemble import EnsembleJudge, EnsembleResult
except ImportError:
    pass

__all__ = [
    "BaseJudge",
    "JudgeResult",
    "ClaudeJudge",
    "GeminiJudge",
    "EnsembleJudge",
    "EnsembleResult",
]
