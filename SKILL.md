---
name: zhixue-marking-workflow
description: Use when the user is doing Zhixue/智学网 teacher-side subjective-question grading, web阅卷/改卷 on an authenticated grading platform, or tasks involving rubric-based marking, batch paper/image scoring, blank-paper handling, score 提交/重提, ledger recovery, reconciliation, or teacher reports.
---

# Zhixue Marking Workflow

## Core Principle

Use this skill to run or refine an authorized Zhixue subjective-question grading workflow, or to adapt the same pattern to another authenticated web grading platform. Keep the grading rubric as the scoring authority, keep the teacher's authenticated session as the access boundary, and keep local ledgers as the recovery and reporting source.

This skill is for legitimate teacher-side grading. Do not use it to bypass login, defeat human verification, scrape unrelated student data, invent unsupported endpoints, or overwrite another grader's work without explicit permission.

## Standard Flow

1. Confirm the user has an active teacher-side Zhixue grading task and approval for automation.
2. Capture the task scope: problem, answer key, total score, subquestion score split, grading rules, and whether recommit is permitted.
3. If the rubric is incomplete, generate a prompt pack with `scripts/build_prompt_pack.py`, then wait for user review before real grading.
4. Confirm the authenticated channel: browser session, cookie/referer, API session, or approved manual export.
5. Cache each paper image and metadata before scoring. Store the run outside the skill folder, such as `./zhixue_work/<task-name>/`.
6. Score from the current rubric with structured output: paper id, per-part scores, total score, brief reason, confidence, and review flag.
7. Validate scores before any submit or recommit: bounds, total sum, allowed score step, and required fields.
8. Submit only high-confidence validated results. Route unclear handwriting, rubric ambiguity, low confidence, and suspected conflicts to review.
9. Reconcile the local ledger, submission events, and platform review list before claiming completion.
10. Generate reports only from saved ledger rows, event logs, and preserved evidence.

## Overall Grading Strategy

Treat grading as a controlled production workflow, not as isolated paper-by-paper judgment.

1. `Define`: lock the question scope, score ceiling, rubric, score atoms, zero-credit rules, and allowed equivalent answers.
2. `Calibrate`: score a small diverse sample first, including blank, low, partial, high, and borderline papers.
3. `Stabilize`: convert calibration findings into prompt rules, validation checks, review flags, and error tags.
4. `Batch`: process papers in bounded batches with local cache, structured output, and checkpointed ledger rows.
5. `Audit`: sample high-confidence auto scores, review low-confidence cases, and re-check any tag affected by a new rule.
6. `Reconcile`: compare ledger, submit events, and platform state before claiming completion.
7. `Report`: summarize score distribution, common errors, strong responses, typical examples, and teaching suggestions from saved evidence.
8. `Generalize`: after close-out, separate reusable scoring/workflow rules from current-question-only rubric details.

The agent should constantly ask: "What evidence supports this score, what would make this case unsafe to auto-submit, and how will this decision be audited later?"

## Cross-Platform Adapter Pattern

Treat every grading site as a platform adapter around the same core loop:

1. task identity: exam, question, rubric, score ceiling, reviewer role
2. queue discovery: current-paper endpoint, preloaded list, review list, or export file
3. paper identity: stable paper id, student/user code, item id, image id, attempt id
4. evidence fetch: image URL, crop regions, answer text, attachments, pagination
5. scoring action: submit endpoint, browser form, batch import, or official review UI
6. correction path: recommit, review-list edit, official regrade, or manual exception
7. reconciliation source: platform count, review list, submitted status, audit export

Keep platform-specific selectors, endpoints, headers, payload fields, and pagination rules in a local adapter script or run notes. Keep scoring, ledger, confidence routing, reporting, and subject rules platform-independent.

## Authenticated Interface Exploration

When adapting to a new grading platform, start from the logged-in manual workflow and map the minimum stable loop.

1. Observe one manual grading cycle: open paper, inspect answer, enter score, submit, load next paper.
2. Inspect network traffic only inside the user's authorized session and current grading task.
3. Identify request families: task metadata, paper fetch, image fetch, score submit, review list, regrade/recommit, heartbeat/session checks.
4. Reproduce read-only calls first. Redact cookies, tokens, and student data from logs.
5. Cache one paper and compare the cached image/metadata with the browser UI.
6. Smoke-test a harmless status/read path before any submit path.
7. If submission automation is needed, test with one explicit user-approved paper and immediately reconcile platform state.
8. Document adapter assumptions: auth source, task ids, item ids, score format, retry behavior, pagination, and failure signals.

Do not continue automation if the platform shows human verification, task mismatch, ownership conflict, or unexplained state changes.

## Batch Grading Exploration

Look for the safest throughput path before grading at scale.

- `single-current queue`: fetch current paper, score, submit, then fetch next.
- `preloaded list`: cache all visible/preloaded papers, then score in batches.
- `occupy then recommit`: submit a provisional score only when approved and later correction is officially possible.
- `official export/import`: prefer it when the platform supports bulk download or upload with auditability.
- `browser-only workflow`: use it when backend calls are unstable or too risky.

For any batch mode:

1. Build a local queue before scoring: identifier, image path, task id, current action state.
2. Sort by answer density or confidence only for routing; do not let density decide scores.
3. Use contact sheets or cropped batches when they remain readable.
4. Score in bounded batches, checkpoint after each batch, and keep a review queue.
5. Run periodic audit sampling on auto-submitted scores.
6. Reconcile after every submit/recommit batch, not only at the end.

## Required Boundaries

- Operate only inside the current authenticated teacher task.
- Never store live cookies or tokens in `SKILL.md`, reference files, examples, or committed configs.
- Treat browser/API parameters as task-local secrets. Put them in a local config file ignored by version control.
- Stop automation at CAPTCHA, slider, SMS, QR, or other human-verification checkpoints and ask the user to complete them.
- Do not submit provisional scores unless the user confirms that later correction or recommit is allowed.
- Do not overwrite another grader's score unless the user confirms the workflow permits it.
- Prefer review over auto-submit when task identity, ownership, score rules, or image readability is uncertain.

## Bundled Scripts

The skill includes two reusable helpers:

- `scripts/build_prompt_pack.py`: creates rubric-generation and grading-prompt drafts from source materials.
- `scripts/zhixue_mark.py`: a Zhixue-specific adapter for authenticated fetch/cache/submit/recommit operations.

### Prompt Pack

Create a JSON input from the current problem, answer key, and score allocation. Start from `scripts/prompt_pack.example.json`.

```powershell
py -3 .\scripts\build_prompt_pack.py .\scripts\prompt_pack.example.json .\prompt-pack-out
```

Review the generated files with the user before grading:

- `rubric-generation-prompt.md`
- `original-question-prompt.md`
- `standard-model-grading-prompt.md`
- `review-required.md`

Do not use a generated grading prompt until the user approves the rubric details and edge-case scoring rules.

### Zhixue Marking Helper

Create a local config from `scripts/zhixue_mark.config.example.json`.

Configuration can be supplied by:

- `ZHIXUE_MARK_CONFIG`
- `scripts/zhixue_mark.config.json`

Required keys:

- `markingPaperId`
- `topicNumStr`
- `referer`
- `cookie`

Recommended keys:

- `outDir`
- calibrated blank thresholds for the current scan style

Core commands:

```powershell
py -3 .\scripts\zhixue_mark.py calibrate-blanks .\confirmed-blank-papers
py -3 .\scripts\zhixue_mark.py current
py -3 .\scripts\zhixue_mark.py commit SCORE
py -3 .\scripts\zhixue_mark.py recommit-user USER_CODE SCORE
py -3 .\scripts\zhixue_mark.py recommit ITEM_ID SCORE USER_CODE
py -3 .\scripts\zhixue_mark.py batch-zero COUNT
py -3 .\scripts\zhixue_mark.py status
py -3 .\scripts\zhixue_mark.py grade SCORE
py -3 .\scripts\zhixue_mark.py skip-blanks
```

Use `batch-zero` only as an occupy/cache strategy when the current task permits later recommit and the user has approved that approach.

## Scoring Rules

The current question rubric always overrides defaults.

Use these general rules when the rubric is incomplete:

- Award only points supported by visible, relevant student work.
- Accept equivalent reasoning or expression when it satisfies the same scoring atom.
- Preserve independent partial credit when one subquestion or step is correct and separable.
- Do not let unrelated errors erase already earned independent points unless the rubric says the later score depends on the earlier result.
- Do not award credit for dense but irrelevant writing.
- Treat blank, unrelated, or wholly incorrect responses as `0`.
- Route unreadable, ambiguous, crossed-out, or near-boundary work to review.
- Use OCR, dark ratio, answer density, and contact-sheet sorting only as routing aids. Final scores must come from the rubric and visual evidence.

Use scoring-rule layers in this order:

1. latest explicit user instruction
2. current question rubric and official answer
3. teacher-corrected calibration samples
4. subject-specific default rules
5. platform-independent general rules

If a subject-specific rule emerges during a run, keep it in the run ledger or rubric file unless it clearly generalizes across future grading tasks. Read `references/subject-scoring-defaults.md` when the task needs subject defaults.

## During-Run Improvement Loop

Treat a grading run as a live calibration process.

1. Tag recurring errors while grading, not only in the final report.
2. Record per-paper scoring reasons compactly enough to audit later.
3. After each batch, summarize new scoring patterns, ambiguous cases, and rubric gaps.
4. If a new rule affects already scored papers, re-audit the affected tag group before final submission or report.
5. Keep question-specific rules in the run rubric. Move only reusable platform or subject rules into the skill.
6. At close-out, produce a short generalization note: reusable rules, task-only rules, unresolved edge cases, and report highlights.

## Confidence Routing

Use confidence to reduce manual work, not to replace validation.

- Confirmed blank zone: eligible for `0` only after calibration or direct visual confirmation.
- High confidence: eligible for submit after score validation.
- Medium confidence: sample audit or second-pass review.
- Low confidence, unreadable image, rubric conflict, or task mismatch: manual review.

Calibrate thresholds from the current task's confirmed samples. Avoid freezing fallback numeric thresholds into future tasks.

## Ledger And Evidence

Maintain one authoritative run ledger. It should include:

- stable paper identifier, such as `userCode` or platform item id
- roster identity when available: admission ticket number or `userNum`, class name, and student name from an authorized local roster export
- image path and crop/contact-sheet path when used
- per-part scores and total score
- concise scoring reason
- one-sentence student-facing or teacher-facing feedback when requested
- confidence and review flag
- action state: cached, scored, submitted, recommitted, reviewed, or blocked

Append an event log for every submit or recommit attempt, including timestamp, score, result, retry count, and fallback path. Before a pause or report, verify row counts, unique identifiers, and unresolved review cases.

Do not rely on chat history as the source of truth for completion or reports.

## Student Roster And Feedback

Use a student roster only when the user provides an authorized export or confirms the current authenticated Zhixue report page permits access. Keep real student names and admission-ticket data in the local run directory or user-provided workbook, not in `SKILL.md`, examples, or committed files.

Recommended roster source:

- local workbook or CSV with `准考证号`, `班级`, and `姓名`, such as a user-provided `学生信息.xlsx`
- platform read-only report export from the current authenticated teacher account

Before using a roster, verify:

1. Required columns are present: admission ticket number or `userNum`, class, and name.
2. No required fields are blank.
3. The roster has no duplicate admission ticket numbers.
4. Roster count and class counts reconcile with the platform or the user's stated task scope.

Join scoring rows to the roster by `userCode`, `userNum`, or `准考证号`. If a row cannot be matched, keep the stable paper id, set a `rosterMissing` or `needsRosterReview` flag, and do not invent class or name.

When per-student feedback is requested, add these fields to the ledger:

- `admissionTicketNo`
- `className`
- `studentName`
- `totalScore`
- per-part scores when available
- `oneSentenceFeedback`

The one-sentence feedback must be grounded in the visible answer and current rubric. It should name the main earned point or main fix, avoid unsupported personality judgments, and stay short enough to fit a spreadsheet cell. Do not let roster identity influence the score; names and classes are for matching, reporting, and targeted feedback only.

## Blank Screening

Blank screening is a safety-sensitive optimization.

1. Calibrate with multiple confirmed blank papers from the current scan style.
2. Keep a review zone above the auto-blank threshold.
3. Review any paper with plausible relevant marks, formulas, diagrams, variables, or answer attempts.
4. Record the threshold and routing decision in the ledger.

If no calibration set exists, use direct visual review or a conservative fallback and document the uncertainty.

## Session Recovery

Treat these as session-expiry or task-identity signals:

- HTTP `401` or `403`
- redirect to a login page
- HTML where JSON is expected
- JSON decode failure
- repeated missing or unusable current-paper payloads
- explicit login-expired messages

On expiry, stop new submissions, checkpoint the ledger and event log, report the last successful item, and ask the user to refresh the authenticated session. Resume from the authoritative local queue after a smoke test.

## Reconciliation And Completion

Before claiming a batch is complete, compare:

1. Local ledger: row count, unique identifiers, final scores, review flags.
2. Event log: successful submit/recommit records and failures.
3. Zhixue review list or platform state: total count, pagination behavior, and score status.

Completion requires:

- no remaining ungraded queue items
- no unresolved submit/recommit failures
- no unexplained ledger/platform mismatch
- requested report artifacts generated from saved evidence

If the platform review list appears inconsistent, rebuild the comparison from ledger and event records before changing scores or declaring unresolved cases.

## Teacher-Facing Reports

Reports are for teachers, not for debugging the automation. Use teacher language in the main body and keep raw IDs, API details, and retry traces in appendices or separate files.

Default report structure:

1. `阅卷概况`: paper count, completion status, scoring source, reconciliation result.
2. `题目特点与难点`: task-specific difficulty tied to the current question.
3. `整体答题情况`: average, median, score bands, full-score and zero-score counts, per-part averages when available.
4. `0分卷分析`: separate blank/no-valid-answer papers from written but invalid answers.
5. `有分卷的共性错误`: common nonzero-paper errors in teacher-readable categories.
6. `高分卷的共同特点`: patterns in strong responses.
7. `教学建议与阅卷建议`: actionable teaching feedback and scoring cautions.
8. `典型卷例`: readable representative images with score captions and concise reasons.

Use large readable images for typical examples. Do not shrink handwriting evidence into unreadable thumbnails.

For `.docx` reports, render-check representative pages. For LaTeX/PDF reports, compile with a real LaTeX engine when feasible and state any blocker if compilation cannot be completed.

## References

Read these only when the current task needs the detail:

- `references/model-scoring.md`: model scoring shape, confidence, and calibration.
- `references/prompt-generation.md`: prompt-pack contents and review gate.
- `references/grading-strategy.md`: end-to-end grading strategy, calibration, batching, audit, and close-out thinking.
- `references/speed-accuracy-controls.md`: accuracy controls for higher-throughput runs.
- `references/subject-scoring-defaults.md`: physics, math, chemistry, biology, humanities, language, and essay-style grading defaults.
