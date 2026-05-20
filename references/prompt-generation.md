# Prompt Generation

## Goal

When the user provides:

- original problem statement or original paper
- reference answer
- total score or per-part scores

the agent should generate three outputs:

1. a scoring-rubric generation prompt
2. an original-question prompt
3. a standard model grading prompt

The usual flow is:

1. normalize uploaded source materials
2. generate rubric-generation prompt
3. ask the model to generate the rubric
4. generate the grading prompt draft from the normalized materials plus rubric
5. show the grading prompt draft to the user
6. let the user modify, add, or delete rubric details
7. only use the prompt after explicit user approval

## Expected Inputs

Minimum:

- `problemText`
- `referenceAnswer`
- `totalPoints`

Recommended:

- `title`
- `subject`
- `gradeLevel`
- `subquestionPoints`
- `teacherConstraints`
- `problemImages`
- `answerImages`

## Expected Outputs

- `rubric-generation-prompt.md`
- `original-question-prompt.md`
- `standard-model-grading-prompt.md`
- `review-required.md`

## Rubric Requirements

The rubric-generation prompt should require the model to produce:

- subquestion-by-subquestion point allocation
- key formulas, key steps, and equivalent expressions
- partial-credit rules
- zero-credit rules
- common wrong answers and how to score them
- final JSON scoring schema when possible

## Original-Question Prompt

This prompt is for solving or explaining the original problem itself. It should contain:

- clean restatement of the problem
- reference answer
- score allocation
- expected solution path

## Standard Model Grading Prompt

This prompt is for grading a student's uploaded paper. It must be treated as a draft before use. It should require:

- reading the student image
- applying the rubric exactly
- scoring each subquestion separately
- outputting total score
- giving short reasons
- giving a confidence score
- declaring whether human review is needed

## Mandatory Review Gate

Before actual grading use:

1. show the generated standard grading prompt to the user
2. let the user revise the rubric details
3. let the user add or remove edge-case scoring rules
4. only then treat the prompt as approved for production use
