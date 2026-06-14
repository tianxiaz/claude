# PERILL Scoring Reference

## Health Assessment (团队现状认知)

Based on team current score (团队全体现状均分):

| Score Range | Level | Description |
|-------------|-------|-------------|
| 4.0 - 5.0 | 高绩效 | 团队认为在此维度表现优秀 |
| 3.5 - 4.0 | 相对健康 | 团队认为基本正常，有优化空间 |
| 3.0 - 3.5 | 中等风险 | 团队认为存在明显问题，需关注 |
| 2.0 - 3.0 | 核心瓶颈 | 团队认为有严重问题，制约整体效能 |
| 1.0 - 2.0 | 危机 | 团队认为极度危险，需立即干预 |

## Blindspot Analysis (认知偏差)

Based on gap = team_current - stakeholder_current:

| Gap Range | Type | Description |
|-----------|------|-------------|
| > +0.5 | 认知盲区（高估） | 团队高估自身表现，可能忽视相关方意见 |
| -0.5 to +0.5 | 认知一致 | 团队内部状态在相关方面前充分暴露 |
| < -0.5 | 认知盲区（低估） | 团队低估自身表现，可能错失改善机会 |

Severity: |gap| > 1.0 = 严重, |gap| > 0.5 = 一般, else = 轻微

## Improvement Needs (提升需求)

Based on gap = expected - current (team):

| Gap Range | Level | Description |
|-----------|-------|-------------|
| > 1.5 | 极强 | 团队迫切希望大幅提升 |
| 1.0 - 1.5 | 强 | 团队有较高的提升期望 |
| 0.5 - 1.0 | 中等 | 适度提升空间 |
| < 0.5 | 弱 | 团队相对满意 |

## Team Health Summary Rules

Priority order for health assessment:
1. 严重盲区 (if |gap| > 1.0 and blindspot detected)
2. 危机 (if score 1.0-2.0)
3. 核心瓶颈 (if score 2.0-3.0)
4. 存在认知盲区 (if blindspot detected)
5. 中等风险 (if score 3.0-3.5)
6. Otherwise: use team awareness level

## Data Classification

**Team members**: Team Member + Team Leader roles
**Stakeholders**: Team Member + Team Leader + Stakeholder roles
**All respondents**: All role types including Sponsor
