import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import models

def generate_experience_pdf(experience: models.PlacementExperience) -> io.BytesIO:
    """
    Generates a PDF document for a placement experience using ReportLab.
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0d6efd"),
        spaceAfter=10
    )
    
    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#198754"), # Green color for sections
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#333333"),
        spaceAfter=8
    )
    
    elements = []
    
    # Header
    company_name = experience.company.name if experience.company else "Unknown Company"
    elements.append(Paragraph(f"CampusConnect Placement Experience Report", title_style))
    elements.append(Paragraph(f"<b>Company:</b> {company_name} | <b>Role:</b> {experience.job_role}", body_style))
    elements.append(Paragraph(f"<b>Contributor:</b> {experience.author.username} ({experience.author.department or 'N/A'}, Batch: {experience.author.batch or 'N/A'})", body_style))
    elements.append(Spacer(1, 10))
    
    # Meta Information grid
    data = [
        [Paragraph(f"<b>CTC:</b> {experience.ctc} LPA", body_style), Paragraph(f"<b>Hiring Type:</b> {experience.hiring_type}", body_style)],
        [Paragraph(f"<b>Job Type:</b> {experience.job_type}", body_style), Paragraph(f"<b>Result:</b> {experience.result}", body_style)],
        [Paragraph(f"<b>Difficulty:</b> {experience.difficulty}", body_style), Paragraph(f"<b>Location:</b> {experience.location or 'N/A'}", body_style)],
        [Paragraph(f"<b>Rounds:</b> {experience.rounds_count}", body_style), Paragraph(f"<b>Drive Date:</b> {str(experience.drive_date or 'N/A')}", body_style)]
    ]
    
    t = Table(data, colWidths=[250, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#dee2e6"))
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))
    
    # Detailed Experience Subsections
    sections = [
        ("Overall Experience Details", experience.experience_details),
        ("Preparation Strategy", experience.prep_strategy),
        ("Preparation Timeline", experience.prep_timeline),
        ("Coding Round Details", experience.coding_round_exp),
        ("Technical Interview Questions Asked", experience.tech_questions),
        ("SQL Interview Questions", experience.sql_questions),
        ("HR Interview Experience & Questions", experience.hr_questions),
        ("Behavioral Questions Asked", experience.behavioral_questions),
        ("System Design Questions", experience.system_design_questions),
        ("Mistakes to Avoid (Mistakes Made)", experience.mistakes),
        ("Advice and Tips for Juniors", experience.tips),
        ("Resources and Channels Used", experience.resources_used),
        ("LeetCode Problems Solved", experience.leetcode_solved),
        ("Projects Discussed", experience.projects_asked),
        ("Resume & Portfolio Tips", experience.resume_tips),
        ("Final Suggestions", experience.final_suggestions)
    ]
    
    for title, content in sections:
        if content and content.strip():
            elements.append(Paragraph(title, section_heading))
            paragraphs = content.replace('\r\n', '\n').split('\n')
            for p in paragraphs:
                if p.strip():
                    elements.append(Paragraph(p, body_style))
            elements.append(Spacer(1, 5))
            
    doc.build(elements)
    buffer.seek(0)
    return buffer
