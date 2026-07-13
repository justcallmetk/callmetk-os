# TOAST AI Standard

TOAST is the explainable decision standard used across CallMeTK OS.

## Decision structure

- **Target:** the objective being pursued.
- **Options:** viable choices considered.
- **Analysis:** evidence, rules, measurements, and constraints.
- **Selection:** the recommended option.
- **Transparency:** confidence, alternatives, estimated cost, limitations, and approval requirements.

## Required review record
Every AI-assisted recommendation should be able to store:

```yaml
target: string
suggestion: string
confidence: 0.0-1.0
reasoning: []
evidence: []
alternatives: []
estimated_cost_usd: 0.0
requires_approval: true
status: pending|accepted|modified|rejected|skipped
user_revision: null
user_reason: null
category: string
model_or_engine: string
created_at: ISO-8601
```

## Confidence thresholds
Default policy:

- **95–100%:** eligible for optional auto-accept only after the category is trusted and auto-accept is enabled.
- **80–94%:** review recommended.
- **60–79%:** manual decision required.
- **Below 60%:** do not present as a confident recommendation; request clarification or offer alternatives.

Auto-accept remains **off by default**.

## Calibration and maturity
AI maturity is based on reviewed decisions:

- **Calibration:** 0–100 reviewed decisions.
- **Learning:** 100–500.
- **Consistent:** 500–1,500.
- **Trusted:** 1,500+.

Maturity is tracked by category. A system may be trusted for objective audio metadata but experimental for album sequencing.

## Agreement metrics
Track:

- suggestions produced
- accepted
- modified
- rejected
- skipped
- agreement rate
- category agreement rate

A modified suggestion is valuable training data and must not be counted as a full agreement.
