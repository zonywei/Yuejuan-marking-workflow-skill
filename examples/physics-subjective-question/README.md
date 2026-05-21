# 高中物理主观题示例

这个示例用一题虚构的高中物理计算题展示完整的输入输出路径，不包含真实学生数据。

## 五分钟能看到什么

| 步骤 | 文件 | 重点看什么 |
| --- | --- | --- |
| 1 | [`question.md`](question.md) | 原始主观题和分值分配 |
| 2 | [`answer-key.md`](answer-key.md) | 教师侧参考答案和计算过程 |
| 3 | [`generated-rubric.md`](generated-rubric.md) | 得分点、等价表达、零分规则、连带错误处理 |
| 4 | [`model-grading-prompt.md`](model-grading-prompt.md) | 要求结构化输出、复核标记和低置信度路由的模型提示词 |
| 5 | [`sample-student-answers.md`](sample-student-answers.md) | 三份虚构答卷：高分卷、部分得分卷、近似空白卷 |
| 6 | [`sample-grading-output.json`](sample-grading-output.json) | 三份答卷的结构化草评分 |
| 7 | [`review-queue.md`](review-queue.md) | 需要教师检查的复核队列 |
| 8 | [`teacher-report.md`](teacher-report.md) | 最终教学反馈报告 |

## 分数摘要

| 答卷编号 | 类型 | 草稿分数 | 复核建议 |
| --- | --- | ---: | --- |
| `paper-phy-001` | 高分卷 | 12 / 12 | 示例中不要求复核 |
| `paper-phy-002` | 部分得分卷 | 6 / 12 | 可抽查连带错误处理是否合理 |
| `paper-phy-003` | 近似空白 / 低置信度卷 | 0 / 12 | 需要教师复核 |

## 这个示例说明了什么

- 工作流从教师材料开始，让人工智能承担重复性草评分，而不是从一句模糊的“帮我打分”开始。
- 评分标准说明每个得分点如何给分、如何扣分。
- 模型提示词要求输出结构化结果、评分理由、置信度和复核标记。
- 低置信度卷在最终处理前会被分离出来。
- 教师报告会把阅卷证据转成教学反馈。

## 这个示例不声称什么

- 不向真实平台提交任何内容。
- 不使用真实答题图片或真实学生记录。
- 不声称人工智能可以在没有评分标准、复核节点和提交确认的情况下完成正式阅卷。
- 不替代平台适配、安全检查或教师确认。

## 用智能体试一下

把这个目录作为输入，并提出：

```text
Use $zhixue-marking-workflow with this demo folder.
检查评分标准、模型提示词、草评分、复核队列和教师报告是否一致。
不要提交任何内容。所有答卷都视为虚构示例。
```

---

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

- The workflow starts from teacher materials and lets AI handle repetitive draft scoring, instead of starting from a vague "grade this" request.
- The rubric explains what earns points and what does not.
- The model prompt asks for structured JSON, reasons, confidence, and review flags.
- Low-confidence cases are separated before final handling.
- The teacher report turns grading evidence into teaching feedback.

## What This Demo Does Not Claim

- It does not submit anything to a real platform.
- It does not use real answer images or real student records.
- It does not claim that AI should finalize official grading without a rubric, review checkpoints, and submission confirmation.
- It does not replace platform-specific safety checks or teacher confirmation.

## Try It With An Agent

Use these files as input and ask:

```text
Use $zhixue-marking-workflow with this demo folder.
Check whether the rubric, model prompt, sample grading output, review queue, and teacher report are consistent.
Do not submit anything. Treat all answers as fictional examples.
```
