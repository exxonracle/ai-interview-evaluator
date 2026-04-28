"""
PDF Report Generator module.
Creates downloadable PDF reports for candidate evaluations using reportlab.
"""

import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def get_score_color(score):
    """Return color based on score value."""
    if score >= 8:
        return colors.HexColor("#22c55e")  # green
    elif score >= 5:
        return colors.HexColor("#eab308")  # yellow
    else:
        return colors.HexColor("#ef4444")  # red


def generate_pdf_report(evaluation_data: dict) -> bytes:
    """Generate a PDF report for a candidate evaluation."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30 * mm,
        leftMargin=30 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=22,
        spaceAfter=6,
        textColor=colors.HexColor("#1e293b"),
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#1e40af"),
        spaceBefore=16,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#334155"),
        leading=14,
        spaceAfter=6
    )
    explanation_style = ParagraphStyle(
        'Explanation',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor("#475569"),
        leading=13,
        spaceAfter=8,
        leftIndent=10,
        fontName='Helvetica-Oblique'
    )

    elements = []

    # Title
    elements.append(Paragraph("Candidate Evaluation Report", title_style))
    elements.append(Paragraph("AI-Powered Skill-Based Hiring Platform", subtitle_style))
    elements.append(HRFlowable(
        width="100%", thickness=1,
        color=colors.HexColor("#e2e8f0"),
        spaceAfter=15
    ))

    # Candidate Info
    name = evaluation_data.get("name", "Unknown")
    email = evaluation_data.get("email", "N/A")
    eval_date = evaluation_data.get("evaluation_date", evaluation_data.get("created_at", "N/A"))

    elements.append(Paragraph("Candidate Information", heading_style))
    info_data = [
        ["Name:", name],
        ["Email:", email],
        ["Evaluation Date:", str(eval_date)[:19]]
    ]
    info_table = Table(info_data, colWidths=[100, 350])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONT', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#475569")),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor("#1e293b")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10))

    # Overall Scores Section
    elements.append(Paragraph("Overall Scores", heading_style))

    full_report = evaluation_data.get("full_report", {}) or {}
    scores = full_report.get("scores", {})
    explanations = full_report.get("explanations", {})

    overall_score = evaluation_data.get("overall_score", 0) or 0
    technical_skill = evaluation_data.get("technical_skill", 0) or 0
    communication = evaluation_data.get("communication", 0) or 0
    problem_solving = evaluation_data.get("problem_solving", 0) or 0

    score_data = [
        ["Metric", "Score", "Rating"],
        ["Overall Score", f"{overall_score}/10",
         "Excellent" if overall_score >= 8 else "Good" if overall_score >= 5 else "Needs Improvement"],
        ["Technical Skill", f"{technical_skill}/10",
         "Excellent" if technical_skill >= 8 else "Good" if technical_skill >= 5 else "Needs Improvement"],
        ["Communication", f"{communication}/10",
         "Excellent" if communication >= 8 else "Good" if communication >= 5 else "Needs Improvement"],
        ["Problem Solving", f"{problem_solving}/10",
         "Excellent" if problem_solving >= 8 else "Good" if problem_solving >= 5 else "Needs Improvement"],
    ]

    score_table = Table(score_data, colWidths=[180, 100, 170])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e40af")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.HexColor("#334155")),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 8))

    # Overall explanation
    overall_expl = explanations.get("overall_explanation", "")
    if overall_expl:
        elements.append(Paragraph(f"Summary: {overall_expl}", explanation_style))

    # Module Breakdown
    elements.append(Paragraph("Module Breakdown", heading_style))

    resume_score = evaluation_data.get("resume_score", 0) or 0
    interview_score = evaluation_data.get("interview_score", 0) or 0
    github_score = evaluation_data.get("github_score", 0) or 0
    video_score = evaluation_data.get("video_score", 0) or 0

    module_data = [
        ["Module", "Score", "Weight"],
        ["Resume Analysis", f"{resume_score}/10", "30%"],
        ["Interview Evaluation", f"{interview_score}/10", "30%"],
        ["GitHub Analysis", f"{github_score}/10", "20%"],
        ["Video Evaluation", f"{video_score}/10", "20%"],
    ]

    module_table = Table(module_data, colWidths=[200, 100, 100])
    module_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#7c3aed")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TEXTCOLOR', (0, 1), (0, -1), colors.HexColor("#334155")),
    ]))
    elements.append(module_table)
    elements.append(Spacer(1, 10))

    # Module Explanations
    module_details = full_report.get("module_details", {})
    
    modules_info = [
        ("Resume Analysis", module_details.get("resume", {})),
        ("Interview Evaluation", module_details.get("interview", {})),
        ("GitHub Analysis", module_details.get("github", {})),
        ("Video Evaluation", module_details.get("video", {})),
    ]

    for module_name, module_data_item in modules_info:
        explanation = module_data_item.get("explanation", "")
        if explanation:
            elements.append(Paragraph(f"<b>{module_name}:</b> {explanation}", body_style))

    elements.append(Spacer(1, 10))

    # Score Explanations
    elements.append(Paragraph("Score Explanations", heading_style))

    expl_items = [
        ("Technical Skill", explanations.get("technical_skill_explanation", "")),
        ("Communication", explanations.get("communication_explanation", "")),
        ("Problem Solving", explanations.get("problem_solving_explanation", "")),
    ]

    for label, expl in expl_items:
        if expl:
            elements.append(Paragraph(f"<b>{label}:</b> {expl}", body_style))

    # Footer
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(
        width="100%", thickness=0.5,
        color=colors.HexColor("#cbd5e1"),
        spaceAfter=8
    ))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor("#94a3b8"),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        "Generated by AI-Powered Skill-Based Hiring Platform • Scores are AI-generated and should be used as guidance only.",
        footer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
