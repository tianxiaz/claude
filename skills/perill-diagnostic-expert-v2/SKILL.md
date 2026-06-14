---
name: perill-diagnostic-expert-v2
description: "PERILL Team Diagnostic Analysis — A comprehensive 7-layer team coaching assessment framework. Analyzes team questionnaire data across 6 dimensions (Purpose, External Systems, Relationships, Internal Systems, Learning, Leadership) to generate diagnostic reports with interactive visualizations and intervention recommendations. Use when: (1) Analyzing PERILL team assessment questionnaire data, (2) Generating team coaching diagnostic reports, (3) Evaluating team performance across multiple systemic dimensions, (4) Identifying team blindspots and improvement needs, (5) Designing team coaching intervention strategies. Supports Excel input with 36 questions scored 1-5, generates Word reports and interactive HTML charts."
---

# PERILL Team Diagnostic Skill

## Overview

PERILL is a 6-dimensional team diagnostic model (Purpose, External Systems, Relationships, Internal Systems, Learning, Leadership) based on 20 years of team performance research. This skill implements a 7-layer analysis framework to process questionnaire data and produce comprehensive diagnostic reports.

## Input Requirements

| Data | Format | Description |
|------|--------|-------------|
| Questionnaire data | Excel (.xlsx) | 36 questions x respondents, current + expected scores (1-5) |
| Respondent info | In Excel | Name, role (Team Member/Leader/Stakeholder/Sponsor) |
| Team background | Text/PDF | Team history, challenges, composition |

**36 Question Dimensions:**
- P (Q1-6): Purpose and motivation
- E (Q7-12): External system and process
- R (Q13-18): Relationship
- I (Q19-24): Internal system and process
- L (Q25-30): Learning
- Ld (Q31-36): Leadership

## Workflow

### Step 1: Data Analysis
Run `scripts/perill_analyzer.py <excel_path> <output_json> [team_background]`

This executes Layers 1-4 analysis:
- **Layer 1**: Calculate dimension/question averages (team/stakeholder/all)
- **Layer 2**: Individual perspective difference analysis
- **Layer 3**: Team awareness assessment & blindspot identification
- **Layer 4**: Gap analysis (current vs expected)

Output: JSON file with all computed scores and analysis results.

### Step 2: Generate Visualizations
Run `scripts/perill_visualizer.py <analysis_json>`

Generates 7 interactive HTML charts in `charts/` subdirectory:
1. `radar_current_vs_expected.html` — 6D current vs expected radar
2. `radar_team_vs_stakeholder.html` — Team self vs stakeholder assessment
3. `gap_analysis.html` — Current-expected gap analysis
4. `blindspot_analysis.html` — Cognitive blindspot visualization
5. `respondent_heatmap.html` — Individual respondent scoring heatmap
6. `system_network.html` — Dimension interconnection network

**Note:** The bar chart (`bar_dimension_scores.html`) is generated but should NOT be included in the Word report - it is redundant with the radar chart.

### Step 3: Qualitative Analysis + Word Report Generation

Run `scripts/generate_report.py <analysis_json> [team_background]`

This consolidated step performs:
- **Layer 5**: Six-dimension deep diagnosis (all 6 dimensions in ONE AI call)
- **Layer 6**: Systemic interconnection analysis (all pairs + causal cycles in ONE AI call)
- **Layer 7**: Intervention design (phases + outcomes in ONE AI call)
- **Word Document**: Complete report generation with embedded analysis

**Two modes:**
1. `--analyze`: Run AI qualitative analysis only (Layers 5-7), saves to `qualitative_analysis.json`
2. `--generate`: Generate Word document from existing `qualitative_analysis.json`

**Recommended workflow:**
```bash
# Run analysis + generate document in one go
python scripts/generate_report.py --analyze output.json "team background..."
python scripts/generate_report.py --generate output.json "team background..."
```

**Report structure follows `references/report-structure.md`:**

- Section 1: Diagnostic Overview with embedded radar/gap charts
- Section 2: Six-Dimension Deep Diagnosis (advantage/problem analysis per dimension)
- Section 3: Systemic Interconnection Analysis with network diagram
- Section 4: Intervention Path Design with phase table
- Section 5: Appendices with heatmap

**Key requirements:**
- Section 1.3 & 4.1: Identical 3-sentence core diagnostic conclusion
- Section 2: Must include BOTH background AND questionnaire evidence
- Section 3.1: Flowing prose format for interconnections
- Section 3.2/3.3: ONLY PERILL dimension abbreviations (no question numbers)
- Section 4.3: Phase goals focus on TEAM AS A SYSTEM (not individual leader)
- Figure order (6 figures, NO bar chart): Radar CE→Radar TS→Gap→Blindspot→Network→Heatmap

## Scoring Reference

**Health Levels** (current score):
| Range | Level |
|-------|-------|
| 4.0-5.0 | 高绩效 |
| 3.5-4.0 | 相对健康 |
| 3.0-3.5 | 中等风险 |
| 2.0-3.0 | 核心瓶颈 |
| 1.0-2.0 | 危机 |

**Blindspot Thresholds** (team - stakeholder):
| Gap | Type |
|-----|------|
| >+0.5 | 认知盲区（高估） |
| -0.5 to +0.5 | 认知一致 |
| <-0.5 | 认知盲区（低估） |

**Improvement Needs** (expected - current):
| Gap | Level |
|-----|-------|
| >1.5 | 极强 |
| 1.0-1.5 | 强 |
| 0.5-1.0 | 中等 |
| <0.5 | 弱 |

## Color Scheme

| Element | Hex |
|---------|-----|
| Current state | #E15759 |
| Expected state | #4E79A7 |
| Healthy/high | #59A14F |
| Medium | #F28E2B |
| Risk/low | #E15759 |

## Key Scripts

- `scripts/perill_analyzer.py` — Core analysis engine (Layers 1-4)
- `scripts/perill_visualizer.py` — Interactive chart generator (HTML)
- `scripts/generate_report.py` — Qualitative analysis + Word report generator

### generate_report.py Usage

```bash
# Step 1: Run AI qualitative analysis (Layers 5-7)
python scripts/generate_report.py --analyze output.json "team background text"

# Step 2: Generate Word document
python scripts/generate_report.py --generate output.json "team background text"
```

The script reads API credentials from `config.json` (api_key, api_base).

## References

- `references/perill-model.md` — Full PERILL model documentation
- `references/scoring-reference.md` — Detailed scoring criteria
- `references/report-structure.md` — **Complete report template and structure with all requirements**