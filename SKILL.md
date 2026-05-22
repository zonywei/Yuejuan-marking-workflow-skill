---
name: zhixue-marking-workflow
description: "Use this skill for Zhixue teacher-side subjective-question grading workflows: AI-assisted rubric scoring, script/API-based batch grading, cache-ledger recovery, blank screening, recommit/review reconciliation, and concise teacher-facing grading reports."
metadata:
  short-description: "Zhixue grading workflow with cache, ledger, and reports."
---

# Zhixue Marking Workflow

## Overview

This skill packages a practical Zhixue subjective-question grading workflow:

- use the model to score subjective-question papers from the rubric
- automate repeated actions around fetch, cache, submit, and continue
- preserve a local cache for review and recovery
- use blank-paper screening conservatively
- calibrate blank thresholds from multiple confirmed blank papers
- optimize for both speed and accuracy through confidence routing, validation, and sampling
- turn grading outcomes into teaching summaries and technical retrospectives

Use this skill only with a valid teacher session and with the user's approval to operate on their Zhixue grading task.

## Capabilities

- score cached Zhixue subjective-question images against a user-confirmed rubric
- automate fetch/cache/submit/recommit/review-list operations when the authenticated session allows it
- batch occupy papers for later offline scoring when the current task permits recommit
- keep resumable local ledgers, pending queues, event logs, and report evidence
- generate concise teacher-facing summaries from saved grading records

## When To Use This Skill

Use it when the user asks to:

- grade Zhixue subjective papers more efficiently
- inspect or improve a Zhixue grading script
- package a Zhixue grading workflow into reusable tooling
- generate rubrics and prompt packs from uploaded source problems and answers
- analyze common student errors after grading
- create meeting briefs, teaching summaries, or technical retrospectives from a grading run

Do not use it for bypassing login, obtaining unauthorized access, or inventing unofficial endpoints without evidence from the current authenticated session.

## Speed And Accuracy Priorities

For this skill, "fast and accurate" depends on more than prompt quality. Prioritize these controls:

1. Version the rubric and prompt pack for each question.
2. Force structured grading output:
   - per-part scores
   - total score
   - reasons
   - confidence
   - review flag
3. Validate score bounds before submission:
   - no part score below `0`
   - no part score above its ceiling
   - total score must equal the sum of part scores
4. Calibrate blank thresholds from confirmed blank samples, not from guesswork.
5. Use confidence routing:
   - `confidence >= 0.90`: high confidence, eligible for auto-submit after validation
   - `0.70 <= confidence < 0.90`: gray zone, use second-pass scoring, sampling audit, or manual review
   - `confidence < 0.70`: low confidence, manual review
   - unreadable image or rubric ambiguity: manual review regardless of numeric confidence
6. Keep an exact grading log for replay and post-analysis.
7. Add audit sampling even for auto-submitted papers so drift is caught early.
8. Preprocess poor scans when needed before model scoring.

## Workflow

1. Confirm the user is already logged in on Zhixue and has an active teacher session.
2. Identify the current grading target:
   - `markingPaperId`
   - `topicNumStr`
   - grading page `referer`
3. Calibrate blank threshold from a folder of confirmed blank papers in the current grading environment.
4. Use the bundled script in `scripts/zhixue_mark.py` to:
   - fetch the current paper
   - download and cache the current image locally
   - hand the image and rubric to the model for scoring
   - commit the model score
   - optionally continue until the next non-blank paper
5. Route papers by confidence using the default thresholds above unless the rubric, teacher-corrected samples, or user instructions justify stricter limits.
6. Keep blank screening conservative. Treat `0.01` only as a fallback when no calibration set exists.
7. Preserve local artifacts:
   - cached image files
   - `current.json`
   - optional grading log
8. After the grading batch, summarize:
   - common scoring errors
   - common strengths
   - estimated or exact score distribution if logs exist
   - teaching implications

For rubric and prompt generation:

1. Collect uploaded materials:
   - original problem text or paper
   - reference answer
   - total points
   - optional per-part points
2. Normalize them into a JSON input file.
3. Run `scripts/build_prompt_pack.py` to generate a prompt pack.
4. Use the generated rubric-generation prompt to ask the model for a scoring rubric.
5. Insert the rubric into the standard grading prompt draft.
6. Show the draft grading prompt to the user.
7. Let the user modify, add, or delete scoring details.
8. Use the grading prompt only after explicit user confirmation.

## Script Usage

The reusable script is [scripts/zhixue_mark.py](./scripts/zhixue_mark.py).

Before running it, provide config in one of these ways:

- environment variable `ZHIXUE_MARK_CONFIG`
- default config file `scripts/zhixue_mark.config.json`

Start from [scripts/zhixue_mark.config.example.json](./scripts/zhixue_mark.config.example.json) and copy it to `scripts/zhixue_mark.config.json` locally before use.

Required config keys:

- `markingPaperId`
- `topicNumStr`
- `referer`
- `cookie`

Optional config keys:

- `outDir`
- `blankThreshold`

Core commands:

```powershell
py -3 .\scripts\zhixue_mark.py calibrate-blanks .\confirmed-blank-papers
py -3 .\scripts\zhixue_mark.py current
py -3 .\scripts\zhixue_mark.py commit 14
py -3 .\scripts\zhixue_mark.py recommit-user 78361158 0
py -3 .\scripts\zhixue_mark.py recommit "[\"item-id\"]" 0 78361158
py -3 .\scripts\zhixue_mark.py batch-zero 20
py -3 .\scripts\zhixue_mark.py status
py -3 .\scripts\zhixue_mark.py grade 9
py -3 .\scripts\zhixue_mark.py grade 14 0.01
py -3 .\scripts\zhixue_mark.py skip-blanks 0.01
py -3 .\scripts\build_prompt_pack.py .\scripts\prompt_pack.example.json .\prompt-pack-out
```

Behavior:

- `calibrate-blanks PATH`: compute `darkRatio` statistics from multiple confirmed blank papers and output strict/recommended thresholds
- `current`: fetch current paper, cache image, write `current.json`
- `commit SCORE`: submit score for cached paper
- `recommit-user USER_CODE SCORE`: locate a graded paper through the review list and overwrite its score
- `recommit ITEM_ID SCORE [USER_CODE]`: overwrite by the original occupied `itemId`; use this when `searchMarked` cannot find the user
- `batch-zero COUNT`: first occupy `COUNT` papers with `0` and append them to `pending_regrade.jsonl` for later offline regrading
- `status`: print current config paths, thresholds, and cache pointers for audit/debug
- `grade SCORE [THRESHOLD]`: submit current score, then continue through blank papers until the next non-blank paper
- `skip-blanks [THRESHOLD]`: skip blank papers conservatively until the next non-blank paper

In agent use, the normal pattern is:

1. fetch image
2. ask the model to score against the rubric
3. auto-submit if confidence is high enough
4. only escalate gray cases when needed

## Preferred Pure Script Batch Mode

For high-throughput Zhixue marking runs, prefer pure script mode when feasible and approved for the current task. Use Chrome or browser automation only to confirm login, capture `cookie` / `referer` / task parameters, or recover a failed session; do not use the browser for ordinary per-paper grading.

Preferred high-throughput flow:

1. After approval for the current task, use script commands such as `batch-zero` to occupy/cache available papers with provisional `0` scores.
2. Store every occupied paper in the authoritative queue with `userCode`, `itemId`, `imagePath`, provisional score, and final-score status.
3. Treat provisional `0` submission as an occupy/cache strategy only when the current workflow permits later recommit and the user approves it. Smoke-test the occupy/recommit chain when the task shape or script integration changes.
4. Before offline scoring, compute an answer-density metric for all cached images and sort from dense to sparse. Do not front-load a separate blank-paper pass.
5. Score dense answer sheets first, sparse answer sheets next, and the low-density tail last; the tail is expected to contain blank or near-blank `0` papers in a cluster.
6. Build contact sheets or model batches with at least 6 papers when legibility remains good. Larger batches are acceptable only when crop labels and answer regions remain unambiguous.
7. Crop each paper to the relevant response area for batch scoring while preserving the original image path for zoom-in review.
8. Require structured scoring output: `userCode`, `itemId`, per-part scores, total score, brief reason, confidence, and review flag.
9. Recommit true scores through review/recommit. If review-list lookup misses a paper, fall back to the stored `itemId`.
10. Reconcile the ledger, event log, and backend review list before claiming completion.

## Runtime Persistence And Evidence Capture

During grading, save progress continuously. Do not rely on chat memory, browser state, or model memory for later reporting. The agent may choose the exact checkpoint cadence for throughput, but it must stay bounded.

1. Write authoritative ledger checkpoints after each contact-sheet/model batch, or at least every 10 scored papers, or before any long pause/context switch. Per-paper immediate writes are allowed but not required when batching is faster.
2. Each ledger checkpoint must include all papers scored since the previous checkpoint, with `userCode`, `itemId`, image path, crop/contact-sheet path when used, per-part scores, total score, concise reason, confidence, review flag, and current action.
3. After every submit or recommit batch, append event-log records with timestamp, `userCode`, `itemId`, submitted score, API result, retry count, and any fallback path used.
4. Save batch artifacts as they are produced: contact sheets, cropped typical-answer candidates, density/order manifests, review queues, and low-confidence lists.
5. Record error tags while grading, not only at the end. Use compact reusable labels such as blank, irrelevant, wrong model, naked formula, calculation error, missing key equation, position error, unreadable, or needs review.
6. Keep a running summary file or JSON snapshot after each batch with completed count, remaining count, score distribution so far, likely typical examples, unresolved review cases, and failed submissions.
7. Before long pauses, context switches, or report generation, checkpoint the ledger and event log and verify that row counts and unique `userCode` counts still match expectations.
8. Generate teacher-facing summaries from saved ledger/evidence only. If a statistic, common error, or typical example is not supported by saved records or screenshots, label it as an estimate or omit it.
9. Preserve enough evidence for the final report: representative full-score, partial-score, low-score, wrong-model, and zero/blank examples should have cropped image paths and one-line reasons available before report writing begins.

## Goal-Style Completion Discipline

A real Zhixue grading run is a goal-style task. Once the user starts a concrete grading batch, treat completion as the full current round being graded, submitted/recommitted, reconciled, and reported when requested.

1. Do not stop merely because one batch, one contact sheet, or one scoring pass is complete.
2. Keep advancing until the current round has no remaining ungraded queue items, no unresolved recommit failures, and no ledger/backend mismatch.
3. If tool context is about to change, checkpoint first and leave a resumable state with next action, remaining queue path, and unresolved cases.
4. Escalate only real blockers: expired login/session, missing rubric, ambiguous user scoring rule, unreadable evidence that affects score, API failure that cannot be retried safely, or user instruction to pause/stop.
5. If a formal goal mechanism is available in the host environment and the user starts an actual grading run, use it to track the run objective and mark it complete only after the full round is finished.

## Default Scoring Principles

These defaults come from high-school physics subjective grading, especially calculation and experiment questions. For other subjects, or when the current rubric conflicts with this section, the question-specific rubric and the user's latest instruction override these physics defaults.

1. `等价给分`: Different valid solution paths receive the same credit when they prove the same required result or relationship.
2. `只看对的`: Award credit for correct, relevant work; do not let unrelated mistakes erase already-earned independent points unless the rubric says the mistake invalidates that step.
3. `关键公式给步骤分`: Give step credit for correct key formulas, physical relationships, conservation equations, or reasoning targets even when the final answer is incomplete.
4. `思路正确优先给分`: When the physical model, object selection, process selection, or equation setup is correct, preserve the corresponding reasoning points.
5. `计算错误不否定前面得分`: Arithmetic or algebra errors should not remove earlier correct setup/formula points, though they may lose result or follow-through points.
6. `不因表达方式扣分`: Do not deduct for nonstandard wording, symbol choice, or answer format if the physical meaning is clear and the rubric requirement is satisfied.
7. `空白或内容与本题无关或全错给0分`: Blank answers, irrelevant content, or answers with no correct physics for the current problem receive `0`.
8. `按当前小问和当前位置给分`: Respect the current subquestion boundaries and answer positions unless the user explicitly allows cross-position credit.
9. `碰巧结果正确不保留结果分`: If the process and physics are wrong and the result is only accidentally correct, do not award result credit.
10. `边界卷谨慎复核`: For sparse, unclear, or near-blank papers, prefer review over aggressive auto-zero when there is any plausible relevant work.
11. `答案分和过程分分开`: If the rubric has result points, a result-only answer may receive only those result points when there is no contradicting wrong physics; if the visible process is wrong, treat the result as accidental and do not award result credit.
12. `省略纯数学化简不扣分`: Do not deduct for omitted algebraic simplification when the correct physical relationship, substitutions, and final rubric target are clear.
13. `少量相关公式不按空白处理`: A paper with any plausible relevant formula, diagram mark, variable relation, or subquestion attempt is not a blank paper; route it to grading or review instead of auto-zero.
14. `有字不等于有分`: Dense writing, copied formulas, or long text still receives `0` when it never establishes a valid model, object, process, state comparison, or required physical relationship for the current problem.
15. `裸公式不等于有效关系`: Generic formulas such as `F=ma`, `PV=nRT`, energy, momentum, or kinematics equations earn credit only when tied to the correct object, process, state, direction, or variables required by the rubric.
16. `模型先于计算`: For physics problems, first judge whether the student chose the correct physical model/process/state; wrong-model work can invalidate a subquestion even if the algebra is lengthy.
17. `独立小问不连坐`: Award a later independent subquestion if its model and relationship are correct, even when earlier subquestions are blank or wrong, unless the current rubric makes the later score depend on the earlier result.
18. `只认稳定可辨认内容`: Use zoom/crop/review for unclear handwriting, but do not force credit for steps that cannot be read reliably.
19. `作答面积和OCR不直接决定分数`: Answer density, dark-ratio, and OCR are routing aids only; final scores must come from the rubric and direct visual reading of the response.
20. `低分和高疑似0分重点复核`: In batch workflows, prioritize review of nonzero low-score papers and high-suspicion zero papers because both under-crediting real steps and over-crediting invalid pseudo-steps occurred in prior runs.

## Score Validation Defaults

- Zhixue subjective-question grading usually uses integer scores. Submit integer scores by default.
- If the user-provided prompt, rubric, or official scoring standard includes decimal scores such as `0.5`, confirm the allowed score step before submitting decimals or changing the script.
- Validate score bounds before any submit/recommit: each part must be within its ceiling, and the total must equal the accepted part-score sum.

## Blank And Density Metrics

- `darkRatio` means the proportion of dark, ink-like pixels in the analyzed image or answer region after grayscale/threshold processing.
- Lower `darkRatio` usually means less writing, but it is only a routing signal. It must not replace direct visual grading.
- Calibrate blank thresholds from confirmed blank samples for the current scan style. Treat fallback thresholds such as `0.01` as conservative defaults only.
- Any plausible relevant formula, diagram mark, variable relation, or subquestion attempt should route to grading or review rather than automatic blank handling.

## Proven Live-Run Rules

The following rules were repeatedly validated in real Zhixue grading runs and should be treated as default operating behavior unless the current task instructions explicitly override them:

1. `Latest explicit user scoring rule overrides earlier rules.`
   - If the user later refines a scoring split, a result-only rule, or a subquestion boundary rule, apply the new rule going forward and re-audit already graded papers that may be affected.
2. `Keep one authoritative ledger.`
   - Record every reviewed paper in a local ledger such as `manual_grades.tsv` with:
     - `userCode`
     - per-part scores
     - total score
     - one-line scoring reason
   - Treat this ledger as the grading truth source for reports.
3. `Before submit, summarize the subquestion rationale when the user asks for traceability.`
   - For each paper, state a short `Q1/Q2/Q3` scoring reason first, then submit.
4. `Separate "occupy" from "final grading" when throughput matters.`
   - For high-volume runs, it is often faster to:
     - batch occupy papers with `0`
     - save `userCode + itemId + imagePath` into `pending_regrade.jsonl`
     - score offline from cached images
     - recommit the true score afterward
5. `When review-list lookup fails, fall back to the original occupied itemId.`
   - Some papers may disappear from `searchMarked` even though the original `itemId` still accepts recommit.
   - In those cases, use the stored `itemId` from `pending_regrade.jsonl` or the event log.
6. `Respect subquestion position integrity when the user requires it.`
   - Do not move a correct equation from `(1)` to `(2)` or `(3)` unless the user explicitly allows cross-position credit.
   - When the user says "write错位置不得分", enforce it retroactively as well.
7. `Do not give result points for lucky answers built on wrong physics.`
   - If the formula and process are wrong and the final result is only accidentally correct, do not keep the result score.
8. `Award partial formula points even when the full subquestion is wrong.`
   - If the user’s rubric splits a subquestion into multiple formula items, preserve any independently correct formula component such as:
     - correct height difference only
     - correct momentum relation only
     - correct energy relation only
9. `Prefer direct image reading over ad hoc OCR unless OCR quality is proven.`
   - In live runs, weak OCR often costs more time than it saves.
   - If the user explicitly says not to use Windows OCR, do not use it.
10. `Do not show large volumes of images in chat when the user flags token/latency cost.`
    - Use local contact sheets, local cache files, and short textual rationale instead.

## Session Recovery And Concurrency

Session expiry detection:

- Treat HTTP `401`, `403`, redirects to login pages, HTML returned where JSON is expected, JSON decode failures, repeated unusable `topicInfo`, or explicit login-expired messages as session-expiry signals.
- On session expiry, stop new submissions, checkpoint the ledger/event log/pending queue, report the last successful item, and ask the user to refresh login or provide a new authenticated session.
- After session refresh, resume from the authoritative local queue. Do not re-fetch or re-score completed items unless reconciliation shows a mismatch.
- Retry transient network errors with a small bounded retry count; do not loop indefinitely on authentication or task-identity errors.

Concurrency assumptions:

- Default assumption: single teacher/agent is grading the current question independently.
- If the platform indicates conflict, already-submitted state, double-evaluation/arbitration, HTTP `409`, changed score after fetch, or an item owned by another reviewer, pause that item and log it as a review conflict.
- Do not overwrite another grader's score through `recommit` unless the user explicitly confirms that the current task permits it.
- For arbitration or double-marking workflows, prefer the official browser workflow or task-specific confirmation over blind batch recommit.

## Reconciliation And Completion Checks

Use all three layers during close-out:

1. `manual ledger`
   - confirm row count, unique `userCode`, and final per-part totals
2. `event log`
   - verify every recommit and any direct-`itemId` fallback submissions
3. `backend review list`
   - verify total count and inspect pagination carefully

Important:

- Zhixue review-list pagination may not be normal zero-based pagination.
- Always verify actual `currentPage` semantics before crawling all pages.
- If the backend list omits papers that were successfully recommitted, reconcile against:
  - `events.jsonl`
  - `pending_regrade.jsonl`
  - the authoritative local ledger

Completion should only be claimed after:

- no remaining papers in the authoritative local queue
- no unresolved mismatch between ledger and successful commit events
- no submitted-but-unconfirmed papers except cases explicitly documented as backend-list omissions with successful `itemId` submit/recommit events
- report artifacts are generated if the user requested a report

## Reporting Rules From Live Runs

When the user asks for a final report:

1. Generate the report from the authoritative ledger, not from memory.
2. Keep the teacher-facing report concise and aimed at the subject teacher, not a technical audience. For physics grading tasks, assume the reader is a physics teacher.
3. Include:
   - scoring rules actually used
   - later rule corrections
   - score distribution
   - common error patterns
   - short lecture or remediation suggestions
   - representative full-score, partial-score, sparse-answer, and zero-score examples
4. Include concrete screenshots for typical answer examples, but never paste whole raw papers when a smaller crop is enough.
5. Crop screenshots to the response area and shrink them for layout efficiency. Do not spend time on duplicate masking when the platform already hides identities; apply extra masking only when visible sensitive information remains or the user asks for it.
6. Combine multiple typical examples side by side, label them clearly such as `Example 1`, `Example 2`, and caption each with its type, e.g. full-score standard answer, correct formula with calculation error, missing key equation, sparse answer, near-blank.
7. Keep captions short; the report should help a physics teacher quickly prepare feedback, not read a long audit log.
8. Put technical submission details, `itemId`, retry traces, and per-paper ledgers in appendices or separate logs, not in the main teacher-facing narrative.
9. If exact totals are unavailable, label them as estimates.
10. If exact totals are available from the ledger, state that explicitly.
11. If the user asked for desktop delivery, output both `docx` and `pdf` when possible. Prefer available document/report-generation and PDF-rendering companion skills over hand-built formatting.

## Companion Skills And Capabilities

This skill works best when the agent also has access to companion skills or equivalent capabilities in these areas:

1. `pdf-or-doc extraction`
   - needed when the user uploads original papers, answer PDFs, or DOCX files instead of plain text
2. `ocr-and-image-reading`
   - needed to extract content from scanned papers and handwritten student responses
3. `image-preprocessing`
   - needed for denoise, crop, contrast adjustment, and orientation correction on poor scans
4. `browser automation or session capture`
   - needed to get authenticated cookies, referer, current page context, or operate the grading UI when API use is not enough
5. `structured-output validation`
   - needed to validate model JSON, enforce score ceilings, and block malformed submissions
6. `logging-and-analytics`
   - needed for score logs, audit reports, error buckets, and post-exam statistics
7. `document/report generation`
   - needed for teaching briefs, technical retrospectives, and group meeting materials

If these skills do not exist as named skills in the current agent platform, the agent should still look for equivalent built-in capabilities or local scripts.

## Safety Rules

- Never hardcode the user's live cookies or session tokens into the skill files.
- Calibrate blank thresholds from multiple confirmed blank papers before enabling auto-blanking.
- Treat blank-paper screening as heuristic only.
- Model scoring should return both score and confidence.
- Treat Zhixue subjective scores as integer scores by default; ask the user to confirm before using decimal scores when the rubric includes decimals.
- Pause and recover rather than pushing through when login/session state, task identity, or reviewer ownership becomes uncertain.
- Use teacher-corrected samples to calibrate model prompts and confidence thresholds.
- Expect occasional `topicInfo = null` responses and retry before failing.
- Prefer exact score logs when the user asks for statistics; if no logs exist, label any ratio as an estimate.

## References

Read these only when needed:

If a referenced file is missing in a copied skill package, do not chase nonexistent paths. Continue from the core rules in this `SKILL.md`, and note the missing reference only if it affects the task.

- [references/workflow-retrospective.md](./references/workflow-retrospective.md)
  Use when the user wants the full engineering replay of the grading optimization.
- [references/teaching-analysis.md](./references/teaching-analysis.md)
  Use when the user wants a group-facing teaching brief, common mistakes, or lesson implications.
- [references/model-scoring.md](./references/model-scoring.md)
  Use when the user wants the model-scoring workflow, prompt shape, or confidence routing rules.
- [references/prompt-generation.md](./references/prompt-generation.md)
  Use when the user wants to generate scoring rubrics and reusable prompt packs from uploaded materials.
- [references/speed-accuracy-controls.md](./references/speed-accuracy-controls.md)
  Use when the user wants the concrete controls that keep the workflow both fast and accurate.
- [references/companion-skills.md](./references/companion-skills.md)
  Use when the user wants to know what extra skills or capability modules should be available to the agent.
- [references/exploration-path.md](./references/exploration-path.md)
  Use when the user wants the practical exploration path from manual grading to backend-assisted automation.

