# Grading Strategy

Use this reference when the user asks how to think through a grading run, not only how to automate a platform.

## Strategic Goal

The goal is consistent, auditable scoring with useful teaching feedback. Speed matters only after the scoring standard, evidence capture, and recovery path are stable.

## Run Phases

### 1. Scope The Task

- Identify the exact question, subquestion boundaries, score ceiling, and platform task.
- Confirm whether the task is single-marking, double-marking, arbitration, or review.
- Collect the problem, official answer, teacher rules, and any known edge cases.
- Decide whether final submission, provisional occupation, or offline scoring is allowed.

### 2. Build The Scoring Standard

- Turn the rubric into score atoms.
- Define full-credit, partial-credit, zero-credit, and review-required cases.
- List acceptable equivalent answers and common wrong paths.
- Specify score step: integer, half-point, band score, or rubric-specific scale.

### 3. Calibrate Before Scale

- Score a small sample before batch submission.
- Include blank, sparse, typical partial, high-score, full-score, and unclear papers.
- Compare model output against the teacher standard.
- Tighten prompts, score bounds, review flags, and confidence thresholds before scaling.

### 4. Batch With Checkpoints

- Cache evidence first, then score from the cache.
- Keep one authoritative ledger and write to it after each bounded batch.
- Use short reasons and reusable error tags so later reports are evidence-backed.
- Avoid very large model batches if image labels or answer regions become ambiguous.

### 5. Audit Continuously

- Sample high-confidence auto scores.
- Review all low-confidence, unreadable, boundary, and suspicious zero papers.
- When a new grading rule appears, re-check the affected tag group.
- Track whether errors are scoring-standard problems, image-quality problems, prompt-output problems, or platform-submit problems.

### 6. Close Out Rigorously

- Reconcile local ledger count, unique paper ids, submit/recommit events, and platform review status.
- Resolve or explicitly document every mismatch.
- Generate reports from saved evidence, not from memory.
- Preserve run artifacts that support future rechecks.

## Operating Heuristics

- Rubric first, model second, platform third.
- Cache before submit.
- Structured output before automation.
- Review flags are part of throughput, not failure.
- Do not change a scoring rule silently mid-run.
- Do not call a batch complete until ledger, submit events, and platform state agree.
- Keep reusable lessons in the skill; keep question-specific facts in the run directory.

## Common Failure Modes

- Starting batch submission before the rubric is stable.
- Treating answer density or OCR as score evidence.
- Letting prompt drift between batches.
- Losing the mapping between image, paper id, score, and submit event.
- Trusting platform pagination without verifying it.
- Reporting statistics from chat notes instead of the ledger.
- Updating future scores after a new rule but forgetting to re-audit already scored papers.
