# Positioning

Yuejuan Marking Workflow Skill is a general `SKILL.md` agent skill for AI-handled repetitive subjective-question draft scoring. It is Zhixue-first because the original workflow came from Zhixue teacher-side marking, but the reusable part is the grading workflow itself.

## 1. 一线教师

Teachers can use this project to:

- co-create a scoring reference rubric from a question, answer key, and score allocation
- prepare model-grading prompts before batch AI scoring
- identify low-confidence, blank, borderline, or suspicious papers
- keep review and reconciliation records
- generate teacher-facing summaries after marking

AI handles repetitive draft scoring. The teacher focuses on rubric confirmation, borderline cases, low-confidence papers, and final platform submission control.

## 2. AI Agent / Skill Developers

Agent and skill developers can use this repository as a reference for:

- designing a `SKILL.md` workflow around a real professional task
- separating platform adapters from domain logic
- using examples to show input, rubric, model prompt, structured output, review queue, and report
- preserving safety boundaries for authenticated browser workflows

The project is useful even if the target platform is not Zhixue, because the core loop is platform-independent.

## 3. 教育产品或学校技术团队

Education product teams and school technical teams can use the project to reason about:

- how to integrate AI scoring into existing web marking systems without turning it into a black box
- what evidence should be retained for audit and recovery
- where teacher confirmation is required
- how to design low-confidence review and final reconciliation
- how to generate teaching feedback from marking evidence

The recommended architecture is not "AI directly submits final scores without controls." It is "AI handles repetitive draft scoring, while the workflow keeps evidence, review, reconciliation, and teacher-approved submission gates."
