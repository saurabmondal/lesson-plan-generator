import streamlit as st
from groq import Groq
import json
import re
from utils.curriculum import CURRICULUM
from utils.pdf_generator import generate_lesson_plan_pdf
from utils.book_extractor import get_topic_content

# ══════════════════════════════════════════════════════════════════════════════
#  ALL HELPER FUNCTIONS — defined first so they are available everywhere below
# ══════════════════════════════════════════════════════════════════════════════

BLOOM_COLORS = {
    "Remember":   ("#e3f2fd", "#1565c0"),
    "Understand": ("#e8f5e9", "#2e7d32"),
    "Apply":      ("#fff9c4", "#f57f17"),
    "Analyze":    ("#fff3e0", "#e65100"),
    "Evaluate":   ("#fce4ec", "#c62828"),
    "Create":     ("#f3e5f5", "#6a1b9a"),
}


def bloom_tag(level: str) -> str:
    bg, tc = BLOOM_COLORS.get(level, ("#f5f5f5", "#333333"))
    return (
        f'<span style="background:{bg};color:{tc};font-weight:700;'
        f'padding:2px 10px;border-radius:12px;font-size:0.76rem;">{level}</span>'
    )


def build_prompt(subject, class_level, chapter, topic, duration, context):
    return f"""Generate EXACTLY 3 lesson plans for the following:

Subject: {subject}
Class: {class_level}
Chapter: {chapter}
Topic: {topic}
Period Duration: {duration}

CURRICULUM CONTEXT:
{context}

REQUIREMENTS:

1. BLOOM'S TAXONOMY action verbs to use:
   - Remember: define, list, recall, name, identify
   - Understand: explain, describe, summarise, classify, discuss
   - Apply: solve, demonstrate, use, compute, construct
   - Analyze: differentiate, examine, compare, break down
   - Evaluate: judge, assess, argue, defend, justify
   - Create: design, formulate, compose, plan, produce

2. Each plan MUST use a DIFFERENT teaching approach AND a DIFFERENT teaching aid:
   Approaches: Direct Instruction | Inquiry-Based | Collaborative Learning |
               Problem-Based | Activity-Based | Story-Telling | Socratic Method |
               Demonstration | Flipped Classroom
   Teaching Aids: Blackboard & Chalk | Charts/Posters | Activity Worksheets |
                  Real Objects/Manipulatives | PPT Presentation | Educational Videos |
                  Graph Paper | Geoboard | Abacus | Number Cards | Computer/Tablet

3. Structure each plan with all these fields.

Return ONLY this JSON (no markdown fences, no extra text):
{{
  "plans": [
    {{
      "plan_number": 1,
      "approach": "Approach Name",
      "teaching_aid": "Teaching Aid Name",
      "general_objectives": [
        "Cognitive: Students will...",
        "Affective: Students will...",
        "Psychomotor: Students will..."
      ],
      "instructional_objectives": [
        {{"objective": "The student will be able to [action verb] [content]", "bloom_level": "Remember"}},
        {{"objective": "The student will be able to...", "bloom_level": "Understand"}},
        {{"objective": "The student will be able to...", "bloom_level": "Apply"}},
        {{"objective": "The student will be able to...", "bloom_level": "Analyze"}},
        {{"objective": "The student will be able to...", "bloom_level": "Evaluate"}}
      ],
      "previous_knowledge": "Students already know about...",
      "introduction": {{
        "duration": "5 mins",
        "activity": "Detailed description of how the teacher introduces the topic...",
        "motivation": "Real-life connection or interesting question to motivate students..."
      }},
      "presentation": {{
        "duration": "25 mins",
        "teaching_points": [
          {{
            "point": "Teaching Point Title",
            "explanation": "Detailed explanation the teacher gives...",
            "activity": "Student activity for this point..."
          }},
          {{
            "point": "Second Teaching Point",
            "explanation": "Explanation...",
            "activity": "Student activity..."
          }},
          {{
            "point": "Third Teaching Point",
            "explanation": "Explanation...",
            "activity": "Student activity..."
          }}
        ],
        "board_work": "What teacher writes/draws on blackboard..."
      }},
      "recapitulation": {{
        "duration": "5 mins",
        "questions": [
          "Oral question 1?",
          "Oral question 2?",
          "Oral question 3?"
        ]
      }},
      "evaluation": [
        {{"question": "Question at Remember level?", "bloom_level": "Remember", "type": "MCQ"}},
        {{"question": "Question at Understand level?", "bloom_level": "Understand", "type": "Short Answer"}},
        {{"question": "Question at Apply level?", "bloom_level": "Apply", "type": "Problem Solving"}},
        {{"question": "Question at Analyze level?", "bloom_level": "Analyze", "type": "Short Answer"}},
        {{"question": "Question at Evaluate level?", "bloom_level": "Evaluate", "type": "Long Answer"}}
      ],
      "homework": "Specific homework assignment from the textbook or worksheet...",
      "reinforcement": "Extension activity or additional practice for fast learners..."
    }}
  ]
}}"""


def parse_lesson_plans(raw_text: str) -> list:
    text = raw_text.strip()
    # Remove markdown fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    # Direct parse
    try:
        data = json.loads(text)
        return data.get("plans", [])
    except json.JSONDecodeError:
        pass
    # Regex fallback — find the outermost JSON object
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            return data.get("plans", [])
        except json.JSONDecodeError:
            pass
    st.warning("Could not parse structured response. Showing raw output.")
    return [{"approach": "Generated Output", "raw": raw_text, "plan_number": 1}]


def display_plan(plan: dict, num: int):
    if "raw" in plan:
        st.markdown(plan["raw"])
        return

    approach = plan.get("approach", f"Plan {num}")
    aid      = plan.get("teaching_aid", "")

    st.markdown(
        f'<div class="lp-card-header">'
        f'📋 Lesson Plan {num}: {approach} &nbsp;|&nbsp; 🎯 Teaching Aid: {aid}'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.expander("🎯 General Objectives", expanded=True):
        for obj in plan.get("general_objectives", []):
            st.markdown(f"• {obj}")

    with st.expander("📌 Instructional Objectives — Bloom's Taxonomy", expanded=True):
        for io in plan.get("instructional_objectives", []):
            level = io.get("bloom_level", "")
            bg, _ = BLOOM_COLORS.get(level, ("#f5f5f5", "#333"))
            st.markdown(
                f'<div style="background:{bg};border-radius:8px;'
                f'padding:0.5rem 0.9rem;margin:0.3rem 0;">'
                f'{bloom_tag(level)} &nbsp; {io.get("objective","")}'
                f'</div>',
                unsafe_allow_html=True,
            )

    with st.expander("🧠 Previous Knowledge"):
        st.markdown(plan.get("previous_knowledge", ""))

    intro = plan.get("introduction", {})
    with st.expander("🚀 Introduction / Set Induction"):
        st.markdown(f"**Duration:** {intro.get('duration','5 mins')}")
        st.markdown(f"**Activity:** {intro.get('activity','')}")
        st.markdown(f"**Motivation / Real-life Link:** {intro.get('motivation','')}")

    pres = plan.get("presentation", {})
    with st.expander("📖 Presentation / Development", expanded=True):
        st.markdown(f"**Duration:** {pres.get('duration','25 mins')}")
        for i, tp in enumerate(pres.get("teaching_points", []), 1):
            st.markdown(f"**{i}. {tp.get('point','')}**")
            st.markdown(tp.get("explanation", ""))
            if tp.get("activity"):
                st.markdown(
                    f'<div class="info-box">🎓 <b>Student Activity:</b> {tp["activity"]}</div>',
                    unsafe_allow_html=True,
                )
        if pres.get("board_work"):
            st.markdown("---")
            st.markdown(f"**🖊️ Board Work:** {pres['board_work']}")

    recap = plan.get("recapitulation", {})
    with st.expander("🔁 Recapitulation"):
        st.markdown(f"**Duration:** {recap.get('duration','5 mins')}")
        for q in recap.get("questions", []):
            st.markdown(f"• {q}")

    with st.expander("✅ Evaluation / Assessment Questions"):
        for ev in plan.get("evaluation", []):
            level = ev.get("bloom_level", "")
            bg, _ = BLOOM_COLORS.get(level, ("#f5f5f5", "#333"))
            st.markdown(
                f'<div style="background:{bg};border-radius:8px;'
                f'padding:0.5rem 0.9rem;margin:0.3rem 0;">'
                f'<b>Q:</b> {ev.get("question","")} &nbsp;'
                f'{bloom_tag(level)} &nbsp;'
                f'<span style="color:#666;font-size:0.77rem;">{ev.get("type","")}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    c1, c2 = st.columns(2)
    with c1:
        with st.expander("📝 Homework / Assignment"):
            st.markdown(plan.get("homework", ""))
    with c2:
        with st.expander("🔧 Reinforcement"):
            st.markdown(plan.get("reinforcement", ""))


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG & CSS
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="AI Lesson Plan Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
        padding: 2rem 2.5rem; border-radius: 16px; color: white;
        margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(26,35,126,0.3);
    }
    .main-header h1 { font-size: 2.2rem; font-weight: 700; margin: 0; }
    .main-header p  { font-size: 1rem; opacity: 0.85; margin: 0.4rem 0 0; }

    .step-card {
        background: white; border: 1px solid #e8eaf6; border-radius: 12px;
        padding: 1.4rem 1.6rem; margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .step-badge {
        display: inline-block; background: #3949ab; color: white;
        border-radius: 50%; width: 28px; height: 28px; line-height: 28px;
        text-align: center; font-weight: 600; font-size: 0.85rem; margin-right: 8px;
    }
    .step-title { font-weight: 600; font-size: 1rem; color: #1a237e; }

    .lp-card-header {
        background: linear-gradient(90deg, #3949ab, #5c6bc0); color: white;
        padding: 0.7rem 1.2rem; border-radius: 8px; font-weight: 600;
        font-size: 1.05rem; margin-bottom: 1.2rem;
    }
    .info-box {
        background: #e8f5e9; border-left: 4px solid #43a047;
        padding: 0.8rem 1rem; border-radius: 0 8px 8px 0;
        margin: 0.6rem 0; font-size: 0.9rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #3949ab, #5c6bc0);
        color: white; border: none; border-radius: 8px;
        padding: 0.6rem 1.8rem; font-weight: 600; font-size: 1rem;
        width: 100%; transition: all 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(57,73,171,0.4);
    }
    .sidebar-info {
        background: #e8eaf6; border-radius: 10px; padding: 1rem;
        font-size: 0.85rem; color: #1a237e; margin-top: 1rem; line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="main-header">
    <h1>📚 AI Lesson Plan Generator</h1>
    <p>⚡ Powered by Groq (Free & Ultra-Fast) &nbsp;|&nbsp; Bloom's Taxonomy Aligned
       &nbsp;|&nbsp; Classes 6–8 &nbsp;|&nbsp; Maths & Computer Science</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    # Auto-load from Streamlit secrets if available
    default_key = ""
    try:
        default_key = st.secrets["groq"]["api_key"]
    except Exception:
        pass

    api_key = st.text_input(
        "Groq API Key",
        value=default_key,
        type="password",
        placeholder="gsk_...",
        help="Get your FREE key at console.groq.com",
    )
    st.markdown("""
    <div class="sidebar-info">
        🔑 <b>Get FREE Groq API Key:</b><br>
        Go to <b>console.groq.com</b><br>
        Sign Up → API Keys → Create Key<br><br>
        ⚡ <b>Groq is 100% free</b> and generates lesson plans in about 5 seconds!
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🌸 Bloom's Taxonomy Levels")
    for emoji, level, verbs in [
        ("🔵", "Remember",   "define, list, recall"),
        ("🟢", "Understand", "explain, describe"),
        ("🟡", "Apply",      "solve, demonstrate"),
        ("🟠", "Analyze",    "compare, examine"),
        ("🔴", "Evaluate",   "judge, assess"),
        ("🟣", "Create",     "design, formulate"),
    ]:
        st.markdown(f"{emoji} **{level}** — *{verbs}*")

    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown(
        "Generates **3 lesson plans** per topic, each with a **different approach** "
        "and **teaching aid**, strictly following **Bloom's Taxonomy**."
    )

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN UI — SELECTIONS
# ══════════════════════════════════════════════════════════════════════════════

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        '<div class="step-card"><span class="step-badge">1</span>'
        '<span class="step-title">Select Subject & Class</span></div>',
        unsafe_allow_html=True,
    )
    subject = st.selectbox(
        "Subject",
        options=list(CURRICULUM.keys()),
        format_func=lambda x: f"📐 {x}" if "Math" in x else f"💻 {x}",
    )
    class_level = st.selectbox(
        "Class",
        options=list(CURRICULUM[subject].keys()),
        format_func=lambda x: f"Class {x}",
    )

with col2:
    st.markdown(
        '<div class="step-card"><span class="step-badge">2</span>'
        '<span class="step-title">Select Chapter & Topic</span></div>',
        unsafe_allow_html=True,
    )
    chapters = list(CURRICULUM[subject][class_level].keys())
    chapter  = st.selectbox("Chapter", options=chapters)
    topics   = CURRICULUM[subject][class_level][chapter]
    topic    = st.selectbox("Topic", options=topics)

st.markdown(
    '<div class="step-card"><span class="step-badge">3</span>'
    '<span class="step-title">Teacher & School Details (for PDF Header)</span></div>',
    unsafe_allow_html=True,
)
tcol1, tcol2, tcol3 = st.columns(3)
with tcol1:
    teacher_name = st.text_input("Teacher Name", placeholder="e.g. Mrs. Priya Sharma")
with tcol2:
    school_name  = st.text_input("School Name",  placeholder="e.g. Kendriya Vidyalaya")
with tcol3:
    duration = st.selectbox("Period Duration", ["35 mins", "40 mins", "45 mins", "50 mins"])

# ══════════════════════════════════════════════════════════════════════════════
#  GENERATE BUTTON & API CALL
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("<br>", unsafe_allow_html=True)
generate_clicked = st.button("✨ Generate Lesson Plans", use_container_width=True)

if generate_clicked:
    if not api_key or not api_key.strip():
        st.error("⚠️ Please enter your Groq API key in the sidebar.")
        st.stop()

    context = get_topic_content(subject, class_level, chapter, topic)

    with st.spinner("⚡ Groq is generating 3 Bloom's Taxonomy lesson plans..."):
        try:
            client   = Groq(api_key=api_key.strip())
            prompt   = build_prompt(subject, class_level, chapter, topic, duration, context)

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert teacher-educator specialising in NCERT curriculum "
                            "for Indian schools (Classes 6-8). You create detailed, "
                            "Bloom's Taxonomy-aligned lesson plans. "
                            "CRITICAL: Respond with valid JSON ONLY. "
                            "No markdown code fences, no explanations, no text outside the JSON."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=8000,
            )

            raw          = response.choices[0].message.content
            lesson_plans = parse_lesson_plans(raw)

            st.session_state["lesson_plans"] = lesson_plans
            st.session_state["meta"] = {
                "subject":     subject,
                "class_level": class_level,
                "chapter":     chapter,
                "topic":       topic,
                "teacher":     teacher_name,
                "school":      school_name,
                "duration":    duration,
            }
            st.success(f"✅ Generated {len(lesson_plans)} lesson plans successfully!")

        except Exception as e:
            err = str(e)
            if "invalid_api_key" in err.lower() or "401" in err:
                st.error("❌ Invalid Groq API key. Please check console.groq.com and try again.")
            elif "rate_limit" in err.lower() or "429" in err:
                st.warning("⏳ Rate limit reached. Please wait 10 seconds and try again.")
            else:
                st.error(f"❌ Something went wrong: {err}")

# ══════════════════════════════════════════════════════════════════════════════
#  DISPLAY RESULTS
# ══════════════════════════════════════════════════════════════════════════════

if "lesson_plans" in st.session_state and st.session_state["lesson_plans"]:
    plans = st.session_state["lesson_plans"]
    meta  = st.session_state["meta"]

    st.markdown("---")
    st.markdown("## 📋 Generated Lesson Plans")
    st.markdown(
        f"**Subject:** {meta['subject']} &nbsp;|&nbsp; "
        f"**Class:** {meta['class_level']} &nbsp;|&nbsp; "
        f"**Chapter:** {meta['chapter']} &nbsp;|&nbsp; "
        f"**Topic:** {meta['topic']}",
        unsafe_allow_html=True,
    )

    tab_labels = [f"📄 Plan {i+1}: {p.get('approach','')}" for i, p in enumerate(plans)]
    tabs = st.tabs(tab_labels)
    for idx, (tab, plan) in enumerate(zip(tabs, plans)):
        with tab:
            display_plan(plan, idx + 1)

    st.markdown("---")
    st.markdown("### 📥 Download All Lesson Plans as PDF")
    if st.button("📄 Generate & Download PDF", use_container_width=True):
        with st.spinner("Building your PDF..."):
            pdf_bytes = generate_lesson_plan_pdf(plans, meta)
            fname = (
                f"LP_{meta['subject'].replace(' ','_')}"
                f"_Class{meta['class_level']}"
                f"_{meta['topic'].replace(' ','_')}.pdf"
            )
            st.download_button(
                label="⬇️ Click here to Download PDF",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                use_container_width=True,
            )
