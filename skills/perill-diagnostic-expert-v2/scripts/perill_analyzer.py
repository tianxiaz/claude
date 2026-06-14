#!/usr/bin/env python3
"""
PERILL Team Diagnostic Analyzer
Core analysis engine implementing 7-layer analysis framework
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np

# Dimension configuration
DIMENSIONS = {
    'P': {'name': 'Purpose and motivation', 'name_zh': '目的与动机', 'questions': list(range(1, 7))},
    'E': {'name': 'External system and process', 'name_zh': '外部系统与流程', 'questions': list(range(7, 13))},
    'R': {'name': 'Relationship', 'name_zh': '关系', 'questions': list(range(13, 19))},
    'I': {'name': 'Internal system and process', 'name_zh': '内部系统与流程', 'questions': list(range(19, 25))},
    'L': {'name': 'Learning', 'name_zh': '学习', 'questions': list(range(25, 31))},
    'Ld': {'name': 'Leadership', 'name_zh': '领导力', 'questions': list(range(31, 37))}
}

DIMENSION_ORDER = ['P', 'E', 'R', 'I', 'L', 'Ld']

# Health assessment thresholds
HEALTH_THRESHOLDS = [
    (4.0, 5.0, '高绩效', '团队认为在此维度表现优秀'),
    (3.5, 4.0, '相对健康', '团队认为基本正常，有优化空间'),
    (3.0, 3.5, '中等风险', '团队认为存在明显问题，需关注'),
    (2.0, 3.0, '核心瓶颈', '团队认为有严重问题，制约团队整体效能'),
    (1.0, 2.0, '危机', '团队认为极度危险，需立即干预')
]

# Gap assessment thresholds
GAP_THRESHOLDS = [
    (1.5, float('inf'), '极强', '团队迫切希望在此维度获得大幅提升'),
    (1.0, 1.5, '强', '团队对此维度有较高的提升期望'),
    (0.5, 1.0, '中等', '适度提升空间'),
    (0.0, 0.5, '弱', '团队对此维度相对满意')
]

# Blindspot thresholds
BLINDSPOT_THRESHOLDS = [
    (0.5, float('inf'), '认知盲区（高估）', '团队高估了自身表现，可能忽视相关方意见'),
    (-0.5, 0.5, '认知一致', '团队内部状态在相关方面前充分暴露'),
    (float('-inf'), -0.5, '认知盲区（低估）', '团队低估了自身表现，可能错失改善机会')
]

@dataclass
class AnalysisResult:
    """Container for complete PERILL analysis results"""
    # Layer 1: Data preparation
    question_scores: Dict  # 36 questions avg scores
    dimension_scores: Dict  # 6 dimensions avg scores
    # Layer 2: Individual perspective analysis
    perspective_analysis: Dict
    top_bottom_questions: Dict
    # Layer 3: Team awareness & blindspot
    team_awareness: Dict
    blindspot_analysis: Dict
    team_health: Dict
    # Layer 4: Gap analysis
    gap_analysis: Dict
    improvement_needs: Dict
    # Raw data for visualization
    raw_data: Dict


class PERILLAnalyzer:
    """Main analyzer class implementing the 7-layer PERILL analysis"""

    def __init__(self, excel_path: str, team_background_text: str = ""):
        self.excel_path = Path(excel_path)
        self.team_background = team_background_text
        self.df = None
        self.respondents = []
        self.respondent_roles = {}
        self.question_texts = {}
        self._load_data()

    def _load_data(self):
        """Load and parse PERILL Excel data"""
        self.df = pd.read_excel(self.excel_path, header=None)

        # Extract respondent info (rows 1-3, columns 4+)
        # Row 1 (index 1): names
        # Row 2 (index 2): roles
        # Row 3 (index 3): recorders
        names_row = self.df.iloc[1, 4:].values
        roles_row = self.df.iloc[2, 4:].values
        recorders_row = self.df.iloc[3, 4:].values

        self.respondents = []
        self.respondent_roles = {}
        self.respondent_recorders = {}

        for i, (name, role, recorder) in enumerate(zip(names_row, roles_row, recorders_row)):
            if pd.notna(name) and pd.notna(role):
                resp_id = f"resp_{i}"
                self.respondents.append({
                    'id': resp_id,
                    'name': str(name).strip(),
                    'role': str(role).strip(),
                    'recorder': str(recorder).strip() if pd.notna(recorder) else ''
                })
                self.respondent_roles[resp_id] = str(role).strip()
                self.respondent_recorders[resp_id] = str(recorder).strip() if pd.notna(recorder) else ''

        # Extract question texts (column 3, rows 5+)
        self.question_data = []
        row_idx = 5
        q_num = 1

        while row_idx < len(self.df):
            dim_cell = self.df.iloc[row_idx, 1]
            q_text_cell = self.df.iloc[row_idx, 2]

            if pd.isna(dim_cell) or pd.isna(q_text_cell):
                row_idx += 1
                continue

            dim_text = str(dim_cell).strip()
            q_text = str(q_text_cell).strip()

            # Extract English and Chinese parts
            dim_en = dim_text.split('\n')[0] if '\n' in dim_text else dim_text
            dim_zh = dim_text.split('\n')[1] if '\n' in dim_text else ''

            q_en = q_text.split('\n')[0] if '\n' in q_text else q_text
            q_zh = q_text.split('\n')[1] if '\n' in q_text else ''

            # Current state scores (row_idx, columns 4+)
            current_scores = []
            for i in range(len(self.respondents)):
                val = self.df.iloc[row_idx, 4 + i]
                if pd.notna(val):
                    try:
                        current_scores.append(float(val))
                    except:
                        current_scores.append(np.nan)
                else:
                    current_scores.append(np.nan)

            # Expected scores (row_idx + 1)
            expected_scores = []
            if row_idx + 1 < len(self.df):
                for i in range(len(self.respondents)):
                    val = self.df.iloc[row_idx + 1, 4 + i]
                    if pd.notna(val):
                        try:
                            expected_scores.append(float(val))
                        except:
                            expected_scores.append(np.nan)
                    else:
                        expected_scores.append(np.nan)

            self.question_data.append({
                'q_num': q_num,
                'dimension': self._get_dim_abbr(q_num),
                'dim_en': dim_en,
                'dim_zh': dim_zh,
                'q_en': q_en,
                'q_zh': q_zh,
                'current': current_scores,
                'expected': expected_scores
            })

            q_num += 1
            row_idx += 2  # Skip expected row

        print(f"Loaded {len(self.respondents)} respondents, {len(self.question_data)} questions")

    def _get_dim_abbr(self, q_num: int) -> str:
        """Get dimension abbreviation for question number"""
        for abbr, info in DIMENSIONS.items():
            if q_num in info['questions']:
                return abbr
        return 'P'

    def _get_team_members(self) -> List[str]:
        """Get IDs of team members (Team Member + Team Leader)"""
        return [r['id'] for r in self.respondents
                if r['role'] in ['Team Member', 'Team Leader']]

    def _get_stakeholders(self) -> List[str]:
        """Get IDs of stakeholders (Team Member + Team Leader + Stakeholder)"""
        return [r['id'] for r in self.respondents
                if r['role'] in ['Team Member', 'Team Leader', 'Stakeholder']]

    def _get_all_respondents(self) -> List[str]:
        """Get all respondent IDs"""
        return [r['id'] for r in self.respondents]

    def _calc_avg(self, scores: List[float]) -> float:
        """Calculate average, ignoring NaN"""
        valid = [s for s in scores if not np.isnan(s)]
        return np.mean(valid) if valid else 0.0

    # ==================== Layer 1: Data Preparation ====================

    def layer1_data_preparation(self) -> Dict:
        """Calculate average scores for questions and dimensions"""
        # Question-level scores
        question_scores = {}
        for q in self.question_data:
            q_num = q['q_num']
            team_indices = [i for i, r in enumerate(self.respondents)
                           if r['role'] in ['Team Member', 'Team Leader']]
            stakeholder_indices = [i for i, r in enumerate(self.respondents)
                                  if r['role'] in ['Team Member', 'Team Leader', 'Stakeholder']]
            all_indices = list(range(len(self.respondents)))

            q_scores = {
                'q_num': q_num,
                'dimension': q['dimension'],
                'dim_zh': q['dim_zh'],
                'q_en': q['q_en'],
                'q_zh': q['q_zh'],
                'current': {
                    'team': self._calc_avg([q['current'][i] for i in team_indices]),
                    'stakeholder': self._calc_avg([q['current'][i] for i in stakeholder_indices]),
                    'all': self._calc_avg([q['current'][i] for i in all_indices])
                },
                'expected': {
                    'team': self._calc_avg([q['expected'][i] for i in team_indices]),
                    'stakeholder': self._calc_avg([q['expected'][i] for i in stakeholder_indices]),
                    'all': self._calc_avg([q['expected'][i] for i in all_indices])
                }
            }
            question_scores[q_num] = q_scores

        # Dimension-level scores
        dimension_scores = {}
        for abbr in DIMENSION_ORDER:
            q_nums = DIMENSIONS[abbr]['questions']
            dim_current_team = []
            dim_current_stakeholder = []
            dim_current_all = []
            dim_expected_team = []
            dim_expected_stakeholder = []
            dim_expected_all = []

            for qn in q_nums:
                if qn in question_scores:
                    dim_current_team.append(question_scores[qn]['current']['team'])
                    dim_current_stakeholder.append(question_scores[qn]['current']['stakeholder'])
                    dim_current_all.append(question_scores[qn]['current']['all'])
                    dim_expected_team.append(question_scores[qn]['expected']['team'])
                    dim_expected_stakeholder.append(question_scores[qn]['expected']['stakeholder'])
                    dim_expected_all.append(question_scores[qn]['expected']['all'])

            dimension_scores[abbr] = {
                'abbr': abbr,
                'name': DIMENSIONS[abbr]['name'],
                'name_zh': DIMENSIONS[abbr]['name_zh'],
                'current': {
                    'team': self._calc_avg(dim_current_team),
                    'stakeholder': self._calc_avg(dim_current_stakeholder),
                    'all': self._calc_avg(dim_current_all)
                },
                'expected': {
                    'team': self._calc_avg(dim_expected_team),
                    'stakeholder': self._calc_avg(dim_expected_stakeholder),
                    'all': self._calc_avg(dim_expected_all)
                }
            }

        return {
            'question_scores': question_scores,
            'dimension_scores': dimension_scores
        }

    # ==================== Layer 2: Individual Perspective Analysis ====================

    def layer2_perspective_analysis(self, question_scores: Dict, dimension_scores: Dict) -> Dict:
        """Analyze differences between team members and stakeholders"""
        # Dimension-level comparison
        dim_comparison = []
        for abbr in DIMENSION_ORDER:
            ds = dimension_scores[abbr]
            dim_comparison.append({
                'dimension': abbr,
                'name_zh': ds['name_zh'],
                'team_current': round(ds['current']['team'], 2),
                'stakeholder_current': round(ds['current']['stakeholder'], 2),
                'difference': round(ds['current']['team'] - ds['current']['stakeholder'], 2)
            })

        # Top/bottom questions for team
        team_current_scores = [(q_num, qs['current']['team'], qs['q_zh'], qs['dimension'])
                               for q_num, qs in question_scores.items()]
        team_current_scores.sort(key=lambda x: x[1], reverse=True)
        team_top4 = team_current_scores[:4]
        team_bottom4 = team_current_scores[-4:]

        # Top/bottom questions for stakeholders
        sth_current_scores = [(q_num, qs['current']['stakeholder'], qs['q_zh'], qs['dimension'])
                              for q_num, qs in question_scores.items()]
        sth_current_scores.sort(key=lambda x: x[1], reverse=True)
        sth_top4 = sth_current_scores[:4]
        sth_bottom4 = sth_current_scores[-4:]

        return {
            'dimension_comparison': dim_comparison,
            'team_top4': [{'dimension': d[3], 'q_num': d[0], 'q_text': d[2], 'score': round(d[1], 2)} for d in team_top4],
            'team_bottom4': [{'dimension': d[3], 'q_num': d[0], 'q_text': d[2], 'score': round(d[1], 2)} for d in team_bottom4],
            'stakeholder_top4': [{'dimension': d[3], 'q_num': d[0], 'q_text': d[2], 'score': round(d[1], 2)} for d in sth_top4],
            'stakeholder_bottom4': [{'dimension': d[3], 'q_num': d[0], 'q_text': d[2], 'score': round(d[1], 2)} for d in sth_bottom4]
        }

    # ==================== Layer 3: Team Awareness & Blindspot ====================

    def layer3_blindspot_analysis(self, dimension_scores: Dict) -> Dict:
        """Analyze team awareness and cognitive blindspots"""
        awareness = {}
        blindspots = {}
        health = {}

        for abbr in DIMENSION_ORDER:
            ds = dimension_scores[abbr]
            team_current = ds['current']['team']
            sth_current = ds['current']['stakeholder']
            gap = team_current - sth_current

            # Team self-awareness
            level = None
            description = None
            for lo, hi, lvl, desc in HEALTH_THRESHOLDS:
                if lo <= team_current <= hi:
                    level = lvl
                    description = desc
                    break

            awareness[abbr] = {
                'score': round(team_current, 2),
                'level': level,
                'description': description
            }

            # Blindspot analysis
            blindspot_type = None
            blindspot_desc = None
            for lo, hi, btype, bdesc in BLINDSPOT_THRESHOLDS:
                if lo <= gap < hi or (gap >= lo and hi == float('inf')):
                    blindspot_type = btype
                    blindspot_desc = bdesc
                    break

            blindspots[abbr] = {
                'team_score': round(team_current, 2),
                'stakeholder_score': round(sth_current, 2),
                'gap': round(gap, 2),
                'blindspot_type': blindspot_type,
                'blindspot_desc': blindspot_desc,
                'severity': '严重' if abs(gap) > 1.0 else '一般' if abs(gap) > 0.5 else '轻微'
            }

            # Health summary
            priority_order = ['严重盲区', '危机', '核心瓶颈', '存在认知盲区', '中等风险']
            health_items = []
            if '盲区' in blindspot_type:
                health_items.append(f"存在认知盲区({blindspot_type.split('（')[1].replace('）','')})")
            health_items.append(level)

            # Select highest priority
            health_level = level
            for p in priority_order:
                if p in health_items or any(p in h for h in health_items):
                    health_level = p
                    break

            health[abbr] = {
                'assessment': health_level,
                'awareness_level': level,
                'blindspot': blindspot_type,
                'score': round(team_current, 2)
            }

        return {
            'awareness': awareness,
            'blindspots': blindspots,
            'health': health
        }

    # ==================== Layer 4: Gap Analysis ====================

    def layer4_gap_analysis(self, dimension_scores: Dict) -> Dict:
        """Analyze gap between current and expected"""
        gaps = {}
        improvements = {}

        for abbr in DIMENSION_ORDER:
            ds = dimension_scores[abbr]
            gap = ds['expected']['team'] - ds['current']['team']

            level = None
            desc = None
            for lo, hi, lvl, d in GAP_THRESHOLDS:
                if lo <= gap < hi or (gap >= lo and hi == float('inf')):
                    level = lvl
                    desc = d
                    break

            gaps[abbr] = {
                'current': round(ds['current']['team'], 2),
                'expected': round(ds['expected']['team'], 2),
                'gap': round(gap, 2),
                'level': level,
                'description': desc
            }

            # Improvement need analysis
            if gap > 1.0:
                interpretation = '团队强烈认知到自身在该维度存在瓶颈，非常期待提升和改变'
            elif gap > 0.5:
                interpretation = '团队认识到该维度有提升空间，期待适度改善'
            else:
                interpretation = '团队对该维度表现相对认同，但也可能缺乏提升信心'

            improvements[abbr] = {
                'gap': round(gap, 2),
                'level': level,
                'interpretation': interpretation
            }

        return {
            'gaps': gaps,
            'improvements': improvements
        }

    # ==================== Full Analysis Pipeline ====================

    def run_full_analysis(self) -> Dict:
        """Execute complete 7-layer analysis pipeline"""
        print("=" * 60)
        print("PERILL Team Diagnostic Analysis")
        print("=" * 60)

        # Layer 1
        print("\n[Layer 1] Data Preparation...")
        l1 = self.layer1_data_preparation()

        # Layer 2
        print("[Layer 2] Individual Perspective Analysis...")
        l2 = self.layer2_perspective_analysis(l1['question_scores'], l1['dimension_scores'])

        # Layer 3
        print("[Layer 3] Team Awareness & Blindspot Analysis...")
        l3 = self.layer3_blindspot_analysis(l1['dimension_scores'])

        # Layer 4
        print("[Layer 4] Gap Analysis...")
        l4 = self.layer4_gap_analysis(l1['dimension_scores'])

        # Build raw data for visualization
        raw_data = self._build_raw_data(l1, l2, l3, l4)

        result = {
            'layer1': l1,
            'layer2': l2,
            'layer3': l3,
            'layer4': l4,
            'raw_data': raw_data,
            'metadata': {
                'respondent_count': len(self.respondents),
                'respondents': [{'name': r['name'], 'role': r['role']} for r in self.respondents],
                'team_background': self.team_background
            }
        }

        print("\n✅ Analysis complete!")
        return result

    def _build_raw_data(self, l1, l2, l3, l4) -> Dict:
        """Build structured data for visualization"""
        ds = l1['dimension_scores']

        return {
            'dimension_current_team': [round(ds[d]['current']['team'], 2) for d in DIMENSION_ORDER],
            'dimension_current_stakeholder': [round(ds[d]['current']['stakeholder'], 2) for d in DIMENSION_ORDER],
            'dimension_expected_team': [round(ds[d]['expected']['team'], 2) for d in DIMENSION_ORDER],
            'dimension_labels': [f"{d}({DIMENSIONS[d]['name_zh']})" for d in DIMENSION_ORDER],
            'dimension_abbrs': DIMENSION_ORDER,
            'health_scores': [l3['health'][d]['assessment'] for d in DIMENSION_ORDER],
            'blindspot_gaps': [l3['blindspots'][d]['gap'] for d in DIMENSION_ORDER],
            'improvement_gaps': [l4['gaps'][d]['gap'] for d in DIMENSION_ORDER],
            'respondent_matrix': self._build_respondent_matrix(),
            'question_scores_table': self._build_question_table(l1['question_scores'])
        }

    def _build_respondent_matrix(self) -> List[Dict]:
        """Build individual respondent scoring matrix"""
        matrix = []
        for resp in self.respondents:
            resp_scores = {}
            for abbr in DIMENSION_ORDER:
                q_nums = DIMENSIONS[abbr]['questions']
                scores = []
                for q in self.question_data:
                    if q['q_num'] in q_nums:
                        idx = self.respondents.index(resp)
                        if idx < len(q['current']) and not np.isnan(q['current'][idx]):
                            scores.append(q['current'][idx])
                resp_scores[abbr] = round(np.mean(scores), 2) if scores else 0
            matrix.append({
                'name': resp['name'],
                'role': resp['role'],
                'scores': resp_scores
            })
        return matrix

    def _build_question_table(self, question_scores: Dict) -> List[Dict]:
        """Build flat question scores table"""
        table = []
        for q_num in sorted(question_scores.keys()):
            qs = question_scores[q_num]
            table.append({
                'q_num': q_num,
                'dimension': qs['dimension'],
                'q_zh': qs['q_zh'],
                'current_team': round(qs['current']['team'], 2),
                'current_stakeholder': round(qs['current']['stakeholder'], 2),
                'current_all': round(qs['current']['all'], 2),
                'expected_team': round(qs['expected']['team'], 2),
                'expected_stakeholder': round(qs['expected']['stakeholder'], 2),
                'expected_all': round(qs['expected']['all'], 2)
            })
        return table

    def export_json(self, result: Dict, output_path: str):
        """Export analysis results to JSON"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to JSON-serializable format
        def serialize(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [serialize(i) for i in obj]
            return obj

        serialized = serialize(result)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serialized, f, ensure_ascii=False, indent=2)

        print(f"\n📁 Results exported to: {output_path}")
        return output_path


def main():
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("Usage: python perill_analyzer.py <excel_path> <output_json_path> [team_background_text]")
        sys.exit(1)

    excel_path = sys.argv[1]
    output_path = sys.argv[2]
    team_background = sys.argv[3] if len(sys.argv) > 3 else ""

    analyzer = PERILLAnalyzer(excel_path, team_background)
    result = analyzer.run_full_analysis()
    analyzer.export_json(result, output_path)


if __name__ == '__main__':
    main()
