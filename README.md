# Yuejuan Marking Workflow Skill

A Codex skill for teacher-side subjective-question grading workflows.

The skill is centered on Zhixue (`zhixue.com`) and also records a reusable method for adapting the same workflow to similar authenticated web grading platforms: rubric preparation, backend workflow exploration, AI-assisted scoring, batch grading, local ledgers, reconciliation, and teacher-facing reports.

## What This Is

- A standard Codex skill folder with `SKILL.md` as the agent entry point.
- A practical workflow for authorized teacher-side grading tasks.
- A Zhixue-specific adapter script for fetch/cache/submit/recommit flows.
- A set of reusable grading strategy references for calibration, batching, review, and reporting.
- A prompt-pack generator for turning problems, answers, and score allocations into draft grading prompts.

## What This Is Not

- It is not a login bypass tool.
- It is not an unauthorized scraping tool.
- It does not include live cookies, tokens, student data, or real grading records.
- It does not guarantee that a platform's private interface is stable.
- It does not replace teacher review for ambiguous, low-confidence, or contested papers.

## Install

Clone this repository into your Codex skills directory. On Windows PowerShell:

```powershell
git clone https://github.com/zonywei/Yuejuan-marking-workflow-skill.git $env:USERPROFILE\.codex\skills\zhixue-marking-workflow
```

On macOS or Linux:

```bash
git clone https://github.com/zonywei/Yuejuan-marking-workflow-skill.git ~/.codex/skills/zhixue-marking-workflow
```

Then start a new Codex session or reload skills.

## Quick Use

Ask Codex to use the skill explicitly:

```text
Use $zhixue-marking-workflow to prepare a Zhixue subjective-question grading workflow.
```

Typical requests:

- Prepare a rubric and grading prompt from a problem and answer key.
- Explore an authenticated web grading workflow after the teacher logs in.
- Cache papers locally before AI-assisted scoring.
- Batch score papers with confidence routing and review flags.
- Reconcile local ledgers with platform submission status.
- Generate a teacher-facing grading report from saved evidence.

## Repository Layout

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── grading-strategy.md
│   ├── model-scoring.md
│   ├── prompt-generation.md
│   ├── speed-accuracy-controls.md
│   └── subject-scoring-defaults.md
├── scripts/
│   ├── build_prompt_pack.py
│   ├── prompt_pack.example.json
│   ├── zhixue_mark.config.example.json
│   └── zhixue_mark.py
└── requirements.txt
```

## Prompt Pack Generation

Use `scripts/build_prompt_pack.py` when the rubric or model-grading prompt is not ready.

```powershell
py -3 .\scripts\build_prompt_pack.py .\scripts\prompt_pack.example.json .\prompt-pack-out
```

Generated files include:

- `rubric-generation-prompt.md`
- `original-question-prompt.md`
- `standard-model-grading-prompt.md`
- `review-required.md`
- `source_bundle.md`
- `normalized_input.json`

Review and approve the generated grading prompt before using it on real papers.

## Zhixue Adapter

`scripts/zhixue_mark.py` is a Zhixue-specific helper. It expects an authenticated teacher session and a local config file copied from:

```text
scripts/zhixue_mark.config.example.json
```

Install script dependencies when needed:

```powershell
py -3 -m pip install -r requirements.txt
```

Common commands:

```powershell
py -3 .\scripts\zhixue_mark.py calibrate-blanks .\confirmed-blank-papers
py -3 .\scripts\zhixue_mark.py current
py -3 .\scripts\zhixue_mark.py commit SCORE
py -3 .\scripts\zhixue_mark.py recommit-user USER_CODE SCORE
py -3 .\scripts\zhixue_mark.py recommit ITEM_ID SCORE USER_CODE
py -3 .\scripts\zhixue_mark.py batch-zero COUNT
py -3 .\scripts\zhixue_mark.py status
```

Only use submit/recommit operations when the user confirms that the current teacher task allows that action.

## Core Workflow

The skill encourages a controlled grading pipeline:

1. Define the task, score ceiling, rubric, score atoms, and zero-credit rules.
2. Calibrate on a small diverse sample before scaling.
3. Stabilize prompts, validation checks, and review flags.
4. Cache paper evidence before scoring or submitting.
5. Score in bounded batches with structured output.
6. Audit high-confidence auto scores and review uncertain cases.
7. Reconcile local ledgers, event logs, and platform status.
8. Generate reports from saved evidence, not from chat memory.

## Cross-Platform Adaptation

For non-Zhixue web grading systems, keep the grading strategy and replace only the platform adapter:

- observe one manual grading cycle
- inspect authenticated network traffic inside the current teacher task
- identify paper-fetch, image-fetch, submit, review-list, and correction paths
- test read-only calls first
- cache one paper and compare it with the UI
- submit only after explicit approval and immediate reconciliation

Do not continue automation through CAPTCHA, SMS, QR confirmation, task mismatch, ownership conflict, or unexplained platform state changes.

## Safety And Privacy

Never commit:

- cookies or tokens
- local `zhixue_mark.config.json`
- real student identifiers
- cached paper images
- grading ledgers or reports containing student data
- temporary `zhixue_work/` output

The repository `.gitignore` excludes the common local config and cache paths, but you should still inspect `git status` before every commit.

## Validation

The skill has been validated with Codex's skill validator and Python syntax checks. To re-check locally from a Codex environment:

```powershell
py -3 "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
py -3 -B -m py_compile .\scripts\build_prompt_pack.py .\scripts\zhixue_mark.py
```

## License

No open-source license has been selected yet. Until a license is added, reuse is limited by the default copyright rules of GitHub-hosted source code.
