# 📚 AI Lesson Plan Generator

An AI-powered lesson plan generator for **Classes 6–8** covering **Mathematics** and **Computer Science**.  
Generates **2–3 lesson plans per topic**, each with a different teaching approach and teaching aid, strictly following **Bloom's Taxonomy**.

---

## ✨ Features

- 📐 **Subjects:** Mathematics & Computer Science (Class 6, 7, 8 — NCERT)
- 🌸 **Bloom's Taxonomy** — Every objective tagged with the correct cognitive level
- 📄 **3 Lesson Plans per topic** — Different approach + different teaching aid each time
- 📥 **PDF Download** — Professional, formatted PDF matching standard LP template
- 📖 **Book-aware** — Upload your NCERT PDFs and the AI extracts relevant content
- 🆓 **100% Free** — Runs on Streamlit Community Cloud + Anthropic free tier

---

## 🚀 Quick Start (Local)

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/lesson-plan-generator.git
cd lesson-plan-generator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Anthropic API key
```bash
# Create the secrets file
mkdir -p .streamlit
echo '[anthropic]
api_key = "sk-ant-YOUR_KEY_HERE"' > .streamlit/secrets.toml
```
> Get a free key at https://console.anthropic.com

### 4. (Optional) Add your textbook PDFs
Place your NCERT textbook PDFs in `data/books/` using these exact names:
```
data/books/Mathematics_Class6.pdf
data/books/Mathematics_Class7.pdf
data/books/Mathematics_Class8.pdf
data/books/ComputerScience_Class6.pdf
data/books/ComputerScience_Class7.pdf
data/books/ComputerScience_Class8.pdf
```
> The app works without books too — it uses the AI's built-in NCERT knowledge.

### 5. Run the app
```bash
streamlit run app.py
```

---

## 🌐 Deploy on Streamlit Community Cloud (FREE)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Go to** https://share.streamlit.io

3. **Click "New app"** → Select your repo → Set main file to `app.py`

4. **Add your API key** → Click "Advanced settings" → Secrets:
   ```toml
   [anthropic]
   api_key = "sk-ant-YOUR_KEY_HERE"
   ```

5. **Click Deploy** → Done! Your app is live at a free URL.

> ⚠️ If your book PDFs are large (>100MB), don't commit them to GitHub.  
> Use Streamlit's file uploader feature instead (see `UPLOAD_BOOKS.md`).

---

## 📁 Project Structure

```
lesson-plan-generator/
├── app.py                    ← Main Streamlit application
├── requirements.txt          ← Python dependencies
├── .streamlit/
│   └── config.toml           ← UI theme
├── utils/
│   ├── curriculum.py         ← All subjects / classes / chapters / topics
│   ├── pdf_generator.py      ← PDF creation with ReportLab
│   └── book_extractor.py     ← Extracts text from uploaded PDFs
├── data/
│   ├── books/                ← Place textbook PDFs here
│   └── templates/            ← Place your LP template PDF here
└── assets/                   ← Logo / images (optional)
```

---

## 📝 Adding / Editing Curriculum

Open `utils/curriculum.py` and edit the `CURRICULUM` dictionary.  
Structure:
```python
CURRICULUM = {
    "Subject Name": {
        "ClassNumber": {
            "Chapter N: Title": [
                "Topic 1",
                "Topic 2",
            ],
        }
    }
}
```

---

## 🌸 Bloom's Taxonomy at a Glance

| Level | Action Verbs |
|-------|-------------|
| 🔵 Remember | define, list, recall, name, identify |
| 🟢 Understand | explain, describe, summarise, classify |
| 🟡 Apply | solve, demonstrate, compute, use |
| 🟠 Analyze | differentiate, compare, examine |
| 🔴 Evaluate | judge, assess, argue, defend |
| 🟣 Create | design, formulate, compose, plan |

---

## 📜 Lesson Plan Template Structure

Each generated lesson plan contains:
1. **General Objectives** (Cognitive / Affective / Psychomotor)
2. **Specific Instructional Objectives** (Bloom's tagged)
3. **Previous Knowledge**
4. **Introduction / Set Induction** (5 mins)
5. **Presentation / Development** (25 mins — teaching points + activities)
6. **Board Work**
7. **Recapitulation** (5 mins)
8. **Evaluation Questions** (5 questions at different Bloom's levels)
9. **Homework / Assignment**
10. **Reinforcement**

---

## 🆓 Cost

| Service | Cost |
|---------|------|
| Streamlit Community Cloud | **Free** |
| GitHub | **Free** |
| Anthropic API (free tier) | **Free** (limited tokens/month) |

> The free Anthropic tier is sufficient for ~100–200 lesson plan generations per month.

---

## 🤝 Contributing

PRs welcome! Add more subjects, classes, or improve the PDF template.

---

## 📧 Support

Open a GitHub Issue for bugs or feature requests.
