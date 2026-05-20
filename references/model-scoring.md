# Model Scoring

## Core Position

The highest-value form of this workflow is not only transport automation. It is:

- fetch the paper image
- ask the model to score it against an explicit rubric
- submit the model score automatically when confidence is high
- reserve human review only for gray cases or audit sampling

## Recommended Scoring Pattern

Input to the model:

- the exact problem statement
- the official answer
- the scoring rubric
- the student paper image

Required output:

- per-subquestion score
- total score
- short reason for each subquestion
- confidence
- whether the paper should be reviewed manually

Recommended structured output:

```json
{
  "partScores": {
    "1": 3,
    "2": 2
  },
  "totalScore": 5,
  "reasons": {
    "1": "Identified the main cause and supported it with relevant evidence.",
    "2": "Explained the consequence but missed one required detail."
  },
  "confidence": 0.88,
  "needsReview": false
}
```

## Routing Rules

- confirmed blank zone: auto `0`
- high-confidence model result: auto submit
- medium-confidence result: optional audit sampling
- low-confidence or unreadable image: manual review

## Calibration

Model scoring should be calibrated on teacher-corrected papers from the same school and rubric style.

Use a seed set to tune:

- prompt wording
- confidence threshold
- blank threshold
- gray-zone boundary

## Why This Matters

If the model is not allowed to score, the workflow only saves clicking time.

If the model scores reliably, the workflow scales to:

- large subjective-question batches
- stable rubric enforcement
- fast feedback loops
- post-exam analytics with structured score reasons
