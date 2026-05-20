import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_spec(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    required = ["problemText", "referenceAnswer", "totalPoints"]
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise ValueError(f"missing required keys: {', '.join(missing)}")
    return data


def normalize_points(spec):
    sub = spec.get("subquestionPoints")
    if not sub:
        return f"Total points: {spec['totalPoints']}"
    if isinstance(sub, dict):
        lines = [f"- {k}: {v} points" for k, v in sub.items()]
    elif isinstance(sub, list):
        lines = [f"- {item}" for item in sub]
    else:
        lines = [f"- {sub}"]
    return "Subquestion points:\n" + "\n".join(lines)


def format_optional_list(title, value):
    if not value:
        return ""
    if isinstance(value, list):
        items = "\n".join(f"- {item}" for item in value)
    else:
        items = f"- {value}"
    return f"{title}\n{items}\n"


def build_rubric_generation_prompt(spec):
    points_block = normalize_points(spec)
    constraints = spec.get("teacherConstraints", "")
    return f"""# Rubric Generation Prompt

You are a senior subject teacher and scoring-rubric designer.

Task:
Generate a strict grading rubric for the following problem.

Requirements:
- Split the rubric by subquestion if the problem has multiple parts.
- Respect the provided total score and subquestion score allocation.
- Accept algebraically equivalent expressions.
- Award partial credit for key facts, formulas, relationships, evidence, reasoning, or intermediate steps when the rubric allows it.
- Define zero-credit cases clearly.
- List common wrong answers and how they should be scored.
- Output both:
  1. a human-readable rubric
  2. a JSON scoring schema with per-part score ceilings and decision rules

Problem Title:
{spec.get('title', 'Untitled Problem')}

Subject:
{spec.get('subject', 'Unknown')}

Grade Level:
{spec.get('gradeLevel', 'Unknown')}

Problem Text:
{spec['problemText']}

Reference Answer:
{spec['referenceAnswer']}

Point Allocation:
{points_block}

Teacher Constraints:
{constraints or 'None'}
"""


def build_original_question_prompt(spec):
    points_block = normalize_points(spec)
    return f"""# Original Question Prompt

You are a subject expert. Solve and explain the following original problem.

Output requirements:
- Restate the problem briefly
- Give a standard solution
- Show the main reasoning chain
- Identify the key formulas or steps
- Match the explanation to the score allocation

Problem Title:
{spec.get('title', 'Untitled Problem')}

Subject:
{spec.get('subject', 'Unknown')}

Grade Level:
{spec.get('gradeLevel', 'Unknown')}

Problem Text:
{spec['problemText']}

Reference Answer:
{spec['referenceAnswer']}

Point Allocation:
{points_block}
"""


def build_standard_model_grading_prompt(spec):
    points_block = normalize_points(spec)
    rubric_placeholder = spec.get(
        "rubricText",
        "[Insert generated scoring rubric here before using this grading prompt.]",
    )
    return f"""# Standard Model Grading Prompt Draft

Status: DRAFT - MUST BE REVIEWED AND APPROVED BY THE USER BEFORE ACTUAL GRADING USE.

You are a grading model for subjective questions.

Task:
Read the student's uploaded paper image and grade it strictly according to the rubric below.

Scoring rules:
- Grade each subquestion separately.
- Follow the rubric exactly.
- Accept equivalent expressions when the rubric allows them.
- Give partial credit for key correct facts, formulas, evidence, or reasoning steps when the rubric allows it.
- Do not invent extra credit.
- If the image is unreadable or the work is too ambiguous, mark `needsReview=true`.

Return JSON in this shape:
{{
  "partScores": {{}},
  "totalScore": 0,
  "reasons": {{}},
  "confidence": 0.0,
  "needsReview": false
}}

Problem Title:
{spec.get('title', 'Untitled Problem')}

Subject:
{spec.get('subject', 'Unknown')}

Grade Level:
{spec.get('gradeLevel', 'Unknown')}

Problem Text:
{spec['problemText']}

Reference Answer:
{spec['referenceAnswer']}

Point Allocation:
{points_block}

Scoring Rubric:
{rubric_placeholder}
"""


def build_review_required(spec):
    return f"""# Review Required Before Production Use

This prompt pack was generated from uploaded source materials and is not production-ready until the user reviews it.

Mandatory review steps:

1. Read `rubric-generation-prompt.md` and generate the rubric.
2. Paste or merge the rubric into `standard-model-grading-prompt.md`.
3. Show `standard-model-grading-prompt.md` to the user.
4. Ask the user whether any scoring details need to be modified, added, or removed.
5. Only use the grading prompt after explicit approval.

Suggested user review checklist:

- Are the subquestion scores correct?
- Are equivalent expressions accepted where they should be?
- Are partial-credit rules complete?
- Are zero-credit rules too harsh or too loose?
- Are common wrong answers and edge cases covered?
- Is any school-specific scoring preference missing?

Problem title:
{spec.get('title', 'Untitled Problem')}
"""


def build_source_bundle(spec):
    points_block = normalize_points(spec)
    extra = []
    extra.append(format_optional_list("Problem Images:", spec.get("problemImages")))
    extra.append(format_optional_list("Answer Images:", spec.get("answerImages")))
    extra.append(format_optional_list("Student Paper Images:", spec.get("studentPaperImages")))
    return f"""# Prompt Pack Source Bundle

Title: {spec.get('title', 'Untitled Problem')}
Subject: {spec.get('subject', 'Unknown')}
Grade Level: {spec.get('gradeLevel', 'Unknown')}

## Problem Text

{spec['problemText']}

## Reference Answer

{spec['referenceAnswer']}

## Point Allocation

{points_block}

## Teacher Constraints

{spec.get('teacherConstraints', 'None')}

{''.join(extra)}
"""


def write_outputs(spec, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "normalized_input.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "source_bundle.md").write_text(build_source_bundle(spec), encoding="utf-8")
    (out_dir / "rubric-generation-prompt.md").write_text(
        build_rubric_generation_prompt(spec),
        encoding="utf-8",
    )
    (out_dir / "original-question-prompt.md").write_text(
        build_original_question_prompt(spec),
        encoding="utf-8",
    )
    (out_dir / "standard-model-grading-prompt.md").write_text(
        build_standard_model_grading_prompt(spec),
        encoding="utf-8",
    )
    (out_dir / "review-required.md").write_text(
        build_review_required(spec),
        encoding="utf-8",
    )


def main():
    if len(sys.argv) != 3:
        print("usage: build_prompt_pack.py INPUT_JSON OUTPUT_DIR")
        raise SystemExit(2)
    spec = load_spec(sys.argv[1])
    out_dir = Path(sys.argv[2]).resolve()
    write_outputs(spec, out_dir)
    print(str(out_dir))


if __name__ == "__main__":
    main()
