# Speed And Accuracy Controls

## Why Accuracy Drops

In this workflow, accuracy usually drops because of one of these:

- weak or incomplete rubric
- unreadable or low-quality scan
- prompt drift between batches
- malformed model output
- missing score-bound validation
- blank threshold set from too few samples

## Required Controls

### 1. Rubric Versioning

Each question should have:

- rubric version
- prompt version
- calibration note

Do not silently reuse old prompts after rubric changes.

### 2. Score Validation

Before submission, validate:

- each part score is within range
- total equals sum of parts
- score schema matches the current question

### 3. Confidence Routing

Recommended routing:

- blank zone: auto `0`
- high confidence: auto submit
- medium confidence: sample audit
- low confidence: manual review

### 4. Audit Sampling

Do not rely on confidence alone.

Auto-submitted papers should still be sampled periodically to detect:

- drift
- new error patterns
- rubric mismatch

### 5. Image Quality Controls

Before model scoring, consider:

- crop
- rotation correction
- contrast boost
- denoise

### 6. Full Logging

Log:

- paper identifier
- model output
- submitted score
- confidence
- threshold values
- whether the paper was auto-submitted or reviewed

Without logs, the workflow is fast but hard to trust.

