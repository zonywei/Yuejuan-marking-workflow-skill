# Physics Subjective Question Demo

This demo shows the complete input-output path of the skill using a fictional high-school physics problem. No real student data is used.

## What You Can See In 5 Minutes

| Step | File | What to look for |
| --- | --- | --- |
| 1 | [`question.md`](question.md) | The original subjective physics question and score allocation |
| 2 | [`answer-key.md`](answer-key.md) | Teacher-side reference answer and calculation path |
| 3 | [`generated-rubric.md`](generated-rubric.md) | Score atoms, equivalent answers, zero-score rules, carried-error handling |
| 4 | [`model-grading-prompt.md`](model-grading-prompt.md) | A JSON-output prompt with review flags and low-confidence routing |
| 5 | [`sample-student-answers.md`](sample-student-answers.md) | Three fictional answers: high-score, partial-score, near-blank |
| 6 | [`sample-grading-output.json`](sample-grading-output.json) | Structured draft scores for the three answers |
| 7 | [`review-queue.md`](review-queue.md) | Cases that should be checked by the teacher |
| 8 | [`teacher-report.md`](teacher-report.md) | The final teaching feedback report |

## Score Summary

| Paper ID | Type | Draft Score | Review |
| --- | --- | ---: | --- |
| `paper-phy-001` | High-score answer | 12 / 12 | No review required in this demo |
| `paper-phy-002` | Partial-score answer | 6 / 12 | Optional spot check for carried-forward error |
| `paper-phy-003` | Near-blank / low-confidence answer | 0 / 12 | Teacher review required |

## What This Demo Proves

- The workflow starts from teacher materials, not from a vague "grade this" request.
- The rubric explains what earns points and what does not.
- The model prompt asks for structured JSON, reasons, confidence, and review flags.
- Low-confidence cases are separated before final handling.
- The teacher report turns grading evidence into teaching feedback.

## What This Demo Does Not Claim

- It does not submit anything to a real platform.
- It does not use real answer images or real student records.
- It does not prove that AI can grade without teacher review.
- It does not replace platform-specific safety checks or teacher confirmation.

## Try It With An Agent

Use these files as input and ask:

```text
Use $zhixue-marking-workflow with this demo folder.
Check whether the rubric, model prompt, sample grading output, review queue, and teacher report are consistent.
Do not submit anything. Treat all answers as fictional examples.
```

