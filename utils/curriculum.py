# utils/__init__.py

# utils/pdf_generator.py
# Generates a polished, professional lesson plan PDF using ReportLab.
# Follows the standard teacher lesson plan template used in Indian schools.

import io
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)
from reportlab.platypus.flowables import BalancedColumns

# ── Brand colours ──────────────────────────────────────────────────────────────
DARK_BLUE   = colors.HexColor("#1a237e")
MED_BLUE    = colors.HexColor("#3949ab")
LIGHT_BLUE  = colors.HexColor("#c5cae9")
VERY_LIGHT  = colors.HexColor("#e8eaf6")
ACCENT      = colors.HexColor("#7986cb")
WHITE       = colors.white
BLACK       = colors.black
GRAY        = colors.HexColor("#546e7a")
LIGHT_GRAY  = colors.HexColor("#eceff1")

BLOOM_BG = {
    "Remember":   colors.HexColor("#e3f2fd"),
    "Understand": colors.HexColor("#e8f5e9"),
    "Apply":      colors.HexColor("#fff9c4"),
    "Analyze":    colors.HexColor("#fff3e0"),
    "Evaluate":   colors.HexColor("#fce4ec"),
    "Create":     colors.HexColor("#f3e5f5"),
}
BLOOM_FG = {
    "Remember":   colors.HexColor("#1565c0"),
    "Understand": colors.HexColor("#2e7d32"),
    "Apply":      colors.HexColor("#f57f17"),
    "Analyze":    colors.HexColor("#e65100"),
    "Evaluate":   colors.HexColor("#c62828"),
    "Create":     colors.HexColor("#6a1b9a"),
}


def generate_lesson_plan_pdf(plans: list, meta: dict) -> bytes:
    """Return a bytes object containing the full PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Lesson Plan – {meta.get('topic', '')}",
        author=meta.get("teacher", "Teacher"),
    )

    styles = _build_styles()
    story  = []

    # ── Document cover page ────────────────────────────────────────────────────
    story += _cover_page(meta, styles)
    story.append(PageBreak())

    # ── Individual lesson plans ────────────────────────────────────────────────
    for idx, plan in enumerate(plans):
        story += _render_plan(plan, idx + 1, meta, styles)
        if idx < len(plans) - 1:
            story.append(PageBreak())

    doc.build(story, onFirstPage=_page_header_footer, onLaterPages=_page_header_footer)
    buffer.seek(0)
    return buffer.read()


# ── Style builder ──────────────────────────────────────────────────────────────
def _build_styles():
    base = getSampleStyleSheet()
    s = {}

    def add(name, **kw):
        s[name] = ParagraphStyle(name, **kw)

    add("CoverTitle",
        fontName="Helvetica-Bold", fontSize=22, textColor=WHITE,
        alignment=TA_CENTER, leading=28, spaceAfter=6)
    add("CoverSub",
        fontName="Helvetica", fontSize=12, textColor=LIGHT_BLUE,
        alignment=TA_CENTER, leading=18, spaceAfter=4)
    add("CoverMeta",
        fontName="Helvetica", fontSize=10, textColor=WHITE,
        alignment=TA_CENTER, leading=16)

    add("SectionHeader",
        fontName="Helvetica-Bold", fontSize=11, textColor=WHITE,
        alignment=TA_LEFT, leading=16, leftIndent=4)
    add("PlanTitle",
        fontName="Helvetica-Bold", fontSize=13, textColor=WHITE,
        alignment=TA_CENTER, leading=18)

    add("Label",
        fontName="Helvetica-Bold", fontSize=9, textColor=MED_BLUE,
        leading=13)
    add("Body",
        fontName="Helvetica", fontSize=9, textColor=BLACK,
        leading=13, alignment=TA_JUSTIFY)
    add("BulletBody",
        fontName="Helvetica", fontSize=9, textColor=BLACK,
        leading=13, leftIndent=12, bulletIndent=0)
    add("BloomTag",
        fontName="Helvetica-Bold", fontSize=8, leading=12)
    add("SmallGray",
        fontName="Helvetica", fontSize=8, textColor=GRAY, leading=11)
    add("TableHeader",
        fontName="Helvetica-Bold", fontSize=9, textColor=WHITE,
        alignment=TA_CENTER, leading=13)
    add("TableCell",
        fontName="Helvetica", fontSize=8.5, textColor=BLACK,
        leading=12, alignment=TA_LEFT)

    return s


# ── Cover page ─────────────────────────────────────────────────────────────────
def _cover_page(meta, s):
    elements = []

    elements.append(Spacer(1, 1.5 * cm))

    # Blue header banner
    banner_data = [[
        Paragraph("LESSON PLAN", s["CoverTitle"]),
    ]]
    banner = Table(banner_data, colWidths=[17 * cm])
    banner.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), DARK_BLUE),
        ("ROUNDEDCORNERS", [10]),
        ("TOPPADDING",  (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))
    elements.append(banner)
    elements.append(Spacer(1, 0.6 * cm))

    # Subtitle band
    sub_data = [[
        Paragraph("AI-Generated • Bloom's Taxonomy Aligned • NCERT Curriculum", s["CoverSub"]),
    ]]
    sub = Table(sub_data, colWidths=[17 * cm])
    sub.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), MED_BLUE),
        ("TOPPADDING",  (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(sub)
    elements.append(Spacer(1, 1.2 * cm))

    # Meta info table
    meta_rows = [
        ["Subject",   meta.get("subject", ""),    "Class",    f"Class {meta.get('class_level','')}"],
        ["Chapter",   meta.get("chapter", ""),    "Topic",    meta.get("topic", "")],
        ["Teacher",   meta.get("teacher", "—"),   "School",   meta.get("school", "—")],
        ["Duration",  meta.get("duration", ""),   "Date",     date.today().strftime("%d %B %Y")],
    ]
    from reportlab.platypus import Table as RLTable
    tbl_data = []
    for r in meta_rows:
        tbl_data.append([
            Paragraph(r[0], s["Label"]),
            Paragraph(r[1], s["Body"]),
            Paragraph(r[2], s["Label"]),
            Paragraph(r[3], s["Body"]),
        ])

    tbl = RLTable(tbl_data, colWidths=[3.2 * cm, 5.3 * cm, 3.2 * cm, 5.3 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (0, -1), VERY_LIGHT),
        ("BACKGROUND",  (2, 0), (2, -1), VERY_LIGHT),
        ("GRID",        (0, 0), (-1, -1), 0.5, LIGHT_BLUE),
        ("TOPPADDING",  (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 1.5 * cm))

    # Bloom's Taxonomy legend
    bloom_data = [["Bloom's Taxonomy Levels Used in This Document"]]
    bloom_hdr = Table(bloom_data, colWidths=[17 * cm])
    bloom_hdr.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), MED_BLUE),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(bloom_hdr)

    bloom_info = [
        ("Remember",   "Recall facts and basic concepts",         "define, list, recall, name, identify"),
        ("Understand", "Explain ideas and concepts",              "explain, describe, summarise, classify"),
        ("Apply",      "Use information in new situations",       "solve, demonstrate, compute, use"),
        ("Analyze",    "Draw connections among ideas",            "differentiate, compare, examine"),
        ("Evaluate",   "Justify a decision or course of action",  "judge, assess, argue, defend"),
        ("Create",     "Produce new or original work",            "design, formulate, compose, plan"),
    ]
    b_rows = []
    for level, desc, verbs in bloom_info:
        bg = BLOOM_BG.get(level, LIGHT_GRAY)
        fg = BLOOM_FG.get(level, BLACK)
        b_rows.append([
            Paragraph(f'<font color="#{_hex(fg)}" size="9"><b>{level}</b></font>', s["Body"]),
            Paragraph(desc, s["Body"]),
            Paragraph(f'<i>{verbs}</i>', s["SmallGray"]),
        ])
    bloom_tbl = Table(b_rows, colWidths=[3.2 * cm, 7 * cm, 6.8 * cm])
    bloom_style = [
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i, (level, _, _) in enumerate(bloom_info):
        bg = BLOOM_BG.get(level, LIGHT_GRAY)
        bloom_style.append(("BACKGROUND", (0, i), (0, i), bg))
    bloom_tbl.setStyle(TableStyle(bloom_style))
    elements.append(bloom_tbl)

    return elements


# ── Individual plan renderer ───────────────────────────────────────────────────
def _render_plan(plan, num, meta, s):
    elements = []

    approach = plan.get("approach", f"Plan {num}")
    aid      = plan.get("teaching_aid", "")

    # ── Plan header ────────────────────────────────────────────────────────────
    hdr_data = [[Paragraph(
        f"Lesson Plan {num}  |  Approach: {approach}  |  Teaching Aid: {aid}",
        s["PlanTitle"],
    )]]
    hdr = Table(hdr_data, colWidths=[17 * cm])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    elements.append(hdr)
    elements.append(Spacer(1, 0.3 * cm))

    # ── Top meta strip ─────────────────────────────────────────────────────────
    strip_data = [[
        Paragraph(f"<b>Subject:</b> {meta.get('subject','')}", s["Body"]),
        Paragraph(f"<b>Class:</b> {meta.get('class_level','')}", s["Body"]),
        Paragraph(f"<b>Topic:</b> {meta.get('topic','')}", s["Body"]),
        Paragraph(f"<b>Duration:</b> {meta.get('duration','')}", s["Body"]),
    ]]
    strip = Table(strip_data, colWidths=[4.25 * cm] * 4)
    strip.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), VERY_LIGHT),
        ("GRID",          (0, 0), (-1, -1), 0.5, LIGHT_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    elements.append(strip)
    elements.append(Spacer(1, 0.4 * cm))

    # ── General Objectives ─────────────────────────────────────────────────────
    elements += _section_header("1. General Objectives", s)
    for obj in plan.get("general_objectives", []):
        elements.append(Paragraph(f"• {obj}", s["BulletBody"]))
    elements.append(Spacer(1, 0.3 * cm))

    # ── Instructional Objectives ───────────────────────────────────────────────
    elements += _section_header("2. Specific / Instructional Objectives (Bloom's Taxonomy)", s)
    io_rows = [
        [
            Paragraph("<b>No.</b>",        s["TableHeader"]),
            Paragraph("<b>Objective</b>",  s["TableHeader"]),
            Paragraph("<b>Bloom's Level</b>", s["TableHeader"]),
        ]
    ]
    for i, io in enumerate(plan.get("instructional_objectives", []), 1):
        level = io.get("bloom_level", "")
        bg    = BLOOM_BG.get(level, LIGHT_GRAY)
        io_rows.append([
            Paragraph(str(i), s["TableCell"]),
            Paragraph(io.get("objective", ""), s["TableCell"]),
            Paragraph(f"<b>{level}</b>", s["TableCell"]),
        ])
    io_tbl = Table(io_rows, colWidths=[0.8 * cm, 12.4 * cm, 3.8 * cm])
    io_style = [
        ("BACKGROUND",    (0, 0), (-1, 0), MED_BLUE),
        ("GRID",          (0, 0), (-1, -1), 0.4, LIGHT_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]
    for i, io in enumerate(plan.get("instructional_objectives", []), 1):
        level = io.get("bloom_level", "")
        bg    = BLOOM_BG.get(level, LIGHT_GRAY)
        io_style.append(("BACKGROUND", (2, i), (2, i), bg))
        fg = BLOOM_FG.get(level, BLACK)
        io_style.append(("TEXTCOLOR", (2, i), (2, i), fg))
    io_tbl.setStyle(TableStyle(io_style))
    elements.append(io_tbl)
    elements.append(Spacer(1, 0.35 * cm))

    # ── Previous Knowledge ─────────────────────────────────────────────────────
    elements += _section_header("3. Previous Knowledge", s)
    elements.append(Paragraph(plan.get("previous_knowledge", ""), s["Body"]))
    elements.append(Spacer(1, 0.35 * cm))

    # ── Introduction ──────────────────────────────────────────────────────────
    intro = plan.get("introduction", {})
    elements += _section_header(
        f"4. Introduction / Set Induction  ({intro.get('duration','5 mins')})", s)
    elements.append(Paragraph(f"<b>Activity:</b> {intro.get('activity','')}", s["Body"]))
    elements.append(Spacer(1, 0.15 * cm))
    elements.append(Paragraph(f"<b>Motivation / Link to Real Life:</b> {intro.get('motivation','')}", s["Body"]))
    elements.append(Spacer(1, 0.35 * cm))

    # ── Presentation ──────────────────────────────────────────────────────────
    pres = plan.get("presentation", {})
    elements += _section_header(
        f"5. Presentation / Development  ({pres.get('duration','25 mins')})", s)

    for i, tp in enumerate(pres.get("teaching_points", []), 1):
        pt_data = [[
            Paragraph(f"<b>Teaching Point {i}: {tp.get('point','')}</b>", s["Label"]),
        ]]
        pt_hdr = Table(pt_data, colWidths=[17 * cm])
        pt_hdr.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), VERY_LIGHT),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("LINEBELOW",     (0, 0), (-1, -1), 1, ACCENT),
        ]))
        elements.append(pt_hdr)
        elements.append(Spacer(1, 0.1 * cm))
        elements.append(Paragraph(tp.get("explanation", ""), s["Body"]))
        if tp.get("activity"):
            act_data = [[
                Paragraph(f"🎓 <b>Student Activity:</b> {tp['activity']}", s["Body"]),
            ]]
            act = Table(act_data, colWidths=[17 * cm])
            act.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#e8f5e9")),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("LINEAFTER",     (0, 0), (0, -1), 3, colors.HexColor("#43a047")),
            ]))
            elements.append(act)
        elements.append(Spacer(1, 0.25 * cm))

    if pres.get("board_work"):
        elements += _section_header("Board Work / Blackboard Summary", s, sub=True)
        elements.append(Paragraph(pres["board_work"], s["Body"]))
        elements.append(Spacer(1, 0.35 * cm))

    # ── Recapitulation ────────────────────────────────────────────────────────
    recap = plan.get("recapitulation", {})
    elements += _section_header(
        f"6. Recapitulation  ({recap.get('duration','5 mins')})", s)
    for q in recap.get("questions", []):
        elements.append(Paragraph(f"• {q}", s["BulletBody"]))
    elements.append(Spacer(1, 0.35 * cm))

    # ── Evaluation ────────────────────────────────────────────────────────────
    elements += _section_header("7. Evaluation / Assessment Questions", s)
    ev_rows = [[
        Paragraph("<b>Q.No</b>", s["TableHeader"]),
        Paragraph("<b>Question</b>", s["TableHeader"]),
        Paragraph("<b>Type</b>", s["TableHeader"]),
        Paragraph("<b>Bloom's Level</b>", s["TableHeader"]),
    ]]
    for i, ev in enumerate(plan.get("evaluation", []), 1):
        level = ev.get("bloom_level", "")
        ev_rows.append([
            Paragraph(str(i), s["TableCell"]),
            Paragraph(ev.get("question", ""), s["TableCell"]),
            Paragraph(ev.get("type", ""), s["TableCell"]),
            Paragraph(f"<b>{level}</b>", s["TableCell"]),
        ])
    ev_tbl = Table(ev_rows, colWidths=[0.8 * cm, 10 * cm, 3 * cm, 3.2 * cm])
    ev_style = [
        ("BACKGROUND",    (0, 0), (-1, 0), MED_BLUE),
        ("GRID",          (0, 0), (-1, -1), 0.4, LIGHT_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]
    for i, ev in enumerate(plan.get("evaluation", []), 1):
        level = ev.get("bloom_level", "")
        bg    = BLOOM_BG.get(level, LIGHT_GRAY)
        fg    = BLOOM_FG.get(level, BLACK)
        ev_style.append(("BACKGROUND", (3, i), (3, i), bg))
        ev_style.append(("TEXTCOLOR",  (3, i), (3, i), fg))
    ev_tbl.setStyle(TableStyle(ev_style))
    elements.append(ev_tbl)
    elements.append(Spacer(1, 0.35 * cm))

    # ── Homework & Reinforcement ───────────────────────────────────────────────
    hw_rf = [
        [
            Paragraph("<b>8. Homework / Assignment</b>", s["Label"]),
            Paragraph("<b>9. Reinforcement</b>", s["Label"]),
        ],
        [
            Paragraph(plan.get("homework", ""), s["Body"]),
            Paragraph(plan.get("reinforcement", ""), s["Body"]),
        ],
    ]
    hw_tbl = Table(hw_rf, colWidths=[8.5 * cm, 8.5 * cm])
    hw_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), VERY_LIGHT),
        ("GRID",          (0, 0), (-1, -1), 0.5, LIGHT_BLUE),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(hw_tbl)
    elements.append(Spacer(1, 0.4 * cm))

    # ── Signature row ─────────────────────────────────────────────────────────
    sig_data = [[
        Paragraph("Teacher's Signature: ___________________________", s["SmallGray"]),
        Paragraph("Principal's Signature: ___________________________", s["SmallGray"]),
        Paragraph(f"Date: {date.today().strftime('%d/%m/%Y')}", s["SmallGray"]),
    ]]
    sig = Table(sig_data, colWidths=[6 * cm, 6 * cm, 5 * cm])
    sig.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEABOVE",     (0, 0), (-1, 0), 0.5, LIGHT_BLUE),
    ]))
    elements.append(sig)

    return elements


# ── Section header helper ──────────────────────────────────────────────────────
def _section_header(title, s, sub=False):
    bg = ACCENT if sub else MED_BLUE
    data = [[Paragraph(title, s["SectionHeader"])]]
    tbl  = Table(data, colWidths=[17 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    return [tbl, Spacer(1, 0.15 * cm)]


# ── Page header / footer canvas callback ──────────────────────────────────────
def _page_header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # Top thin bar
    canvas.setFillColor(DARK_BLUE)
    canvas.rect(1.8 * cm, h - 1.3 * cm, w - 3.6 * cm, 0.35 * cm, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.setFillColor(WHITE)
    canvas.drawString(1.9 * cm, h - 1.22 * cm, "AI LESSON PLAN GENERATOR  |  BLOOM'S TAXONOMY ALIGNED")

    # Bottom bar
    canvas.setFillColor(VERY_LIGHT)
    canvas.rect(1.8 * cm, 1.2 * cm, w - 3.6 * cm, 0.35 * cm, fill=1, stroke=0)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MED_BLUE)
    canvas.drawString(1.9 * cm, 1.28 * cm,
        "Generated by AI Lesson Plan Generator  |  NCERT Curriculum  |  Classes 6–8")
    canvas.drawRightString(w - 1.9 * cm, 1.28 * cm, f"Page {doc.page}")

    canvas.restoreState()


# ── Utility ────────────────────────────────────────────────────────────────────
def _hex(color_obj):
    """Return 6-char hex string from a ReportLab Color (no leading #)."""
    r, g, b = int(color_obj.red * 255), int(color_obj.green * 255), int(color_obj.blue * 255)
    return f"{r:02x}{g:02x}{b:02x}"

# utils/book_extractor.py
# ─────────────────────────────────────────────────────────────────────────────
# Extracts relevant topic content from uploaded textbook PDFs.
# Books should be placed in:  data/books/<subject>_Class<N>.pdf
#   e.g. data/books/Mathematics_Class6.pdf
#        data/books/ComputerScience_Class7.pdf
#
# If no book PDF is found, a rich fallback context is returned so the AI
# can still generate a high-quality lesson plan from its training knowledge.
# ─────────────────────────────────────────────────────────────────────────────

import os
import re
from pathlib import Path

# Try to import pdfplumber; fall back gracefully if not installed
try:
    import pdfplumber
    _PDFPLUMBER = True
except ImportError:
    _PDFPLUMBER = False

try:
    from pypdf import PdfReader
    _PYPDF = True
except ImportError:
    _PYPDF = False

BOOKS_DIR = Path(__file__).parent.parent / "data" / "books"
CONTEXT_WINDOW = 3000  # max characters of book text to include in prompt


def get_topic_content(subject: str, class_level: str, chapter: str, topic: str) -> str:
    """
    Return a text excerpt from the relevant textbook.
    Falls back to a structured fallback if no book is found.
    """
    pdf_path = _find_book(subject, class_level)

    if pdf_path and pdf_path.exists():
        text = _extract_pdf_text(pdf_path)
        snippet = _find_relevant_snippet(text, chapter, topic)
        if snippet:
            return (
                f"[Extracted from uploaded textbook: {pdf_path.name}]\n\n"
                f"{snippet}\n\n"
                f"[End of book excerpt]"
            )

    # No book found — return knowledge-base context
    return _fallback_context(subject, class_level, chapter, topic)


# ── Private helpers ────────────────────────────────────────────────────────────

def _find_book(subject: str, class_level: str) -> Path | None:
    """Try several filename patterns to locate the textbook PDF."""
    safe_subject = subject.replace(" ", "").replace("/", "")
    patterns = [
        f"{safe_subject}_Class{class_level}.pdf",
        f"{safe_subject}_class{class_level}.pdf",
        f"{subject.replace(' ','_')}_Class{class_level}.pdf",
        f"Class{class_level}_{safe_subject}.pdf",
        f"class{class_level}_{safe_subject.lower()}.pdf",
        f"Math_Class{class_level}.pdf",
        f"CS_Class{class_level}.pdf",
    ]
    for pattern in patterns:
        p = BOOKS_DIR / pattern
        if p.exists():
            return p

    # Fuzzy: any PDF that contains both subject hint and class number
    subject_hint = "math" if "math" in subject.lower() else "computer"
    for pdf in BOOKS_DIR.glob("*.pdf"):
        name_lower = pdf.name.lower()
        if subject_hint in name_lower and class_level in name_lower:
            return pdf

    return None


def _extract_pdf_text(pdf_path: Path) -> str:
    """Extract all text from PDF using pdfplumber → pypdf fallback."""
    text = ""

    if _PDFPLUMBER:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return text
        except Exception:
            pass

    if _PYPDF:
        try:
            reader = PdfReader(str(pdf_path))
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        except Exception:
            pass

    return text


def _find_relevant_snippet(full_text: str, chapter: str, topic: str) -> str:
    """
    Find the most relevant section of the book text for the given chapter/topic.
    Uses keyword matching and returns a trimmed window of text.
    """
    if not full_text.strip():
        return ""

    # Build search keywords from chapter title and topic name
    chapter_clean = re.sub(r"Chapter\s*\d+\s*[:–-]?\s*", "", chapter, flags=re.IGNORECASE).strip()
    keywords = (
        _tokenize(topic) +
        _tokenize(chapter_clean)
    )

    lines = full_text.split("\n")
    scored: list[tuple[int, int]] = []  # (score, line_index)

    for i, line in enumerate(lines):
        line_lower = line.lower()
        score = sum(1 for kw in keywords if kw in line_lower)
        if score > 0:
            scored.append((score, i))

    if not scored:
        # Return first CONTEXT_WINDOW characters as fallback
        return full_text[:CONTEXT_WINDOW]

    # Pick the highest-scoring hit
    scored.sort(key=lambda x: -x[0])
    best_line = scored[0][1]

    # Extract a window of lines around the best hit
    start = max(0, best_line - 3)
    end   = min(len(lines), best_line + 60)
    snippet = "\n".join(lines[start:end])

    return snippet[:CONTEXT_WINDOW]


def _tokenize(text: str) -> list[str]:
    """Return lower-case tokens (2+ chars) from a string."""
    return [w.lower() for w in re.findall(r"\b[a-zA-Z]{2,}\b", text)]


def _fallback_context(subject: str, class_level: str, chapter: str, topic: str) -> str:
    """
    Return a rich structured context string when no book PDF is available.
    This gives the AI enough scaffolding to generate a great lesson plan.
    """
    return f"""[No textbook PDF found for {subject} Class {class_level}. 
Using AI knowledge base.]

Subject:     {subject}
Class:       {class_level}
Chapter:     {chapter}
Topic:       {topic}

Teaching Context:
- Students are in Class {class_level} (age approximately {int(class_level) + 5}–{int(class_level) + 6} years)
- Curriculum follows NCERT / CBSE guidelines
- Medium of instruction: English
- Prior knowledge: students have completed earlier chapters in this subject

Topic Overview:
Please generate a comprehensive lesson plan for "{topic}" from the chapter "{chapter}" 
as per the NCERT Class {class_level} {subject} curriculum. 

The lesson plan should:
1. Be appropriate for the cognitive level of Class {class_level} students
2. Connect to real-life examples familiar to Indian school students
3. Use the NCERT textbook approach and terminology
4. Follow the Indian school classroom structure (single teacher, 35–45 min period)
5. Include activities suitable for a classroom with basic resources (blackboard, chalk, textbook)

Generate 3 lesson plans with DIFFERENT teaching approaches and teaching aids.
"""
