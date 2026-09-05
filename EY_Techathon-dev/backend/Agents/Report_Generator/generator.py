from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                                TableStyle, PageBreak, Image, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import re
import os

class ReportGenerator:
    def __init__(self, title="Report", author="EY Techathon", company="EY"):
        self.title = title
        self.author = author
        self.company = company
        self.styles = self._create_custom_styles()
        self.story = []
        
    def _create_custom_styles(self):
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#455a64'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Heading styles with colors
        styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#3f51b5'),
            borderPadding=5,
            leftIndent=0,
            backColor=colors.HexColor('#e8eaf6')
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0277bd'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            leftIndent=0
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#00695c'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#212121'),
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16,
            fontName='Helvetica'
        ))
        
        # Code block style
        styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=styles['Code'],
            fontSize=9,
            textColor=colors.HexColor('#c7254e'),
            backColor=colors.HexColor('#f9f2f4'),
            borderWidth=1,
            borderColor=colors.HexColor('#e1bee7'),
            borderPadding=10,
            leftIndent=20,
            rightIndent=20,
            fontName='Courier'
        ))
        
        # Quote style
        styles.add(ParagraphStyle(
            name='Quote',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#424242'),
            leftIndent=30,
            rightIndent=30,
            backColor=colors.HexColor('#fafafa'),
            borderWidth=0,
            borderColor=colors.HexColor('#3f51b5'),
            borderPadding=10,
            spaceAfter=12,
            fontStyle='italic'
        ))
        
        return styles
    
    def _parse_markdown(self, markdown_text):
        lines = markdown_text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Headers
            if line.startswith('# '):
                text = line[2:].strip()
                self.story.append(Paragraph(text, self.styles['CustomHeading1']))
                self.story.append(Spacer(1, 0.2*inch))
                
            elif line.startswith('## '):
                text = line[3:].strip()
                self.story.append(Paragraph(text, self.styles['CustomHeading2']))
                self.story.append(Spacer(1, 0.15*inch))
                
            elif line.startswith('### '):
                text = line[4:].strip()
                self.story.append(Paragraph(text, self.styles['CustomHeading3']))
                self.story.append(Spacer(1, 0.1*inch))
            
            # Code blocks
            elif line.startswith('```'):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                code_text = '\n'.join(code_lines)
                code_text = code_text.replace('<', '&lt;').replace('>', '&gt;')
                self.story.append(Paragraph(f'<pre>{code_text}</pre>', self.styles['CodeBlock']))
                self.story.append(Spacer(1, 0.15*inch))
            
            # Tables
            elif '|' in line and i + 1 < len(lines) and '|' in lines[i + 1]:
                table_data = []
                while i < len(lines) and '|' in lines[i]:
                    row = [cell.strip() for cell in lines[i].split('|') if cell.strip()]
                    if row and not all(c in '-:' for cell in row for c in cell):
                        table_data.append(row)
                    i += 1
                
                if table_data:
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3f51b5')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                        ('TOPPADDING', (0, 1), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                    ]))
                    self.story.append(table)
                    self.story.append(Spacer(1, 0.2*inch))
                i -= 1
            
            # Blockquotes
            elif line.startswith('>'):
                quote_text = line[1:].strip()
                self.story.append(Paragraph(f'"{quote_text}"', self.styles['Quote']))
                self.story.append(Spacer(1, 0.1*inch))
            
            # Lists
            elif line.startswith('- ') or line.startswith('* ') or re.match(r'^\d+\.', line):
                bullet = '•' if line.startswith(('-', '*')) else '▸'
                text = re.sub(r'^[-*]\s*|\d+\.\s*', '', line)
                # Bold text handling
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                self.story.append(Paragraph(f'{bullet} {text}', self.styles['CustomBody']))
            
            # Regular paragraphs
            else:
                # Bold text handling
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                # Italic text handling
                text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
                # Inline code handling
                text = re.sub(r'`(.*?)`', r'<font face="Courier" color="#c7254e">\1</font>', text)
                self.story.append(Paragraph(text, self.styles['CustomBody']))
            
            i += 1
    
    def _create_header_footer(self, canvas, doc):
        canvas.saveState()
        
        # Header
        canvas.setFillColor(colors.HexColor('#3f51b5'))
        canvas.rect(0, A4[1] - 0.8*inch, A4[0], 0.8*inch, fill=True, stroke=False)
        
        canvas.setFont('Helvetica-Bold', 16)
        canvas.setFillColor(colors.white)
        canvas.drawString(1*inch, A4[1] - 0.5*inch, self.title)
        
        # Footer
        canvas.setFillColor(colors.HexColor('#f5f5f5'))
        canvas.rect(0, 0, A4[0], 0.6*inch, fill=True, stroke=False)
        
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#757575'))
        canvas.drawString(1*inch, 0.3*inch, f"{self.company} | {self.author}")
        canvas.drawRightString(A4[0] - 1*inch, 0.3*inch, 
                              f"Page {doc.page} | {datetime.now().strftime('%B %d, %Y')}")
        
        canvas.restoreState()
    
    def create_report(self, markdown_content, output_path=None):
        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(__file__),
                f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1*inch,
            leftMargin=1*inch,
            topMargin=1.2*inch,
            bottomMargin=0.8*inch
        )
        
        # Title page
        self.story.append(Spacer(1, 2*inch))
        self.story.append(Paragraph(self.title, self.styles['CustomTitle']))
        self.story.append(Spacer(1, 0.3*inch))
        
        metadata = f"{self.author} | {datetime.now().strftime('%B %d, %Y')}"
        self.story.append(Paragraph(metadata, self.styles['CustomSubtitle']))
        self.story.append(Spacer(1, 0.5*inch))
        
        self.story.append(PageBreak())
        
        # Parse markdown content
        self._parse_markdown(markdown_content)
        
        # Build PDF
        doc.build(self.story, onFirstPage=self._create_header_footer, 
                 onLaterPages=self._create_header_footer)
        
        return output_path


def create_report(markdown_content, title="Report", author="EY Techathon", save_path=None):
    generator = ReportGenerator(title=title, author=author)
    return generator.create_report(markdown_content, save_path)


# Example usage
if __name__ == "__main__":
    sample_markdown = """
# Executive Summary

This report demonstrates advanced PDF generation capabilities with professional design and formatting.

## Key Performance Indicators

- **Revenue Growth**: 45% increase year-over-year
- **Customer Satisfaction**: 94% positive feedback
- **Market Share**: Expanded to 23% of target market
- **Operational Efficiency**: 30% cost reduction achieved

## Quarterly Performance Analysis

| Quarter | Revenue | Users | Growth Rate |
|---------|---------|-------|-------------|
| Q1 2024 | $2.5M | 15,000 | 12% |
| Q2 2024 | $3.2M | 22,000 | 28% |
| Q3 2024 | $4.1M | 31,000 | 28% |
| Q4 2024 | $5.8M | 45,000 | 41% |

## Technical Implementation

### System Architecture

The platform utilizes a microservices architecture with the following components:

```python
class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.engine = create_engine()
    
    def process(self, data):
        return self.engine.transform(data)
```

### Security Measures

> **Important**: All data is encrypted at rest and in transit using AES-256 encryption standards. Multi-factor authentication is enforced across all user accounts.

## Strategic Recommendations

### Short-term Actions
1. Optimize customer onboarding process
2. Enhance mobile application features
3. Expand customer support team

### Long-term Initiatives
1. **Market Expansion**: Target APAC region by Q2 2025
2. **Product Innovation**: Launch AI-powered analytics suite
3. **Partnership Development**: Establish strategic alliances with industry leaders

## Conclusion

The organization has demonstrated exceptional growth and operational excellence. Continued focus on innovation and customer satisfaction will ensure sustained success.
"""
    
    try:
        report_path = create_report(
            sample_markdown,
            title="Annual Performance Report 2024",
            author="Strategy & Analytics Team"
        )
        
        print(f"✓ Professional PDF report generated successfully!")
        print(f"✓ Location: {report_path}")
    except Exception as e:
        print(f"✗ Error generating report: {e}")
