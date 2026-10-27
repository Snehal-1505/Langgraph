import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class PDFExporter:
    """Exports research reports into clean, professional PDF documents."""

    @staticmethod
    def generate_pdf(title: str, markdown_content: str, metadata: dict = None) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()

        # Custom professional styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0F172A'),  # Slate-900
            spaceAfter=12
        )

        h1_style = ParagraphStyle(
            'ReportH1',
            parent=styles['Heading2'],
            fontSize=15,
            leading=18,
            textColor=colors.HexColor('#1E3A8A'),  # Blue-900
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True
        )

        h2_style = ParagraphStyle(
            'ReportH2',
            parent=styles['Heading3'],
            fontSize=12,
            leading=15,
            textColor=colors.HexColor('#0369A1'),  # Sky-700
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True
        )

        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155'),  # Slate-700
            spaceAfter=6
        )

        meta_style = ParagraphStyle(
            'ReportMeta',
            parent=styles['Italic'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#64748B'),  # Slate-500
            spaceAfter=12
        )

        story = []

        # Title
        story.append(Paragraph(title, title_style))
        if metadata:
            meta_text = f"ResearchLab AI Report | Status: {metadata.get('status', 'Completed')} | Generated: {metadata.get('date', 'Recent')}"
            story.append(Paragraph(meta_text, meta_style))

        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#CBD5E1'), spaceAfter=14))

        # Parse markdown lines
        lines = markdown_content.split("\n")
        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                story.append(Spacer(1, 4))
                continue

            if trimmed.startswith("# "):
                continue  # Main title already added
            elif trimmed.startswith("## "):
                header_text = trimmed[3:].strip()
                story.append(Paragraph(header_text, h1_style))
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceAfter=6))
            elif trimmed.startswith("### "):
                header_text = trimmed[4:].strip()
                story.append(Paragraph(header_text, h2_style))
            elif trimmed.startswith("- ") or trimmed.startswith("* "):
                bullet_text = "&bull; " + PDFExporter._clean_markdown(trimmed[2:])
                story.append(Paragraph(bullet_text, body_style))
            else:
                body_text = PDFExporter._clean_markdown(trimmed)
                story.append(Paragraph(body_text, body_style))

        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Escape XML entities and format markdown inline tags for ReportLab Paragraphs."""
        # Escape XML chars
        clean = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # Convert markdown bold **text** to <b>text</b>
        clean = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", clean)

        # Convert markdown italic *text* to <i>text</i>
        clean = re.sub(r"\*(.*?)\*", r"<i>\1</i>", clean)

        # Convert markdown links [text](url) to <font color="#0284c7"><u>text</u></font>
        clean = re.sub(r"\[(.*?)\]\((.*?)\)", r'<font color="#0284c7"><u>\1</u></font>', clean)

        return clean
