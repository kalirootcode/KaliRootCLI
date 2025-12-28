"""
Executive Reporting Module for KaliRoot CLI
Generates professional PDF reports using ReportLab.
"""

import os
import json
import logging
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from .ui.display import BANNER_ASCII

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates professional PDF reports."""
    
    def __init__(self, output_dir: str = os.path.expanduser("~/reports")):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Define custom styles matching KR-CLI theme."""
        self.styles.add(ParagraphStyle(
            name='DominionTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00FFFF'), # Cyan
            alignment=1, # Center
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='DominionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#00CED1'), # Cyan
            spaceBefore=20,
            spaceAfter=10,
            borderPadding=5,
            borderColor=colors.HexColor('#FFA500'),
            borderWidth=0,
            borderBottomWidth=1
        ))
        
        self.styles.add(ParagraphStyle(
            name='DominionText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=self.styles['Code'],
            fontSize=8,
            textColor=colors.white,
            backColor=colors.HexColor('#1a1a1a'),
            borderPadding=5,
            leftIndent=10,
            rightIndent=10,
            spaceAfter=12
        ))

    def generate_report(self, session_data: dict, filename: str = None) -> str:
        """
        Generate PDF report from session data.
        
        Args:
            session_data: Dict containing 'summary', 'findings', 'raw_log'
            filename: Optional filename override
            
        Returns:
            Path to generated PDF
        """
        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"KR_Report_{ts}.pdf"
            
        filepath = os.path.join(self.output_dir, filename)
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=72,
            title="KR-CLI Executive Report"
        )
        
        story = []
        
        # 1. Header / Logo
        # Try to add logo if available
        logo_path = os.path.join(os.path.dirname(__file__), "..", "logo.png")
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*inch, height=2*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 0.3 * inch))
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")
        
        story.append(Paragraph("KR-CLI DOMINION", self.styles['DominionTitle']))
        story.append(Paragraph(f"Executive Security Report", self.styles['Title']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 0.5 * inch))
        
        # 2. Executive Summary
        if 'summary' in session_data:
            story.append(Paragraph("Executive Summary", self.styles['DominionHeader']))
            story.append(Paragraph(session_data['summary'], self.styles['DominionText']))
            
        # 3. Critical Findings (Table)
        if 'findings' in session_data and session_data['findings']:
            story.append(Paragraph("Critical Findings", self.styles['DominionHeader']))
            
            # Table Header
            data = [['Severity', 'Vulnerability', 'Location', 'Status']]
            
            for finding in session_data['findings']:
                data.append([
                    finding.get('severity', 'UNKNOWN'),
                    Paragraph(finding.get('name', ''), self.styles['Normal']),
                    finding.get('location', 'N/A'),
                    finding.get('status', 'Open')
                ])
                
            table = Table(data, colWidths=[1*inch, 3*inch, 1.5*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 0.2 * inch))

        # 4. Remediation
        if 'remediation' in session_data:
            story.append(Paragraph("Strategic Remediation", self.styles['DominionHeader']))
            for item in session_data['remediation']:
                story.append(Paragraph(f"• {item}", self.styles['DominionText']))

        # 5. Raw Evidence
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("Appendix: Technical Evidence", self.styles['DominionHeader']))
        if 'raw_log' in session_data:
            # Clean raw log for PDF (simple ASCII handling)
            clean_log = session_data['raw_log'].encode('ascii', errors='ignore').decode('ascii')
            story.append(Paragraph(clean_log, self.styles['CodeBlock']))
            
        doc.build(story)
        return filepath
