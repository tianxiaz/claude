#!/usr/bin/env python3
"""
PERILL Team Diagnostic Visualizer
Generate interactive HTML charts for PERILL analysis
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# Color scheme per methodology doc
COLORS = {
    'current': '#E15759',      # Red for current state
    'expected': '#4E79A7',     # Blue for expected
    'healthy': '#59A14F',      # Green for healthy/high
    'medium': '#F28E2B',       # Orange for medium
    'risk': '#E15759',         # Red for risk/low
    'background': '#FFFFFF',
    'grid': '#E5E5E5',
    'text': '#333333'
}

DIMENSION_ORDER = ['P', 'E', 'R', 'I', 'L', 'Ld']
DIMENSION_NAMES = {
    'P': '目的与动机',
    'E': '外部系统与流程',
    'R': '关系',
    'I': '内部系统与流程',
    'L': '学习',
    'Ld': '领导力'
}


class PERILLVisualizer:
    """Generate interactive visualizations for PERILL analysis"""

    def __init__(self, analysis_json_path: str):
        with open(analysis_json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.raw = self.data['raw_data']
        self.output_dir = Path(analysis_json_path).parent / 'charts'
        self.output_dir.mkdir(exist_ok=True)

    # ==================== Chart 1: Radar - Current vs Expected ====================

    def radar_current_vs_expected(self) -> str:
        """Radar chart: team current vs expected scores"""
        labels = [f"{d}({DIMENSION_NAMES[d]})" for d in DIMENSION_ORDER]
        current = self.raw['dimension_current_team']
        expected = self.raw['dimension_expected_team']

        # Close the radar
        labels_closed = labels + [labels[0]]
        current_closed = current + [current[0]]
        expected_closed = expected + [expected[0]]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=current_closed,
            theta=labels_closed,
            fill='toself',
            name='团队现状',
            line_color=COLORS['current'],
            fillcolor='rgba(225, 87, 89, 0.2)'
        ))

        fig.add_trace(go.Scatterpolar(
            r=expected_closed,
            theta=labels_closed,
            fill='toself',
            name='一年后期待',
            line_color=COLORS['expected'],
            fillcolor='rgba(78, 121, 167, 0.2)'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    dtick=1,
                    gridcolor=COLORS['grid']
                ),
                bgcolor='white'
            ),
            title=dict(
                text='PERILL六维诊断雷达图<br><sub>团队现状 vs 一年后期待</sub>',
                font=dict(size=18)
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.15,
                xanchor='center',
                x=0.5
            ),
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', color=COLORS['text']),
            width=700,
            height=600
        )

        output_path = self.output_dir / 'radar_current_vs_expected.html'
        fig.write_html(str(output_path))
        return str(output_path)

    # ==================== Chart 2: Radar - Team vs Stakeholder ====================

    def radar_team_vs_stakeholder(self) -> str:
        """Radar chart: team self vs stakeholder assessment"""
        labels = [f"{d}({DIMENSION_NAMES[d]})" for d in DIMENSION_ORDER]
        team = self.raw['dimension_current_team']
        stakeholder = self.raw['dimension_current_stakeholder']

        labels_closed = labels + [labels[0]]
        team_closed = team + [team[0]]
        stakeholder_closed = stakeholder + [stakeholder[0]]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=team_closed,
            theta=labels_closed,
            fill='toself',
            name='团队自评',
            line_color=COLORS['current'],
            fillcolor='rgba(225, 87, 89, 0.2)'
        ))

        fig.add_trace(go.Scatterpolar(
            r=stakeholder_closed,
            theta=labels_closed,
            fill='toself',
            name='相关方他评',
            line_color=COLORS['healthy'],
            fillcolor='rgba(89, 161, 79, 0.2)'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    dtick=1,
                    gridcolor=COLORS['grid']
                ),
                bgcolor='white'
            ),
            title=dict(
                text='PERILL六维认知差异雷达图<br><sub>团队自评 vs 相关方他评</sub>',
                font=dict(size=18)
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.15,
                xanchor='center',
                x=0.5
            ),
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', color=COLORS['text']),
            width=700,
            height=600
        )

        output_path = self.output_dir / 'radar_team_vs_stakeholder.html'
        fig.write_html(str(output_path))
        return str(output_path)

    # ==================== Chart 3: Bar - Dimension Scores ====================

    def bar_dimension_scores(self) -> str:
        """Bar chart: all dimension scores comparison"""
        labels = [DIMENSION_NAMES[d] for d in DIMENSION_ORDER]
        team_current = self.raw['dimension_current_team']
        stakeholder_current = self.raw['dimension_current_stakeholder']
        expected = self.raw['dimension_expected_team']

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='团队现状',
            x=labels,
            y=team_current,
            marker_color=COLORS['current']
        ))

        fig.add_trace(go.Bar(
            name='相关方现状',
            x=labels,
            y=stakeholder_current,
            marker_color=COLORS['healthy']
        ))

        fig.add_trace(go.Bar(
            name='一年后期待',
            x=labels,
            y=expected,
            marker_color=COLORS['expected']
        ))

        fig.update_layout(
            title=dict(
                text='PERILL各维度得分对比',
                font=dict(size=18)
            ),
            xaxis_title='维度',
            yaxis_title='得分',
            yaxis=dict(range=[0, 5.5], dtick=1),
            barmode='group',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family='Arial, sans-serif', color=COLORS['text']),
            width=800,
            height=500
        )

        fig.update_xaxes(gridcolor=COLORS['grid'])
        fig.update_yaxes(gridcolor=COLORS['grid'])

        output_path = self.output_dir / 'bar_dimension_scores.html'
        fig.write_html(str(output_path))
        return str(output_path)

    # ==================== Chart 4: Gap Analysis ====================

    def gap_analysis_chart(self) -> str:
        """Bar chart: gap between current and expected"""
        labels = [DIMENSION_NAMES[d] for d in DIMENSION_ORDER]
        gaps = self.raw['improvement_gaps']

        # Color bars by gap magnitude
        bar_colors = []
        for gap in gaps:
            if gap > 1.5:
                bar_colors.append('#8B0000')  # Dark red
            elif gap > 1.0:
                bar_colors.append(COLORS['risk'])
            elif gap > 0.5:
                bar_colors.append(COLORS['medium'])
            else:
                bar_colors.append(COLORS['healthy'])

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=labels,
            y=gaps,
            marker_color=bar_colors,
            text=[f'{g:.2f}' for g in gaps],
            textposition='outside'
        ))

        # Add threshold lines
        fig.add_hline(y=1.5, line_dash="dash", line_color="#8B0000",
                      annotation_text="极强", annotation_position="right")
        fig.add_hline(y=1.0, line_dash="dash", line_color=COLORS['risk'],
                      annotation_text="强", annotation_position="right")
        fig.add_hline(y=0.5, line_dash="dash", line_color=COLORS['medium'],
                      annotation_text="中等", annotation_position="right")

        fig.update_layout(
            title=dict(
                text='现状-期待差距分析',
                font=dict(size=18)
            ),
            xaxis_title='维度',
            yaxis_title='提升需求（期待-现状）',
            yaxis=dict(range=[0, max(gaps) + 0.5]),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family='Arial, sans-serif', color=COLORS['text']),
            showlegend=False,
            width=800,
            height=500
        )

        fig.update_xaxes(gridcolor=COLORS['grid'])
        fig.update_yaxes(gridcolor=COLORS['grid'])

        output_path = self.output_dir / 'gap_analysis.html'
        fig.write_html(str(output_path))
        return str(output_path)

    # ==================== Chart 5: Blindspot Analysis ====================

    def blindspot_chart(self) -> str:
        """Bar chart: blindspot gaps"""
        labels = [DIMENSION_NAMES[d] for d in DIMENSION_ORDER]
        blindspot_gaps = self.raw['blindspot_gaps']

        bar_colors = []
        for gap in blindspot_gaps:
            if abs(gap) > 1.0:
                bar_colors.append('#8B0000')
            elif abs(gap) > 0.5:
                bar_colors.append(COLORS['risk'])
            else:
                bar_colors.append(COLORS['healthy'])

        fig = go.Figure()

        colors_pos = ['rgba(225,87,89,0.8)' if g > 0 else 'rgba(89,161,79,0.8)' for g in blindspot_gaps]

        fig.add_trace(go.Bar(
            x=labels,
            y=blindspot_gaps,
            marker_color=colors_pos,
            text=[f'{g:+.2f}' for g in blindspot_gaps],
            textposition='outside'
        ))

        fig.add_hline(y=0, line_color='#333333', line_width=1)
        fig.add_hline(y=0.5, line_dash="dash", line_color=COLORS['risk'])
        fig.add_hline(y=-0.5, line_dash="dash", line_color=COLORS['risk'])

        fig.update_layout(
            title=dict(
                text='认知偏差分析（团队自评 - 相关方他评）',
                font=dict(size=18)
            ),
            xaxis_title='维度',
            yaxis_title='认知偏差',
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family='Arial, sans-serif', color=COLORS['text']),
            showlegend=False,
            width=800,
            height=500
        )

        fig.update_xaxes(gridcolor=COLORS['grid'])
        fig.update_yaxes(gridcolor=COLORS['grid'])

        output_path = self.output_dir / 'blindspot_analysis.html'
        fig.write_html(str(output_path))
        return str(output_path)

    # ==================== Chart 6: Respondent Heatmap ====================

    def respondent_heatmap(self) -> str:
        """Heatmap: individual respondent scores by dimension"""
        matrix = self.raw['respondent_matrix']

        names = [m['name'] + f"\n({m['role'][:3]})" for m in matrix]
        dims = [DIMENSION_NAMES[d] for d in DIMENSION_ORDER]

        z_data = []
        for m in matrix:
            row = [m['scores'][d] for d in DIMENSION_ORDER]
            z_data.append(row)

        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=dims,
            y=names,
            colorscale=[
                [0, '#E15759'],
                [0.25, '#F28E2B'],
                [0.5, '#FCE38A'],
                [0.75, '#B8E1A8'],
                [1, '#59A14F']
            ],
            zmin=1,
            zmax=5,
            text=[[f'{v:.1f}' for v in row] for row in z_data],
            texttemplate='%{text}',
            textfont=dict(size=12),
            colorbar=dict(title='得分')
        ))

        fig.update_layout(
            title=dict(
                text='答卷人六维评分热力图',
                font=dict(size=18)
            ),
            xaxis_title='维度',
            yaxis_title='答卷人',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', color=COLORS['text']),
            width=700,
            height=400 + len(matrix) * 40
        )

        output_path = self.output_dir / 'respondent_heatmap.html'
        fig.write_html(str(output_path))
        return str(output_path)

    # ==================== Chart 7: System Network ====================

    def system_network_chart(self) -> str:
        """Network diagram: dimension interconnections"""
        labels = [f"{d}<br>{DIMENSION_NAMES[d]}" for d in DIMENSION_ORDER]
        team_scores = self.raw['dimension_current_team']

        # Calculate positions (hexagon)
        import math
        positions = []
        for i in range(6):
            angle = math.pi / 2 - i * math.pi / 3
            r = 1 + (5 - team_scores[i]) * 0.15
            positions.append((r * math.cos(angle), r * math.sin(angle)))

        fig = go.Figure()

        # Draw connections based on score correlations
        node_colors = []
        for s in team_scores:
            if s >= 4.0:
                node_colors.append(COLORS['healthy'])
            elif s >= 3.0:
                node_colors.append(COLORS['medium'])
            else:
                node_colors.append(COLORS['risk'])

        # Draw edges
        for i in range(6):
            for j in range(i + 1, 6):
                # Connection strength based on score similarity
                similarity = 1 - abs(team_scores[i] - team_scores[j]) / 4.0
                if similarity > 0.3:
                    fig.add_trace(go.Scatter(
                        x=[positions[i][0], positions[j][0]],
                        y=[positions[i][1], positions[j][1]],
                        mode='lines',
                        line=dict(
                            color=f'rgba(150,150,150,{similarity * 0.5})',
                            width=similarity * 3
                        ),
                        showlegend=False,
                        hoverinfo='skip'
                    ))

        # Draw nodes
        fig.add_trace(go.Scatter(
            x=[p[0] for p in positions],
            y=[p[1] for p in positions],
            mode='markers+text',
            marker=dict(
                size=[40 + (5 - s) * 8 for s in team_scores],
                color=node_colors,
                line=dict(color='white', width=2)
            ),
            text=labels,
            textposition='middle center',
            textfont=dict(size=10, color='white', family='Arial Black'),
            showlegend=False,
            hovertemplate='%{text}<br>得分: %{customdata:.2f}<extra></extra>',
            customdata=team_scores
        ))

        # Add score labels below
        for i, (pos, score) in enumerate(zip(positions, team_scores)):
            fig.add_annotation(
                x=pos[0],
                y=pos[1] - 0.35,
                text=f'{score:.2f}',
                showarrow=False,
                font=dict(size=12, color=node_colors[i], family='Arial Black')
            )

        fig.update_layout(
            title=dict(
                text='PERILL系统因果网络图<br><sub>节点大小=提升需求，颜色=健康度</sub>',
                font=dict(size=18)
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family='Arial, sans-serif', color=COLORS['text']),
            showlegend=False,
            width=700,
            height=700,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            margin=dict(l=50, r=50, t=100, b=50)
        )

        output_path = self.output_dir / 'system_network.html'
        fig.write_html(str(output_path))
        return str(output_path)

    # ==================== Generate All Charts ====================

    def generate_all_charts(self) -> List[str]:
        """Generate all visualization charts"""
        print("\n" + "=" * 60)
        print("Generating Interactive Visualizations")
        print("=" * 60)

        charts = []

        print("[1/7] Radar: Current vs Expected...")
        charts.append(self.radar_current_vs_expected())

        print("[2/7] Radar: Team vs Stakeholder...")
        charts.append(self.radar_team_vs_stakeholder())

        print("[3/7] Bar: Dimension Scores...")
        charts.append(self.bar_dimension_scores())

        print("[4/7] Gap Analysis...")
        charts.append(self.gap_analysis_chart())

        print("[5/7] Blindspot Analysis...")
        charts.append(self.blindspot_chart())

        print("[6/7] Respondent Heatmap...")
        charts.append(self.respondent_heatmap())

        print("[7/7] System Network...")
        charts.append(self.system_network_chart())

        print(f"\n✅ All {len(charts)} charts generated in: {self.output_dir}")
        return charts


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python perill_visualizer.py <analysis_json_path>")
        sys.exit(1)

    analysis_path = sys.argv[1]
    viz = PERILLVisualizer(analysis_path)
    viz.generate_all_charts()


if __name__ == '__main__':
    main()
