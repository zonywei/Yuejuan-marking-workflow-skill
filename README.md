# Yuejuan Marking Workflow Skill / 阅卷工作流 Skill

## 中文介绍

这是一个面向教师、教研团队、学校和教育公司的通用 Agent/智能体阅卷工作流 Skill，用于辅助主观题阅卷、评分标准整理、批量评分、复核对账和教师报告生成。

当前 Skill 名称为 `$zhixue-marking-workflow`。名称保留了最早的智学网场景，便于已有 Agent 继续识别和调用；但项目定位已经扩展为通用网页登录阅卷平台工作流：智学网优先，同时可以迁移到其他需要登录、取卷、评分、提交、复核和对账的阅卷系统。

## 面向用户

核心用户是教师，尤其是需要批改大量主观题的一线学科教师。

适合：

- 一线教师：希望提高阅卷效率，同时保持评分一致性和可复核性。
- 教研组长或备课组：希望统一评分标准、复盘共性错误、产出教学反馈。
- 学校或教育公司：希望把 AI 辅助阅卷接入现有网页阅卷平台，但需要安全、可审计的流程。
- 教育产品和技术团队：希望把网页登录阅卷平台拆成“登录会话、试卷缓存、评分、提交、复核、报告”等可复用模块。

## 解决的问题

主观题阅卷真正困难的不只是“点提交”。更重要的是：

- 评分标准能不能稳定执行。
- 空白卷、边界卷、低置信度卷能不能识别。
- 批量处理后能不能回查每一份卷子的评分依据。
- 本地评分记录、提交事件和平台状态能不能对得上。
- 阅卷结束后能不能形成教师可直接阅读的教学反馈报告。

## 核心能力

- 评分标准整理：从题目、参考答案、分值拆出 rubric 和评分原子。
- Prompt Pack 生成：生成 rubric prompt、原题讲解 prompt 和模型阅卷 prompt 草稿。
- AI 辅助评分：要求结构化输出每小问得分、总分、理由、置信度和复核标记。
- 批量阅卷：支持缓存、分批评分、置信度路由、抽样复核和低置信度队列。
- 平台适配：以智学网为主要 adapter，同时给出迁移到其他网页登录阅卷平台的方法。
- 对账恢复：用本地 ledger、event log 和平台复核列表确认阅卷是否真正完成。
- 教师报告：从保存证据生成阅卷概况、共性错误、高分特征、典型卷例和教学建议。

## 工作流

1. 定标：确认题目范围、总分、小问分值、评分原子、0 分规则和等价答案。
2. 校准：先看少量样本，包括空白、低分、部分得分、高分和边界卷。
3. 稳定：把校准结果转成 prompt 规则、校验规则、复核标记和错误标签。
4. 批量：先缓存证据，再分批评分，并持续写入本地 ledger。
5. 复核：抽查高置信度自动评分，重点复核低置信度和疑似 0 分卷。
6. 对账：比较本地 ledger、提交事件和平台状态。
7. 报告：用保存的证据生成教师能直接阅读的阅卷反馈。
8. 沉淀：把通用规则留在 Skill，把本题专属细则留在本次阅卷目录。

## 安装

把仓库克隆到你的 Agent/智能体 Skill 目录。不同 Agent 的目录可能不同，下面是常见示例。

Codex:

```powershell
git clone https://github.com/zonywei/Yuejuan-marking-workflow-skill.git $env:USERPROFILE\.codex\skills\zhixue-marking-workflow
```

Claude Code:

```powershell
git clone https://github.com/zonywei/Yuejuan-marking-workflow-skill.git $env:USERPROFILE\.claude\skills\zhixue-marking-workflow
```

macOS / Linux:

```bash
git clone https://github.com/zonywei/Yuejuan-marking-workflow-skill.git ~/.codex/skills/zhixue-marking-workflow
git clone https://github.com/zonywei/Yuejuan-marking-workflow-skill.git ~/.claude/skills/zhixue-marking-workflow
```

其他支持 `SKILL.md` 的 Agent，可以把整个仓库作为一个 Skill 目录安装，并确保目录内保留 `SKILL.md`、`references/`、`scripts/` 和 `agents/`。

## 快速使用

在支持 Skill 调用的 Agent 里明确调用：

```text
Use $zhixue-marking-workflow 帮我根据这道题和参考答案整理评分标准，并准备批量阅卷流程。
```

或：

```text
Use $zhixue-marking-workflow to prepare a rubric, grading prompt, and review workflow for this subjective question.
```

## 已发布平台

- GitHub: `https://github.com/zonywei/Yuejuan-marking-workflow-skill`
- agentskill.sh: `https://agentskill.sh/zonywei/yuejuan-marking-workflow-skill`
- SkillHQ: `https://skillhq.dev/skills/user_0404bb5c/zhixue-marking-workflow`

## 商店 Listing 信息

推荐标题：

```text
Yuejuan Marking Workflow Skill
```

一句话介绍：

```text
面向教师和教育机构的通用主观题阅卷工作流：整理评分标准、辅助批量评分、复核对账，并生成教学反馈报告。
```

推荐分类：

```text
Education, Productivity, AI Agents
```

关键词：

```text
teacher, education, grading, marking, rubric, subjective questions, AI-assisted grading, web grading platform, Zhixue, reconciliation, teacher reports
```

## 典型使用场景

- 教师上传题目、参考答案和分值，Agent 帮助生成评分标准草稿。
- 教师登录阅卷平台后，Agent 协助观察当前平台的可操作工作流。
- 批量缓存学生答题图片，按 rubric 进行 AI 辅助评分。
- 将低置信度、边界卷、疑似空白卷放入复核队列。
- 对已提交或重提的分数与平台复核列表做对账。
- 生成面向教师的阅卷报告和教学反馈。

## 智学网 Adapter

`scripts/zhixue_mark.py` 是智学网专用 helper，用于已授权教师会话下的 fetch/cache/submit/recommit 流程。

先从示例配置复制本地配置文件：

```text
scripts/zhixue_mark.config.example.json
```

安装脚本依赖：

```powershell
py -3 -m pip install -r requirements.txt
```

常用命令：

```powershell
py -3 .\scripts\zhixue_mark.py calibrate-blanks .\confirmed-blank-papers
py -3 .\scripts\zhixue_mark.py current
py -3 .\scripts\zhixue_mark.py commit SCORE
py -3 .\scripts\zhixue_mark.py recommit-user USER_CODE SCORE
py -3 .\scripts\zhixue_mark.py recommit ITEM_ID SCORE USER_CODE
py -3 .\scripts\zhixue_mark.py batch-zero COUNT
py -3 .\scripts\zhixue_mark.py status
```

只有在教师确认当前任务允许提交、重提或临时占卷时，才使用提交类命令。

## Prompt Pack 生成

当评分标准或模型阅卷 prompt 还不稳定时，使用：

```powershell
py -3 .\scripts\build_prompt_pack.py .\scripts\prompt_pack.example.json .\prompt-pack-out
```

会生成：

- `rubric-generation-prompt.md`
- `original-question-prompt.md`
- `standard-model-grading-prompt.md`
- `review-required.md`
- `source_bundle.md`
- `normalized_input.json`

真实阅卷前，教师需要审阅并确认生成的评分 prompt。

## 跨平台迁移

对于非智学网平台，保留阅卷策略，只替换平台 adapter。

迁移时按这个顺序观察：

1. 观察一次人工阅卷流程：打开试卷、看答案、输入分数、提交、进入下一份。
2. 只在教师已登录且授权的当前阅卷任务里检查网络请求。
3. 找出任务信息、试卷获取、图片获取、提交、复核列表和重评路径。
4. 先测试只读接口，再测试提交接口。
5. 先缓存一份试卷，并和浏览器界面比对。
6. 提交前获得明确授权，提交后立即对账。

不要自动绕过 CAPTCHA、短信、扫码、人机验证、任务冲突或阅卷权属冲突。

## 安全与隐私

不要提交到仓库：

- cookies 或 tokens。
- local `zhixue_mark.config.json`。
- 真实学生 ID、姓名或答题图片。
- 阅卷 ledger、event log 或含学生数据的报告。
- `zhixue_work/` 等临时输出目录。

`.gitignore` 已排除常见本地配置和缓存路径，但每次提交前仍应检查 `git status`。

## 目录结构

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

## 校验

```powershell
py -3 "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
py -3 -B -m py_compile .\scripts\build_prompt_pack.py .\scripts\zhixue_mark.py
```

## 许可证

本项目使用 MIT License。你可以使用、修改、分发和商业使用本项目，但需要保留版权声明和许可证文本。

---

## English Introduction

Yuejuan Marking Workflow Skill is a general SKILL.md agent skill for teachers, teaching teams, schools, and education companies. It helps AI agents support subjective-question grading, rubric preparation, batch scoring, reconciliation, and teacher-facing report generation.

The current skill name is `$zhixue-marking-workflow`. The name is preserved for compatibility with existing agent installations, but the project is no longer limited to Zhixue. It is Zhixue-first and can be adapted to similar authenticated web grading platforms that require login, paper fetching, scoring, submission, review, and reconciliation.

## Intended Users

The primary users are teachers, especially subject teachers grading large volumes of subjective-answer papers.

Good fits:

- Teachers who want faster grading without losing consistency or accountability.
- Teaching leads who need shared rubrics, common-error summaries, and teaching feedback.
- Schools or education companies integrating AI-assisted grading into existing web marking systems.
- Education product or engineering teams modeling grading platforms as session, cache, scoring, submission, reconciliation, and reporting modules.

## What It Helps With

The hard part of subjective-question grading is not just clicking Submit. The workflow focuses on:

- applying the rubric consistently
- identifying blank, borderline, and low-confidence papers
- preserving evidence for every score
- reconciling local records with platform submission status
- producing useful teaching feedback after grading

## Core Capabilities

- Rubric preparation: turn a question, answer key, and score allocation into scoring atoms.
- Prompt pack generation: create rubric, original-question, and model-grading prompt drafts.
- AI-assisted scoring: require structured part scores, total score, reasons, confidence, and review flags.
- Batch grading: cache papers, score in batches, route by confidence, audit samples, and review uncertain cases.
- Platform adaptation: use Zhixue as the first adapter and apply the same strategy to similar web grading systems.
- Reconciliation and recovery: compare local ledgers, event logs, and platform status before claiming completion.
- Teacher-facing reports: summarize completion, common mistakes, strong responses, examples, and teaching suggestions.

## Workflow

1. Define the task, score ceiling, scoring atoms, zero-credit rules, and acceptable equivalents.
2. Calibrate on a small sample: blank, low, partial, high, and borderline papers.
3. Stabilize prompts, validation checks, review flags, and error tags.
4. Batch only after caching evidence and writing structured ledger rows.
5. Audit auto-scored papers and review uncertain or suspicious cases.
6. Reconcile local records, submit events, and platform status.
7. Generate reports from saved evidence.
8. Keep reusable rules in the skill and task-specific rules in the run folder.

## Install

Clone this repository into the skill directory used by your AI agent.

Codex:

```powershell
git clone https://github.com/zonywei/Yuejuan-marking-workflow-skill.git $env:USERPROFILE\.codex\skills\zhixue-marking-workflow
```

Claude Code:

```powershell
git clone https://github.com/zonywei/Yuejuan-marking-workflow-skill.git $env:USERPROFILE\.claude\skills\zhixue-marking-workflow
```

macOS / Linux:

```bash
git clone https://github.com/zonywei/Yuejuan-marking-workflow-skill.git ~/.codex/skills/zhixue-marking-workflow
git clone https://github.com/zonywei/Yuejuan-marking-workflow-skill.git ~/.claude/skills/zhixue-marking-workflow
```

For other agents that support `SKILL.md`, install the whole repository as one skill folder and keep `SKILL.md`, `references/`, `scripts/`, and `agents/` together.

## Quick Use

Invoke it explicitly in a compatible agent:

```text
Use $zhixue-marking-workflow to prepare a rubric, grading prompt, and review workflow for this subjective question.
```

## Published Listings

- GitHub: `https://github.com/zonywei/Yuejuan-marking-workflow-skill`
- agentskill.sh: `https://agentskill.sh/zonywei/yuejuan-marking-workflow-skill`
- SkillHQ: `https://skillhq.dev/skills/user_0404bb5c/zhixue-marking-workflow`

## Marketplace Listing

Recommended title:

```text
Yuejuan Marking Workflow Skill
```

Short description:

```text
A general agent skill for teachers and education teams: prepare rubrics, assist batch scoring, reconcile results, and generate teaching feedback reports.
```

Suggested category:

```text
Education, Productivity, AI Agents
```

Keywords:

```text
teacher, education, grading, marking, rubric, subjective questions, AI-assisted grading, web grading platform, Zhixue, reconciliation, teacher reports
```

## Typical Use Cases

- A teacher provides a question, answer key, and points; the agent drafts the rubric.
- After the teacher logs into a grading platform, the agent helps map the safe workflow.
- Student answer images are cached and graded against the rubric.
- Low-confidence, borderline, and suspected blank papers are routed to review.
- Submitted or recommitted scores are reconciled against platform state.
- A teacher-facing grading report is generated from saved evidence.

## Zhixue Adapter

`scripts/zhixue_mark.py` is a Zhixue-specific helper for fetch/cache/submit/recommit flows under an authorized teacher session.

Start from the example config:

```text
scripts/zhixue_mark.config.example.json
```

Install script dependencies:

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

Use submit/recommit commands only when the teacher confirms that the current task allows the action.

## Prompt Pack Generation

Use this when the rubric or model-grading prompt is not ready:

```powershell
py -3 .\scripts\build_prompt_pack.py .\scripts\prompt_pack.example.json .\prompt-pack-out
```

It generates:

- `rubric-generation-prompt.md`
- `original-question-prompt.md`
- `standard-model-grading-prompt.md`
- `review-required.md`
- `source_bundle.md`
- `normalized_input.json`

The teacher should review and approve the generated grading prompt before real grading.

## Cross-Platform Adaptation

For non-Zhixue platforms, keep the grading strategy and replace only the platform adapter.

Adaptation checklist:

1. Observe one manual grading cycle.
2. Inspect network requests only inside the authorized teacher task.
3. Identify task metadata, paper fetch, image fetch, submit, review-list, and correction paths.
4. Test read-only calls before submit calls.
5. Cache one paper and compare it with the browser UI.
6. Get explicit approval before submission and reconcile immediately after.

Do not automate around CAPTCHA, SMS, QR confirmation, human verification, task mismatch, or reviewer ownership conflicts.

## Safety And Privacy

Never commit:

- cookies or tokens
- local `zhixue_mark.config.json`
- real student identifiers, names, or answer images
- grading ledgers, event logs, or reports containing student data
- temporary output folders such as `zhixue_work/`

The `.gitignore` excludes common local config and cache paths, but always inspect `git status` before committing.

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

## Validation

```powershell
py -3 "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
py -3 -B -m py_compile .\scripts\build_prompt_pack.py .\scripts\zhixue_mark.py
```

## License

This project is licensed under the MIT License. You may use, modify, distribute, and use it commercially, provided that the copyright notice and license text are preserved.
