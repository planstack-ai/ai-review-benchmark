# Model Comparison Report - 2026-01-25

## Overview

This report compares 5 AI code review models using the improved evaluation metrics:
- Traditional Recall
- Element-Based Recall/Precision
- 2-Stage FP/Noise Metrics

**Test Cases**: 95 cases (75 bug cases + 20 FP cases)

---

## Results Summary

| Model | Recall | E-Recall | E-Precision | Case-FPR | Find-FPR | TP-Noise |
|-------|--------|----------|-------------|----------|----------|----------|
| claude-sonnet | 100% | 85% | 14% | 95% | 7.3 | 85% |
| gemini-3-flash | 100% | 92% | 17% | 95% | 6.1 | 82% |
| deepseek-v3 | 99% | 87% | 16% | 60% | 5.8 | 84% |
| **gpt-4o** | 99% | 88% | **21%** | **50%** | **4.8** | **77%** |
| claude-opus | 100% | **93%** | 11% | 100% | 10.6 | 88% |

---

## Metric Definitions

| Metric | Definition | Target |
|--------|------------|--------|
| **Recall** | Bug cases where any issue detected / Total bug cases | > 80% |
| **E-Recall** | Matched expected elements / Total expected elements | > 80% |
| **E-Precision** | Matched elements / Total findings | > 50% |
| **Case-FPR** | FP cases with critical finding / Total FP cases | < 20% |
| **Find-FPR** | Average findings per FP case | < 2.0 |
| **TP-Noise** | Extra findings in TP cases / Total findings in TP cases | < 30% |

---

## Analysis by Model

### GPT-4o - Best Overall 🏆

**Strengths:**
- Lowest Case-FPR (50%) - Best at avoiding false positives
- Lowest TP-Noise (77%) - Least noisy among all models
- Highest E-Precision (21%) - Most focused findings

**Weaknesses:**
- Recall slightly below 100% (99%)

**Recommendation:** Best choice for production use where balanced performance is needed.

---

### Claude Opus - Most Thorough

**Strengths:**
- Highest E-Recall (93%) - Best at finding expected issues
- 100% Traditional Recall - Never misses bugs

**Weaknesses:**
- Highest Case-FPR (100%) - Flags every FP case as having issues
- Highest Find-FPR (10.6) - Most verbose output
- Highest TP-Noise (88%) - Most extra findings

**Recommendation:** Use when missing bugs is unacceptable and human review will filter noise.

---

### DeepSeek V3 - Cost Effective

**Strengths:**
- Good balance (similar to GPT-4o)
- Moderate Case-FPR (60%)
- **1/20th the cost** of Claude models

**Weaknesses:**
- 99% Recall (missed 1 case)

**Recommendation:** Best for high-volume review with budget constraints.

---

### Gemini 3 Flash - Fast & Balanced

**Strengths:**
- 100% Recall
- High E-Recall (92%)
- Fast response time

**Weaknesses:**
- High Case-FPR (95%)

**Recommendation:** Good for quick reviews where speed matters.

---

### Claude Sonnet - Baseline

**Strengths:**
- 100% Recall
- Moderate E-Recall (85%)

**Weaknesses:**
- High Case-FPR (95%)
- High TP-Noise (85%)

**Recommendation:** Standard choice, but GPT-4o outperforms on precision metrics.

---

## Cost Comparison

| Model | Cost ($/1M input) | Cost per 95 cases (est.) |
|-------|-------------------|--------------------------|
| Claude Opus 4.5 | $5.00 | ~$0.50 |
| Claude Sonnet 4 | $3.00 | ~$0.30 |
| GPT-4o | $2.50 | ~$0.25 |
| GPT-5 | $1.25 | ~$0.12 |
| Gemini 2.5 Pro | $1.25 | ~$0.12 |
| DeepSeek V3 | $0.14 | ~$0.01 |

---

## Key Findings

### 1. All Models Have High Noise
- TP-Noise ranges from 77% (GPT-4o) to 88% (Claude Opus)
- E-Precision is low across all models (11-21%)
- Models find bugs but also report many unnecessary issues

### 2. FPR Varies Significantly
- GPT-4o: 50% (best)
- DeepSeek V3: 60%
- Claude Sonnet/Gemini: 95%
- Claude Opus: 100% (worst)

### 3. DeepSeek V3 Delivers Value
- Performance close to GPT-4o
- Cost is 1/20th
- Good choice for cost-conscious teams

### 4. Claude Opus Trade-off
- Best at finding bugs (93% E-Recall)
- But also most noisy (100% FPR, 88% TP-Noise)
- Use only when completeness > precision

---

## Recommendations

| Use Case | Recommended Model | Reason |
|----------|-------------------|--------|
| Production CI/CD | GPT-4o | Best balance of precision and recall |
| Security-critical | Claude Opus | Highest recall, accept noise |
| High-volume batch | DeepSeek V3 | Cost-effective, good performance |
| Quick feedback | Gemini 3 Flash | Fast, high recall |
| Baseline comparison | Claude Sonnet | Standard benchmark |

---

## Methodology

### Evaluation Pipeline
1. **Traditional Evaluation**: Severity-based detection (critical/major/minor)
2. **Element-Based Evaluation**: Match findings against `must_find` keywords
3. **FP Metrics**: 2-stage analysis (case-level + finding-level)

### Data Sources
- Run directories: `results/20260125_*_run/`
- Test cases: `cases/rails/` (95 cases)
- Expected elements: `meta.json` with `must_find` field

### Tools Used
- `scripts/evaluator.py` - Main evaluation
- `scripts/extractors/` - Structured finding extraction
- `scripts/metrics/` - FP/Noise metrics calculation

---

## Raw Data Location

```
results/20260125_164053_run/claude-sonnet.json
results/20260125_174036_run/gemini-3-flash.json
results/20260125_182635_run/deepseek-v3.json
results/20260125_183800_run/gpt-4o.json
results/20260125_194709_run/claude-opus.json
```

---

*Generated: 2026-01-25*
*Evaluation System: v2.0 (with Element-Based Evaluation)*
