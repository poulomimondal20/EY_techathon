"""
ESG Report PDF Generator - Compact Professional Design
Creates dense, content-rich PDF reports with minimal whitespace
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
import os

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
        KeepTogether, CondPageBreak
    )
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not installed. Install with: pip install reportlab")


class Colors:
    PRIMARY = colors.HexColor('#0D47A1')
    SECONDARY = colors.HexColor('#1565C0')
    SUCCESS = colors.HexColor('#2E7D32')
    WARNING = colors.HexColor('#F57C00')
    DANGER = colors.HexColor('#C62828')
    DARK = colors.HexColor('#1A1A2E')
    LIGHT_BG = colors.HexColor('#F5F7FA')
    WHITE = colors.white
    TEXT = colors.HexColor('#212121')
    TEXT_MUTED = colors.HexColor('#616161')
    BORDER = colors.HexColor('#E0E0E0')
    ENV = colors.HexColor('#2E7D32')
    SOCIAL = colors.HexColor('#1565C0')
    GOV = colors.HexColor('#6A1B9A')


class ESGReportPDFGenerator:
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self._setup_styles()
    
    def _setup_styles(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle('ESGBody', fontSize=9, leading=11, alignment=TA_JUSTIFY, spaceAfter=4))
        self.styles.add(ParagraphStyle('ESGSmall', fontSize=8, leading=10, alignment=TA_JUSTIFY, spaceAfter=3))
        self.styles.add(ParagraphStyle('ESGTiny', fontSize=7, leading=9, spaceAfter=2))
    
    def _clean(self, text: str) -> str:
        if not text:
            return ""
        text = str(text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        for old, new in [('•', '-'), ('–', '-'), ('—', '-'), ('"', '"'), ('"', '"'), (''', "'"), (''', "'"), ('…', '...')]:
            text = text.replace(old, new)
        text = text.replace('&', '&amp;')
        text = re.sub(r'<(?!/?[bi]>)', '&lt;', text)
        text = re.sub(r'(?<![bi])>', '&gt;', text)
        return text
    
    def _s(self, val) -> str:
        if val is None:
            return ""
        if isinstance(val, str):
            return self._clean(val)
        if isinstance(val, list):
            return self._clean(", ".join(str(x) for x in val))
        if isinstance(val, dict):
            return self._clean(" | ".join(f"{k}: {v}" for k, v in val.items() if not isinstance(v, (dict, list))))
        return self._clean(str(val))
    
    def generate_pdf(self, company_name: str, report_data: Dict[str, Any], 
                     industry: Optional[str] = None, output_filename: Optional[str] = None) -> str:
        if not REPORTLAB_AVAILABLE:
            return self._fallback_html(company_name, report_data, industry)
        
        if not output_filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe = company_name.replace(' ', '_').replace('&', 'and')
            output_filename = f"ESG_Report_{safe}_{ts}.pdf"
        
        path = os.path.join(self.output_dir, output_filename)
        doc = SimpleDocTemplate(path, pagesize=letter, rightMargin=0.5*inch, leftMargin=0.5*inch,
                               topMargin=0.4*inch, bottomMargin=0.4*inch)
        
        story = self._build(company_name, report_data, industry)
        doc.build(story, onFirstPage=self._page_footer, onLaterPages=self._page_footer)
        print(f"PDF generated: {path}")
        return path
    
    def _page_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(Colors.TEXT_MUTED)
        canvas.drawCentredString(letter[0]/2, 0.25*inch, f"Page {doc.page}")
        canvas.restoreState()
    
    def _build(self, company: str, data: Dict, industry: Optional[str]) -> List:
        story = []
        rj = self._parse_json(data.get('report', '{}'))
        sc = data.get('calculated_scores', {})
        overall, env, soc, gov = [float(sc.get(k, 0)) for k in ['overall_score', 'environmental_score', 'social_score', 'governance_score']]
        env_det = data.get('env_detailed_analysis', '')
        soc_det = data.get('social_detailed_analysis', '')
        gov_det = data.get('gov_detailed_analysis', '')
        
        # === HEADER ===
        story.append(self._header_banner())
        story.append(Spacer(1, 0.15*inch))
        story.append(self._company_info(company, industry))
        story.append(Spacer(1, 0.15*inch))
        story.append(self._scores_table(overall, env, soc, gov))
        story.append(Spacer(1, 0.2*inch))
        
        # Debug: Check if risks/recommendations parsed
        print(f"   DEBUG: Parsed JSON keys: {list(rj.keys())}")
        print(f"   DEBUG: material_risks count: {len(rj.get('material_risks', []))}")
        print(f"   DEBUG: opportunities count: {len(rj.get('opportunities', []))}")
        print(f"   DEBUG: recommendations count: {len(rj.get('recommendations', []))}")
        
        # === EXECUTIVE SUMMARY ===
        story.append(self._section("EXECUTIVE SUMMARY", Colors.PRIMARY))
        if rj.get('executive_summary'):
            story.append(Paragraph(self._s(rj['executive_summary']), self.styles['ESGBody']))
        if rj.get('company_profile'):
            story.append(Spacer(1, 0.08*inch))
            story.append(Paragraph(f"<b>Company Profile:</b> {self._s(rj['company_profile'])}", self.styles['ESGSmall']))
        story.append(Spacer(1, 0.15*inch))
        
        # === ENVIRONMENTAL ===
        story.append(CondPageBreak(1.5*inch))
        story.extend(self._pillar_section("ENVIRONMENTAL ANALYSIS", Colors.ENV, env, 
                                          rj.get('environmental_analysis', {}), env_det,
                                          ['emissions', 'energy', 'water', 'waste', 'climate_risks']))
        
        # === SOCIAL ===
        story.append(CondPageBreak(1.5*inch))
        story.extend(self._pillar_section("SOCIAL ANALYSIS", Colors.SOCIAL, soc,
                                          rj.get('social_analysis', {}), soc_det,
                                          ['diversity', 'employee_experience', 'health_safety', 'compensation', 'community', 'supply_chain']))
        
        # === GOVERNANCE ===
        story.append(CondPageBreak(1.5*inch))
        story.extend(self._pillar_section("GOVERNANCE ANALYSIS", Colors.GOV, gov,
                                          rj.get('governance_analysis', {}), gov_det,
                                          ['board', 'compensation', 'ethics_compliance', 'risk_management', 'transparency']))
        
        # === RISKS ===
        story.append(CondPageBreak(1.5*inch))
        story.extend(self._risks_section(rj.get('material_risks', [])))
        
        # === OPPORTUNITIES ===
        story.append(CondPageBreak(1*inch))
        story.extend(self._opportunities_section(rj.get('opportunities', [])))
        
        # === RECOMMENDATIONS ===
        story.append(CondPageBreak(1.5*inch))
        story.extend(self._recommendations_section(rj.get('recommendations', [])))
        
        # === PEER COMPARISON ===
        if rj.get('peer_comparison'):
            story.append(CondPageBreak(1*inch))
            story.append(self._section("PEER COMPARISON", Colors.SECONDARY))
            story.append(Paragraph(self._s(rj['peer_comparison']), self.styles['ESGBody']))
            story.append(Spacer(1, 0.1*inch))
        
        # === CONCLUSION ===
        if rj.get('conclusion'):
            story.append(CondPageBreak(1*inch))
            story.append(self._section("CONCLUSION & OUTLOOK", Colors.DARK))
            cbox = Table([[Paragraph(self._s(rj['conclusion']), self.styles['ESGBody'])]], colWidths=[7.1*inch])
            cbox.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#E3F2FD')),
                ('BOX', (0,0), (-1,-1), 1, Colors.PRIMARY),
                ('PADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(cbox)
        
        # Footer
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f'<font size="6" color="#999">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | ESG Report Generator</font>',
                              ParagraphStyle('ft', alignment=TA_CENTER)))
        return story
    
    def _header_banner(self):
        t = Table([[Paragraph('<font color="white" size="18"><b>ESG ASSESSMENT REPORT</b></font>', 
                             ParagraphStyle('hb', alignment=TA_CENTER))]], colWidths=[7.1*inch])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), Colors.DARK), ('PADDING', (0,0), (-1,-1), 12)]))
        return t
    
    def _company_info(self, company, industry):
        """Company name and industry as a separate clean row"""
        t = Table([[Paragraph(f'<font size="16" color="#0D47A1"><b>{company}</b></font>', self.styles['Normal']),
                   Paragraph(f'<font size="10" color="#666">{industry or "N/A"}</font>', ParagraphStyle('ind', alignment=TA_RIGHT)),
                   Paragraph(f'<font size="10" color="#666">{datetime.now().strftime("%B %Y")}</font>', ParagraphStyle('dt', alignment=TA_RIGHT))]], 
                  colWidths=[4.5*inch, 1.5*inch, 1.1*inch])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), Colors.LIGHT_BG), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                               ('PADDING', (0,0), (-1,-1), 10), ('BOX', (0,0), (-1,-1), 1, Colors.BORDER)]))
        return t
    
    def _scores_table(self, overall, env, soc, gov):
        rows = [[Paragraph(f'<b>{h}</b>', self.styles['ESGTiny']) for h in ['Pillar', 'Score', 'Rating', 'Performance']]]
        for name, val in [("Overall ESG", overall), ("Environmental", env), ("Social", soc), ("Governance", gov)]:
            c = self._sc(val)
            bar = f'<font color="{c}">{"█"*int(val/5)}</font><font color="#E0E0E0">{"░"*(20-int(val/5))}</font>'
            rows.append([Paragraph(f'<b>{name}</b>', self.styles['ESGTiny']),
                        Paragraph(f'<font color="{c}"><b>{val:.0f}/100</b></font>', self.styles['ESGTiny']),
                        Paragraph(f'<font color="{c}">{self._rating(val)}</font>', self.styles['ESGTiny']),
                        Paragraph(bar, self.styles['ESGTiny'])])
        t = Table(rows, colWidths=[1.3*inch, 0.8*inch, 0.8*inch, 4.2*inch])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), Colors.PRIMARY), ('TEXTCOLOR', (0,0), (-1,0), Colors.WHITE),
                               ('GRID', (0,0), (-1,-1), 0.5, Colors.BORDER), ('PADDING', (0,0), (-1,-1), 4),
                               ('ROWBACKGROUNDS', (0,1), (-1,-1), [Colors.WHITE, Colors.LIGHT_BG]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        return t
    
    def _section(self, title, color):
        t = Table([[Paragraph(f'<font color="white" size="10"><b>{title}</b></font>', ParagraphStyle('sh', alignment=TA_LEFT))]], colWidths=[7.1*inch])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), color), ('LEFTPADDING', (0,0), (-1,-1), 8), ('PADDING', (0,0), (-1,-1), 5)]))
        return t
    
    def _pillar_section(self, title, color, score, analysis, detailed, keys):
        els = []
        # Header with score
        ht = Table([[Paragraph(f'<font color="white" size="11"><b>{title}</b></font>', ParagraphStyle('ph', alignment=TA_LEFT)),
                    Paragraph(f'<font color="white" size="12"><b>{score:.0f}/100</b></font>', ParagraphStyle('ps', alignment=TA_RIGHT))]], 
                   colWidths=[5.6*inch, 1.5*inch])
        ht.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), color), ('PADDING', (0,0), (-1,-1), 6), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        els.append(ht)
        els.append(Spacer(1, 0.06*inch))
        
        # Score justification
        if analysis.get('score_justification'):
            jb = Table([[Paragraph(f'<font size="8"><b>Score Justification:</b> {self._s(analysis["score_justification"])}</font>', self.styles['Normal'])]], colWidths=[7.1*inch])
            jb.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), Colors.LIGHT_BG), ('BOX', (0,0), (-1,-1), 1, color), ('PADDING', (0,0), (-1,-1), 5)]))
            els.append(jb)
            els.append(Spacer(1, 0.06*inch))
        
        # Summary
        if analysis.get('summary'):
            els.append(Paragraph(f"<b>Summary:</b> {self._s(analysis['summary'])}", self.styles['ESGBody']))
            els.append(Spacer(1, 0.06*inch))
        
        # Key areas in compact format
        for key in keys:
            if analysis.get(key):
                kt = Table([[Paragraph(f'<font size="8" color="{self._hex(color)}"><b>{key.replace("_", " ").title()}</b></font>', self.styles['Normal'])],
                           [Paragraph(f'<font size="8">{self._s(analysis[key])}</font>', self.styles['Normal'])]], colWidths=[7.1*inch])
                kt.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), Colors.LIGHT_BG), ('BOX', (0,0), (-1,-1), 0.5, Colors.BORDER), ('PADDING', (0,0), (-1,-1), 4)]))
                els.append(kt)
                els.append(Spacer(1, 0.04*inch))
        
        # Detailed analysis from agent
        if detailed and len(detailed) > 100:
            els.append(Spacer(1, 0.06*inch))
            els.append(Paragraph(f'<font size="9" color="{self._hex(color)}"><b>Detailed Research Findings</b></font>', self.styles['Normal']))
            els.append(Spacer(1, 0.03*inch))
            # Render paragraphs
            for para in self._s(detailed).split('\n'):
                para = para.strip()
                if para:
                    els.append(Paragraph(f'<font size="8">{para}</font>', self.styles['ESGSmall']))
        
        els.append(Spacer(1, 0.12*inch))
        return els
    
    def _risks_section(self, risks):
        els = [self._section("MATERIAL RISKS", Colors.DANGER), Spacer(1, 0.06*inch)]
        for i, r in enumerate(risks, 1):
            if isinstance(r, dict):
                sev = r.get('severity', 'N/A')
                sc = '#C62828' if sev == 'High' else '#F57C00' if sev == 'Medium' else '#2E7D32'
                rows = [[Paragraph(f'<font size="9"><b>{i}. {self._s(r.get("risk", "N/A"))}</b></font> | '
                                  f'<font size="7" color="#666">{r.get("category", "N/A")}</font> | '
                                  f'<font size="7" color="{sc}"><b>{sev}</b></font>', self.styles['Normal'])]]
                if r.get('impact'):
                    rows.append([Paragraph(f'<font size="7"><b>Impact:</b> {self._s(r["impact"])}</font>', self.styles['Normal'])])
                if r.get('mitigation'):
                    rows.append([Paragraph(f'<font size="7"><b>Mitigation:</b> {self._s(r["mitigation"])}</font>', self.styles['Normal'])])
                rt = Table(rows, colWidths=[7.1*inch])
                rt.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFEBEE')), ('BOX', (0,0), (-1,-1), 0.5, Colors.DANGER), ('PADDING', (0,0), (-1,-1), 4)]))
                els.append(rt)
                els.append(Spacer(1, 0.04*inch))
        els.append(Spacer(1, 0.08*inch))
        return els
    
    def _opportunities_section(self, opps):
        els = [self._section("STRATEGIC OPPORTUNITIES", Colors.SUCCESS), Spacer(1, 0.06*inch)]
        for i, o in enumerate(opps, 1):
            if isinstance(o, dict):
                rows = [[Paragraph(f'<font size="9"><b>{i}. {self._s(o.get("opportunity", "N/A"))}</b></font> | '
                                  f'<font size="7" color="#666">{o.get("pillar", "N/A")}</font>', self.styles['Normal'])]]
                if o.get('potential_value'):
                    rows.append([Paragraph(f'<font size="7"><b>Value:</b> {self._s(o["potential_value"])}</font>', self.styles['Normal'])])
                if o.get('strategic_fit'):
                    rows.append([Paragraph(f'<font size="7"><b>Strategic Fit:</b> {self._s(o["strategic_fit"])}</font>', self.styles['Normal'])])
                ot = Table(rows, colWidths=[7.1*inch])
                ot.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E8F5E9')), ('BOX', (0,0), (-1,-1), 0.5, Colors.SUCCESS), ('PADDING', (0,0), (-1,-1), 4)]))
                els.append(ot)
                els.append(Spacer(1, 0.04*inch))
        els.append(Spacer(1, 0.08*inch))
        return els
    
    def _recommendations_section(self, recs):
        els = [self._section("STRATEGIC RECOMMENDATIONS", Colors.PRIMARY), Spacer(1, 0.06*inch)]
        for i, r in enumerate(recs, 1):
            if isinstance(r, dict):
                pri = r.get('priority', 'N/A')
                pc = '#C62828' if pri == 'High' else '#F57C00' if pri == 'Medium' else '#2E7D32'
                kpis = r.get('kpis', [])
                kstr = ', '.join(kpis) if isinstance(kpis, list) else str(kpis)
                rows = [[Paragraph(f'<font size="9"><b>{i}. {self._s(r.get("recommendation", "N/A"))}</b></font>', self.styles['Normal'])],
                       [Paragraph(f'<font size="7" color="{pc}"><b>Priority: {pri}</b></font> | '
                                 f'<font size="7" color="#666">Pillar: {r.get("pillar", "N/A")} | Timeline: {r.get("timeline", "N/A")}</font>', self.styles['Normal'])]]
                if r.get('rationale'):
                    rows.append([Paragraph(f'<font size="7"><b>Rationale:</b> {self._s(r["rationale"])}</font>', self.styles['Normal'])])
                if kstr:
                    rows.append([Paragraph(f'<font size="7"><b>KPIs:</b> {self._s(kstr)}</font>', self.styles['Normal'])])
                if r.get('expected_impact'):
                    rows.append([Paragraph(f'<font size="7"><b>Expected Impact:</b> {self._s(r["expected_impact"])}</font>', self.styles['Normal'])])
                rt = Table(rows, colWidths=[7.1*inch])
                rt.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), Colors.LIGHT_BG), ('BOX', (0,0), (-1,-1), 0.5, Colors.PRIMARY), ('PADDING', (0,0), (-1,-1), 4)]))
                els.append(rt)
                els.append(Spacer(1, 0.04*inch))
        els.append(Spacer(1, 0.08*inch))
        return els
    
    def _sc(self, v):
        if v >= 85: return '#2E7D32'
        if v >= 70: return '#1565C0'
        if v >= 50: return '#F57C00'
        return '#C62828'
    
    def _rating(self, v):
        if v >= 85: return 'Excellent'
        if v >= 70: return 'Good'
        if v >= 50: return 'Fair'
        return 'Poor'
    
    def _hex(self, c):
        if isinstance(c, str): return c
        try: return c.hexval()
        except: return '#1565C0'
    
    def _parse_json(self, s) -> Dict:
        if isinstance(s, dict): return s
        if not s or not isinstance(s, str): return {}
        try:
            s = s.strip()
            # Remove markdown code blocks
            if '```json' in s: 
                s = s.split('```json')[1].split('```')[0].strip()
            elif '```' in s:
                parts = s.split('```')
                if len(parts) >= 3: 
                    s = parts[1].strip()
                    if s.startswith('json'): s = s[4:].strip()
            # Extract JSON object
            if '{' in s and '}' in s: 
                start = s.find('{')
                end = s.rfind('}') + 1
                s = s[start:end]
            result = json.loads(s)
            print(f"   JSON parsed successfully with {len(result)} keys")
            return result
        except json.JSONDecodeError as e:
            print(f"   ⚠️ JSON parse error: {e}")
            print(f"   First 500 chars of content: {s[:500] if s else 'empty'}")
            return {}
        except Exception as e:
            print(f"   ⚠️ Parse error: {e}")
            return {}
    
    def _fallback_html(self, company, data, industry):
        fn = f"ESG_Report_{company.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        fp = os.path.join(self.output_dir, fn)
        sc = data.get('calculated_scores', {})
        html = f"""<!DOCTYPE html><html><head><title>ESG Report - {company}</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:Arial;background:#f5f7fa;padding:20px;line-height:1.5}}
.c{{max-width:900px;margin:0 auto}}.card{{background:#fff;border-radius:8px;padding:20px;margin:15px 0;box-shadow:0 2px 8px rgba(0,0,0,.1)}}
h1{{color:#0D47A1;font-size:24px}}h2{{color:#1565C0;font-size:16px;border-bottom:2px solid #1565C0;padding-bottom:5px;margin:15px 0}}
.scores{{display:flex;gap:15px;margin:15px 0}}.score{{text-align:center;padding:12px 20px;background:#f0f4f8;border-radius:6px;flex:1}}
.sv{{font-size:32px;font-weight:bold;color:#0D47A1}}.sl{{font-size:10px;color:#666;text-transform:uppercase}}p{{margin:8px 0;color:#333;font-size:14px}}</style></head>
<body><div class="c"><div class="card"><h1>ESG REPORT: {company}</h1><p style="color:#666">{industry or 'N/A'} | {datetime.now().strftime('%B %d, %Y')}</p></div>
<div class="card"><div class="scores"><div class="score"><div class="sv">{sc.get('overall_score',0):.0f}</div><div class="sl">Overall</div></div>
<div class="score"><div class="sv" style="color:#2E7D32">{sc.get('environmental_score',0):.0f}</div><div class="sl">Environmental</div></div>
<div class="score"><div class="sv" style="color:#1565C0">{sc.get('social_score',0):.0f}</div><div class="sl">Social</div></div>
<div class="score"><div class="sv" style="color:#6A1B9A">{sc.get('governance_score',0):.0f}</div><div class="sl">Governance</div></div></div></div>
<div class="card"><h2>Summary</h2><p>{str(data.get('report',''))[:3000]}</p></div></div></body></html>"""
        with open(fp, 'w', encoding='utf-8') as f: f.write(html)
        return fp
