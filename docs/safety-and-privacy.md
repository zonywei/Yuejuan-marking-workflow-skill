# Safety And Privacy

This project is for legitimate teacher-side marking workflows. It must not be used to bypass platform access controls or expose student data.

## Never Commit Sensitive Data

Do not commit:

- real student names, IDs, classes, phone numbers, account IDs, or school identifiers
- real answer images or screenshots containing student information
- grading ledgers, event logs, reports, or exports containing student data
- cookies, tokens, session headers, local config files, or `.env` files
- platform request logs that include authentication data

Use fictional or anonymized examples only.

## Authentication Boundaries

- Operate only inside the teacher's authorized task.
- Do not bypass CAPTCHA, sliders, SMS, QR confirmation, human verification, or permission checks.
- Stop when the platform shows task mismatch, ownership conflict, expired session, or unexplained state changes.
- Keep cookies and tokens in local ignored config only, never in `SKILL.md`, examples, docs, or committed scripts.

## Submission Boundaries

- Teacher confirmation is required before submit, recommit, regrade, or provisional scoring actions.
- Provisional scores should only be used when the teacher confirms that correction or recommit is officially allowed.
- Never overwrite another grader's work unless the teacher confirms the workflow permits it.

## AI Scoring Boundaries

- AI scoring must keep a review path.
- Low-confidence, unreadable, blank, off-topic, or ambiguous cases must be routed to review.
- Do not treat AI output as final evidence by itself. Keep the rubric, score reasons, preserved answer evidence, review decisions, and reconciliation records.

