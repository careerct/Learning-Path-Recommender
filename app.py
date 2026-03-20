import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
import datetime
import hashlib
import time

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NeuralPath — AI Career Recommender",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }

.stApp {
    background:#04070f;
    font-family:'DM Sans',sans-serif;
    color:#e2e8f8;
}
.stApp::before {
    content:'';
    position:fixed; inset:0;
    background-image:
        linear-gradient(rgba(96,165,250,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(96,165,250,0.03) 1px, transparent 1px);
    background-size:52px 52px;
    animation:gridScroll 30s linear infinite;
    pointer-events:none; z-index:0;
}
@keyframes gridScroll { to { background-position:52px 52px; } }
.stApp::after {
    content:'';
    position:fixed; inset:0;
    background:
        radial-gradient(ellipse 55% 45% at 8% 12%, rgba(56,189,248,0.055) 0%, transparent 65%),
        radial-gradient(ellipse 45% 40% at 92% 78%, rgba(139,92,246,0.055) 0%, transparent 65%);
    pointer-events:none; z-index:0;
}
.main .block-container {
    position:relative; z-index:1;
    padding:0 2.4rem 4rem;
    max-width:1380px;
}
h1,h2,h3,h4 { font-family:'Syne',sans-serif !important; letter-spacing:-0.02em; }
#MainMenu, footer, header { visibility:hidden; }
.stDeployButton { display:none; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:#0d1117; }
::-webkit-scrollbar-thumb { background:#1e40af; border-radius:4px; }

/* ── Buttons ── */
.stButton > button {
    background:linear-gradient(135deg,#1d4ed8 0%,#7c3aed 100%) !important;
    color:#fff !important; border:none !important;
    border-radius:11px !important;
    font-family:'Syne',sans-serif !important;
    font-weight:700 !important; font-size:14px !important;
    padding:0.62rem 1.5rem !important;
    transition:all 0.22s ease !important;
    box-shadow:0 4px 18px rgba(29,78,216,0.3) !important;
}
.stButton > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 8px 28px rgba(29,78,216,0.5) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stPasswordInput > div > div > input {
    background:rgba(15,23,42,0.85) !important;
    border:1px solid rgba(96,165,250,0.2) !important;
    border-radius:11px !important; color:#e2e8f8 !important;
    font-family:'DM Sans',sans-serif !important;
    padding:0.65rem 1rem !important;
    transition:border 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stPasswordInput > div > div > input:focus {
    border-color:rgba(96,165,250,0.5) !important;
    box-shadow:0 0 0 3px rgba(96,165,250,0.1) !important;
}

/* ── Radio (quiz options) ── */
.stRadio > div { gap:10px !important; }
.stRadio > div > label {
    background:rgba(15,23,42,0.7) !important;
    border:1px solid rgba(96,165,250,0.15) !important;
    border-radius:11px !important;
    padding:12px 18px !important;
    cursor:pointer !important;
    transition:all 0.18s !important;
    color:#94a3b8 !important; font-size:14px !important;
    width:100% !important; display:block !important;
}
.stRadio > div > label:hover {
    border-color:rgba(96,165,250,0.42) !important;
    color:#e2e8f8 !important;
    background:rgba(29,78,216,0.13) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background:rgba(15,23,42,0.6) !important;
    border-radius:13px !important; padding:4px !important;
    border:1px solid rgba(96,165,250,0.12) !important; gap:3px !important;
}
.stTabs [data-baseweb="tab"] {
    background:transparent !important; color:#64748b !important;
    border-radius:10px !important;
    font-family:'Syne',sans-serif !important; font-weight:600 !important;
    padding:9px 18px !important; transition:all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background:linear-gradient(135deg,#1d4ed8,#7c3aed) !important;
    color:#fff !important;
}

/* ── Misc ── */
.stSuccess { border-radius:12px !important; border-left:3px solid #10b981 !important; background:rgba(16,185,129,0.08) !important; }
.stError   { border-radius:12px !important; border-left:3px solid #ef4444 !important; }
.stInfo    { border-radius:12px !important; border-left:3px solid #3b82f6 !important; background:rgba(59,130,246,0.08) !important; }
hr { border-color:rgba(96,165,250,0.08) !important; }
.stProgress > div > div > div { background:linear-gradient(90deg,#1d4ed8,#7c3aed) !important; border-radius:100px !important; }
.stRadio label, .stSelectbox label, .stTextInput label {
    color:#64748b !important; font-size:11px !important;
    font-weight:500 !important; letter-spacing:.06em !important; text-transform:uppercase !important;
}
.streamlit-expanderHeader {
    background:rgba(15,23,42,0.6) !important;
    border:1px solid rgba(96,165,250,0.13) !important;
    border-radius:11px !important; color:#94a3b8 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────────────────────────────────────
DB_PATH = "neuralpath.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
        full_name TEXT, email TEXT, created_at TEXT, last_login TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, login_time TEXT, status TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT, timestamp TEXT, domain TEXT,
        gpa REAL, python_skill INTEGER, ml_skill INTEGER,
        web_interest INTEGER, ai_interest INTEGER,
        predicted_career TEXT)""")
    # ── Migration: safely add any missing columns to old DBs ──
    existing_cols = [row[1] for row in c.execute("PRAGMA table_info(sessions)").fetchall()]
    migrations = {
        "domain": "ALTER TABLE sessions ADD COLUMN domain TEXT DEFAULT 'General'",
    }
    for col, sql in migrations.items():
        if col not in existing_cols:
            try:
                c.execute(sql)
            except Exception:
                pass
    conn.commit(); conn.close()

def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password, full_name, email):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO users (username,password_hash,full_name,email,created_at,last_login) VALUES (?,?,?,?,?,?)",
            (username, _hash(password), full_name, email,
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "—"))
        conn.commit(); conn.close()
        return True, "Account created!"
    except sqlite3.IntegrityError:
        return False, "Username already taken."

def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password_hash, full_name FROM users WHERE username=?", (username,))
    row = c.fetchone()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if row and row[0] == _hash(password):
        conn.execute("UPDATE users SET last_login=? WHERE username=?", (now, username))
        conn.execute("INSERT INTO login_logs VALUES (NULL,?,?,?)", (username, now, "success"))
        conn.commit(); conn.close(); return True, row[1]
    else:
        if row: conn.execute("INSERT INTO login_logs VALUES (NULL,?,?,?)", (username, now, "failed")); conn.commit()
        conn.close(); return False, None

def save_prediction(username, domain, gpa, py, ml, web, ai, career):
    # Always run init_db first so migration has run before any INSERT
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO sessions (username,timestamp,domain,gpa,python_skill,ml_skill,web_interest,ai_interest,predicted_career) VALUES (?,?,?,?,?,?,?,?,?)",
        (username, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(domain), float(gpa), int(py), int(ml), int(web), int(ai), str(career)))
    conn.commit(); conn.close()

def get_sessions(username):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM sessions WHERE username=? ORDER BY timestamp", conn, params=(username,))
    conn.close(); return df

def get_login_logs(username):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT login_time, status FROM login_logs WHERE username=? ORDER BY login_time DESC LIMIT 25",
        conn, params=(username,))
    conn.close(); return df

def count_users():
    conn = sqlite3.connect(DB_PATH)
    n = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close(); return n

init_db()

# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN DATA
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS = {
    "Data Science & Analytics": {
        "icon": "📊", "color": "#3b82f6", "rgb": (59,130,246),
        "desc": "Work with data, statistics & machine learning to uncover insights",
        "career": "Data Scientist",
        "quiz": [
            {"q":"How comfortable are you with maths & statistics?",
             "opts":[("I avoid maths wherever possible","1"),
                     ("Basic arithmetic & percentages only","3"),
                     ("Comfortable with algebra & basic stats","5"),
                     ("Know probability, distributions & hypothesis testing","7"),
                     ("Love linear algebra, calculus & statistical inference","10")]},
            {"q":"Have you ever explored a dataset to find patterns?",
             "opts":[("Never heard of datasets","1"),
                     ("Opened a CSV file in Excel","3"),
                     ("Used pandas/R to explore data","5"),
                     ("Built dashboards or visualisations","7"),
                     ("Done end-to-end EDA with statistical insights","10")]},
            {"q":"How much Python or R programming do you know?",
             "opts":[("No coding experience","1"),
                     ("Know variables and basic loops","3"),
                     ("Write small scripts independently","5"),
                     ("Use data libraries (pandas, numpy, ggplot)","7"),
                     ("Write clean, reusable data pipelines","10")]},
            {"q":"Have you trained any machine learning models?",
             "opts":[("What is ML?","1"),
                     ("Watched tutorials but not tried","3"),
                     ("Trained a simple model (e.g. linear regression)","5"),
                     ("Tuned hyperparameters & evaluated models","7"),
                     ("Deploy models and monitor them in production","10")]},
            {"q":"What is your academic/GPA performance?",
             "opts":[("Below average","4"),("Average","5.5"),
                     ("Good","6.5"),("Very good","7.5"),("Excellent","9")]},
        ],
        "skill_keys": ["python","ml","web","ai"],
        "weights":    [1, 1, 0, 0.5],   # how quiz Q maps to skill axes
    },
    "Machine Learning & AI": {
        "icon": "🤖", "color": "#8b5cf6", "rgb": (139,92,246),
        "desc": "Build intelligent systems, neural networks & AI-powered products",
        "career": "ML Engineer",
        "quiz": [
            {"q":"How well do you understand linear algebra & calculus?",
             "opts":[("Not at all","1"),("Recall school basics","3"),
                     ("Comfortable with matrices & derivatives","5"),
                     ("Apply them in ML context (gradients, PCA)","7"),
                     ("Research-level understanding","10")]},
            {"q":"Have you built any deep learning models?",
             "opts":[("Never tried","1"),("Followed a YouTube tutorial","3"),
                     ("Built a CNN or RNN from scratch","5"),
                     ("Fine-tuned pre-trained models (BERT, ResNet)","7"),
                     ("Designed novel architectures","10")]},
            {"q":"How familiar are you with PyTorch or TensorFlow?",
             "opts":[("Never used them","1"),("Installed but confused","3"),
                     ("Train basic models with them","5"),
                     ("Custom training loops, optimisers","7"),
                     ("Contribute to or extend frameworks","10")]},
            {"q":"How do you approach reading AI research papers?",
             "opts":[("I don't read papers","1"),("Read abstracts sometimes","3"),
                     ("Read full papers with effort","5"),
                     ("Reproduce results from papers","7"),
                     ("Publish or peer-review papers","10")]},
            {"q":"What is your academic/GPA performance?",
             "opts":[("Below average","4"),("Average","5.5"),
                     ("Good","6.5"),("Very good","7.5"),("Excellent","9")]},
        ],
        "skill_keys": ["python","ml","web","ai"],
        "weights":    [0.8, 1, 0, 1],
    },
    "Web Development": {
        "icon": "🌐", "color": "#10b981", "rgb": (16,185,129),
        "desc": "Create websites, apps & digital products people love to use",
        "career": "Web Developer",
        "quiz": [
            {"q":"How comfortable are you with HTML & CSS?",
             "opts":[("Never written a tag","1"),("Can make a simple page","3"),
                     ("Build responsive layouts","5"),("Use frameworks like Tailwind","7"),
                     ("Pixel-perfect, accessible UIs","10")]},
            {"q":"How much JavaScript do you know?",
             "opts":[("What is JS?","1"),("Basic DOM manipulation","3"),
                     ("Async/await, fetch, ES6+","5"),
                     ("React / Vue / frameworks","7"),
                     ("TypeScript, state management, performance","10")]},
            {"q":"Have you built a backend or API?",
             "opts":[("Never","1"),("Used drag-and-drop builders","3"),
                     ("Simple Flask/Express routes","5"),
                     ("REST API with auth & database","7"),
                     ("Microservices, GraphQL, scalable architecture","10")]},
            {"q":"How familiar are you with databases?",
             "opts":[("No idea","1"),("Used spreadsheets as data","3"),
                     ("Written basic SQL queries","5"),
                     ("Designed schemas, used ORMs","7"),
                     ("Optimised queries, handles migrations","10")]},
            {"q":"What is your academic/GPA performance?",
             "opts":[("Below average","4"),("Average","5.5"),
                     ("Good","6.5"),("Very good","7.5"),("Excellent","9")]},
        ],
        "skill_keys": ["python","ml","web","ai"],
        "weights":    [0.3, 0, 1, 0],
    },
    "AI Research": {
        "icon": "🔬", "color": "#f59e0b", "rgb": (245,158,11),
        "desc": "Push the boundaries of AI through experiments, papers & breakthroughs",
        "career": "AI Research Scientist",
        "quiz": [
            {"q":"How deeply do you understand backpropagation?",
             "opts":[("Never heard of it","1"),("Know it updates weights","3"),
                     ("Can derive it manually","5"),
                     ("Implement custom gradient flows","7"),
                     ("Research novel optimisation methods","10")]},
            {"q":"How many AI/ML papers have you read end-to-end?",
             "opts":[("Zero","1"),("1–2 casually","3"),
                     ("10+ with understanding","5"),
                     ("50+ and implemented some","7"),
                     ("Hundreds; I follow arxiv daily","10")]},
            {"q":"Have you reproduced or extended research results?",
             "opts":[("Never tried","1"),("Followed someone else's code","3"),
                     ("Reproduced a paper independently","5"),
                     ("Extended a paper with new experiments","7"),
                     ("Published original research","10")]},
            {"q":"How strong is your mathematics background?",
             "opts":[("School level only","1"),("Some university maths","3"),
                     ("Probability theory & linear algebra solid","5"),
                     ("Measure theory, convex optimisation","7"),
                     ("Research-grade mathematical maturity","10")]},
            {"q":"What is your academic/GPA performance?",
             "opts":[("Below average","4"),("Average","5.5"),
                     ("Good","6.5"),("Very good","7.5"),("Excellent","9")]},
        ],
        "skill_keys": ["python","ml","web","ai"],
        "weights":    [0.7, 1, 0, 1],
    },
    "Full-Stack AI Dev": {
        "icon": "🚀", "color": "#ef4444", "rgb": (239,68,68),
        "desc": "Blend ML + web skills to ship AI-powered products end-to-end",
        "career": "Full-Stack AI Developer",
        "quiz": [
            {"q":"Can you build a REST API and connect it to a frontend?",
             "opts":[("No idea how","1"),("Built a simple endpoint","3"),
                     ("Full CRUD API with React frontend","5"),
                     ("Authentication, state, real-time updates","7"),
                     ("Production-grade, CI/CD, deployed","10")]},
            {"q":"Have you integrated an ML model into a web app?",
             "opts":[("Never tried","1"),("Loaded a model in a notebook","3"),
                     ("Served model via Flask/FastAPI","5"),
                     ("Built a polished AI-powered product","7"),
                     ("Scaled ML serving with queues & caching","10")]},
            {"q":"How comfortable are you with cloud deployment?",
             "opts":[("Never deployed anything","1"),("Used Heroku once","3"),
                     ("Deployed on AWS/GCP/Azure","5"),
                     ("Containers, serverless, load balancers","7"),
                     ("DevOps: IaC, monitoring, auto-scaling","10")]},
            {"q":"How familiar are you with LLMs & prompt engineering?",
             "opts":[("What is an LLM?","1"),("Used ChatGPT casually","3"),
                     ("Built apps with OpenAI/Anthropic APIs","5"),
                     ("Fine-tuned models, RAG pipelines","7"),
                     ("Train or contribute to foundation models","10")]},
            {"q":"What is your academic/GPA performance?",
             "opts":[("Below average","4"),("Average","5.5"),
                     ("Good","6.5"),("Very good","7.5"),("Excellent","9")]},
        ],
        "skill_keys": ["python","ml","web","ai"],
        "weights":    [0.8, 0.7, 0.8, 0.7],
    },
}

CAREER_ICONS = {
    "Data Scientist":"📊","ML Engineer":"⚙️","Web Developer":"🌐",
    "AI Research Scientist":"🔬","Full-Stack AI Developer":"🚀",
}
CAREER_COLORS = {
    "Data Scientist":"#3b82f6","ML Engineer":"#8b5cf6",
    "Web Developer":"#10b981","AI Research Scientist":"#f59e0b",
    "Full-Stack AI Developer":"#ef4444",
}
CAREER_RGB = {
    "Data Scientist":(59,130,246),"ML Engineer":(139,92,246),
    "Web Developer":(16,185,129),"AI Research Scientist":(245,158,11),
    "Full-Stack AI Developer":(239,68,68),
}

ROADMAPS = {
    "Data Scientist":[
        ("Python Basics","2 wks","🐍"),("Statistics","3 wks","📐"),
        ("Data Wrangling","2 wks","🗃️"),("EDA","2 wks","🔍"),
        ("ML Fundamentals","4 wks","🤖"),("Visualisation","2 wks","📈"),
        ("Portfolio","4 wks","💼"),("Job Ready!","","🎯"),
    ],
    "ML Engineer":[
        ("Python & OOP","2 wks","🐍"),("Linear Algebra","3 wks","📐"),
        ("Core ML","4 wks","🧠"),("Deep Learning","5 wks","🔥"),
        ("MLOps","3 wks","☁️"),("Optimisation","2 wks","⚡"),
        ("E2E Pipeline","4 wks","🔄"),("Job Ready!","","🎯"),
    ],
    "Web Developer":[
        ("HTML & CSS","2 wks","🎨"),("JavaScript","3 wks","⚡"),
        ("React/Vue","4 wks","⚛️"),("Backend","3 wks","🔧"),
        ("Databases","2 wks","🗄️"),("APIs & Auth","2 wks","🔐"),
        ("Deploy","3 wks","🚀"),("Job Ready!","","🎯"),
    ],
    "AI Research Scientist":[
        ("Advanced Python","1 wk","🐍"),("Advanced Maths","4 wks","📐"),
        ("ML Theory","5 wks","📚"),("DL Papers","5 wks","🔬"),
        ("Research Methods","3 wks","🧪"),("Reproduce Paper","6 wks","✏️"),
        ("PhD/MS Apps","Ongoing","🎓"),("Job Ready!","","🎯"),
    ],
    "Full-Stack AI Developer":[
        ("Python + JS","3 wks","💻"),("ML Basics","4 wks","🤖"),
        ("React + FastAPI","4 wks","⚛️"),("ML in Web","3 wks","🔗"),
        ("Prompt Eng.","2 wks","💬"),("Cloud Deploy","3 wks","☁️"),
        ("AI SaaS Build","4 wks","🚀"),("Job Ready!","","🎯"),
    ],
}

IDEAL_PROFILES = {
    "Data Scientist":[7,8,3,6],"ML Engineer":[9,9,2,7],
    "Web Developer":[5,2,9,2],"AI Research Scientist":[8,9,2,10],
    "Full-Stack AI Developer":[8,7,8,7],
}

COURSES = {
    "Python":{
        "Beginner":[
            ("Python for Everybody – Coursera",     "https://www.coursera.org/specializations/python"),
            ("Automate the Boring Stuff (Free)",    "https://automatetheboringstuff.com"),
            ("Python Basics – Codecademy",          "https://www.codecademy.com/learn/learn-python-3"),
            ("100 Days of Code – Udemy",            "https://www.udemy.com/course/100-days-of-code/"),
        ],
        "Intermediate":[
            ("Intermediate Python – Udemy",         "https://www.udemy.com/course/python-beyond-the-basics/"),
            ("Real Python Tutorials",               "https://realpython.com"),
            ("Python OOP – Corey Schafer YouTube",  "https://www.youtube.com/playlist?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc"),
            ("Python Testing with pytest",          "https://testdriven.io/blog/pytest-for-beginners/"),
        ],
        "Advanced":[
            ("Python Design Patterns",              "https://refactoring.guru/design-patterns/python"),
            ("High Performance Python (O'Reilly)", "https://www.oreilly.com/library/view/high-performance-python/9781492055013/"),
            ("Fluent Python – Book",                "https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/"),
            ("Python Concurrency & Async IO",       "https://realpython.com/async-io-python/"),
        ],
    },
    "Machine Learning":{
        "Beginner":[
            ("ML Crash Course – Google",            "https://developers.google.com/machine-learning/crash-course"),
            ("Intro to ML – Kaggle (Free)",         "https://www.kaggle.com/learn/intro-to-machine-learning"),
            ("ML for Beginners – Microsoft",        "https://github.com/microsoft/ML-For-Beginners"),
            ("Supervised ML – Coursera",            "https://www.coursera.org/learn/machine-learning"),
        ],
        "Intermediate":[
            ("ML Specialization – Andrew Ng",       "https://www.coursera.org/specializations/machine-learning-introduction"),
            ("Hands-On ML with Sklearn & TF",       "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/"),
            ("Feature Engineering – Kaggle",        "https://www.kaggle.com/learn/feature-engineering"),
            ("Applied ML – Coursera",               "https://www.coursera.org/learn/python-machine-learning"),
        ],
        "Advanced":[
            ("Deep Learning Specialization",        "https://www.coursera.org/specializations/deep-learning"),
            ("Fast.ai – Practical Deep Learning",   "https://course.fast.ai"),
            ("MLOps Specialization – Coursera",     "https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops"),
            ("Full Stack Deep Learning",            "https://fullstackdeeplearning.com"),
        ],
    },
    "Web Dev":{
        "Beginner":[
            ("The Odin Project (Free)",             "https://www.theodinproject.com"),
            ("freeCodeCamp (Free)",                 "https://www.freecodecamp.org"),
            ("HTML & CSS – Codecademy",             "https://www.codecademy.com/learn/learn-html"),
            ("Web Dev Bootcamp – Udemy",            "https://www.udemy.com/course/the-web-developer-bootcamp/"),
        ],
        "Intermediate":[
            ("Full-Stack Open (Free)",              "https://fullstackopen.com"),
            ("React Official Docs",                 "https://react.dev"),
            ("Node.js – The Complete Guide",        "https://www.udemy.com/course/nodejs-the-complete-guide/"),
            ("CS50 Web Programming",                "https://cs50.harvard.edu/web/"),
        ],
        "Advanced":[
            ("System Design for Web Apps",          "https://www.educative.io/courses/web-application-software-architecture-101"),
            ("Advanced React Patterns",             "https://www.patterns.dev"),
            ("Next.js Official Docs",               "https://nextjs.org/docs"),
            ("Web Security Academy (Free)",         "https://portswigger.net/web-security"),
        ],
    },
    "AI":{
        "Beginner":[
            ("AI for Everyone – Andrew Ng",         "https://www.coursera.org/learn/ai-for-everyone"),
            ("Elements of AI (Free)",               "https://www.elementsofai.com"),
            ("Intro to AI – Udacity",               "https://www.udacity.com/course/intro-to-artificial-intelligence--cs271"),
            ("ChatGPT Prompt Engineering – DeepLearning.AI","https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/"),
        ],
        "Intermediate":[
            ("HuggingFace NLP Course (Free)",       "https://huggingface.co/learn/nlp-course/chapter1/1"),
            ("LangChain – Build LLM Apps",          "https://www.youtube.com/watch?v=lG7Uxts9SXs"),
            ("Generative AI with LLMs – Coursera",  "https://www.coursera.org/learn/generative-ai-with-llms"),
            ("Practical AI – Fast.ai",              "https://course.fast.ai"),
        ],
        "Advanced":[
            ("Attention is All You Need (Paper)",   "https://arxiv.org/abs/1706.03762"),
            ("Stanford CS224N – NLP with DL",       "https://web.stanford.edu/class/cs224n/"),
            ("Stanford CS231N – CNNs",              "http://cs231n.stanford.edu/"),
            ("The Little Book of Deep Learning",    "https://fleuret.org/public/lbdl.pdf"),
        ],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# MODEL
# ─────────────────────────────────────────────────────────────────────────────
CAREER_LABELS = {0:"Data Scientist",1:"ML Engineer",2:"Web Developer",
                 3:"AI Research Scientist",4:"Full-Stack AI Developer"}

def predict_career(gpa, py, ml, web, ai):
    # Replace body with: return CAREER_LABELS[model.predict([[gpa,py,ml,web,ai]])[0]]
    scores = {
        0: gpa*0.3 + ml*0.5 + ai*0.2,
        1: py*0.4  + ml*0.4 + ai*0.2,
        2: web*0.7 + py*0.3,
        3: ai*0.5  + ml*0.3 + gpa*0.2,
        4: py*0.3  + web*0.3 + ai*0.2 + ml*0.2,
    }
    return CAREER_LABELS[max(scores, key=scores.get)]

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
DEFAULTS = {
    "logged_in": False, "username": "", "full_name": "",
    "screen": "domain",          # domain | quiz | results
    "selected_domain": None,
    "extra_domains": [],          # additional domain quizzes taken
    "quiz_step": 0,
    "domain_scores": {},          # domain_name -> {py,ml,web,ai,gpa}
    "career_result": None,
    "completed_steps": {},   # career -> set of completed step indices
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def metric_pill(label, value, icon, color):
    return (f'<div style="background:rgba(15,23,42,0.7);border:1px solid {color}33;'
            f'border-radius:14px;padding:1rem 1.2rem;text-align:center;">'
            f'<div style="font-size:24px;margin-bottom:3px;">{icon}</div>'
            f'<div style="font-family:Syne,sans-serif;font-size:19px;font-weight:700;color:{color};">{value}</div>'
            f'<div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:.07em;margin-top:2px;">{label}</div>'
            f'</div>')

def top_nav(show_logout=True, show_retake=False):
    """Render persistent top nav bar with profile chip when logged in."""
    uname     = st.session_state.get("username","")
    fname     = st.session_state.get("full_name","")
    logged_in = st.session_state.get("logged_in", False)

    left, right = st.columns([1, 0.55])
    with left:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;padding:0.9rem 0 0.7rem;">'
            '<span style="font-size:26px;">🧠</span>'
            '<span style="font-family:Syne,sans-serif;font-weight:800;font-size:20px;'
            'background:linear-gradient(135deg,#60a5fa,#a78bfa);'
            '-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">'
            'NeuralPath</span>'
            '<span style="background:rgba(96,165,250,0.12);border:1px solid rgba(96,165,250,0.22);'
            'border-radius:20px;padding:2px 11px;font-size:11px;color:#60a5fa;font-weight:600;">'
            'AI Career Advisor</span>'
            '</div>',
            unsafe_allow_html=True
        )
    with right:
        if logged_in:
            # Profile chip + action buttons all in one row
            nav_parts = st.columns([1.4, 1, 1] if show_retake else [2, 1])
            with nav_parts[0]:
                # Profile chip
                initial = fname[0].upper() if fname else "?"
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:9px;'
                    f'background:rgba(15,23,42,0.7);border:1px solid rgba(96,165,250,0.18);'
                    f'border-radius:40px;padding:5px 14px 5px 6px;margin-top:10px;">'
                    f'<div style="width:30px;height:30px;border-radius:50%;'
                    f'background:linear-gradient(135deg,#1d4ed8,#7c3aed);'
                    f'display:flex;align-items:center;justify-content:center;'
                    f'font-family:Syne,sans-serif;font-size:13px;font-weight:700;color:#fff;flex-shrink:0;">'
                    f'{initial}</div>'
                    f'<div>'
                    f'<div style="font-family:Syne,sans-serif;font-weight:700;font-size:13px;color:#e2e8f8;line-height:1.1;">{fname}</div>'
                    f'<div style="font-size:10px;color:#475569;">@{uname}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            if show_retake:
                with nav_parts[1]:
                    st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
                    if st.button("🔄 Retake", use_container_width=True):
                        st.session_state.screen = "domain"
                        st.session_state.selected_domain = None
                        st.session_state.extra_domains = []
                        st.session_state.quiz_step = 0
                        st.session_state.domain_scores = {}
                        st.session_state.career_result = None
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with nav_parts[2]:
                    st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
                    if st.button("Logout →", use_container_width=True):
                        for k, v in DEFAULTS.items():
                            st.session_state[k] = v
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                with nav_parts[1]:
                    st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
                    if st.button("Logout →", use_container_width=True):
                        for k, v in DEFAULTS.items():
                            st.session_state[k] = v
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<hr style="margin:0 0 0.8rem;">', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# AUTH SCREEN
# ─────────────────────────────────────────────────────────────────────────────
def show_auth():
    top_nav(show_logout=False)

    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 1.2rem;">
        <div style="font-size:50px;margin-bottom:10px;">🧠</div>
        <h1 style="font-family:Syne,sans-serif;font-size:clamp(1.9rem,4.5vw,3rem);font-weight:800;
            background:linear-gradient(135deg,#60a5fa 0%,#a78bfa 50%,#34d399 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
            margin:0 0 8px;line-height:1.1;">NeuralPath</h1>
        <p style="color:#475569;font-size:15px;margin:0;">
            Pick your domain · Take a smart quiz · Get your career path
        </p>
    </div>
    """, unsafe_allow_html=True)

    total = count_users()
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(metric_pill("Students", str(total), "👩‍🎓", "#60a5fa"), unsafe_allow_html=True)
    with c2: st.markdown(metric_pill("Career Paths", "5", "🎯", "#a78bfa"), unsafe_allow_html=True)
    with c3: st.markdown(metric_pill("Domain Quizzes", "5", "⚡", "#34d399"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, col_form, _ = st.columns([1, 1.5, 1])
    with col_form:
        tab_in, tab_reg = st.tabs(["🔑  Sign In", "✨  Register"])
        with tab_in:
            with st.form("login_form", clear_on_submit=False):
                uname = st.text_input("Username", placeholder="your_username")
                pwd   = st.text_input("Password", type="password", placeholder="••••••••")
                sub   = st.form_submit_button("Sign In →", use_container_width=True)
            if sub:
                if not uname or not pwd:
                    st.error("Please fill in both fields.")
                else:
                    ok, name = login_user(uname, pwd)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.username  = uname
                        st.session_state.full_name = name or uname
                        st.session_state.screen    = "domain"
                        st.success(f"Welcome back, {name or uname}! 🎉")
                        time.sleep(0.5); st.rerun()
                    else:
                        st.error("Invalid username or password.")
        with tab_reg:
            with st.form("reg_form", clear_on_submit=True):
                rn  = st.text_input("Full Name",        placeholder="Alex Kumar")
                re  = st.text_input("Email",            placeholder="alex@example.com")
                ru  = st.text_input("Username",         placeholder="alex_kumar")
                rp  = st.text_input("Password",         type="password", placeholder="min 6 chars")
                rp2 = st.text_input("Confirm Password", type="password", placeholder="repeat")
                rbtn= st.form_submit_button("Create Account →", use_container_width=True)
            if rbtn:
                if not all([rn,re,ru,rp,rp2]): st.error("Fill in all fields.")
                elif len(rp) < 6:              st.error("Password ≥ 6 characters.")
                elif rp != rp2:                st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(ru, rp, rn, re)
                    st.success(msg) if ok else st.error(msg)

# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN SELECTION SCREEN
# ─────────────────────────────────────────────────────────────────────────────
def show_domain_select():
    top_nav(show_logout=True, show_retake=False)

    full_name = st.session_state.full_name
    sessions  = get_sessions(st.session_state.username)
    last_c    = sessions["predicted_career"].iloc[-1] if len(sessions) > 0 else None

    # Welcome
    st.markdown(
        f'<div style="background:linear-gradient(135deg,rgba(29,78,216,0.14),rgba(124,58,237,0.14));'
        f'border:1px solid rgba(96,165,250,0.16);border-radius:18px;'
        f'padding:1.4rem 1.8rem;margin-bottom:1.8rem;'
        f'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">'
        f'<div>'
        f'<div style="font-size:12px;color:#475569;text-transform:uppercase;letter-spacing:.08em;">Welcome back</div>'
        f'<div style="font-family:Syne,sans-serif;font-size:24px;font-weight:800;color:#e2e8f8;">{full_name} 👋</div>'
        f'<div style="font-size:13px;color:#475569;margin-top:2px;">@{st.session_state.username}</div>'
        f'</div>'
        f'<div style="text-align:right;">'
        f'<div style="font-size:12px;color:#475569;text-transform:uppercase;letter-spacing:.07em;">Last prediction</div>'
        f'<div style="font-size:16px;font-weight:600;color:#60a5fa;margin-top:2px;">'
        f'{last_c or "None yet"}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<h2 style="font-family:Syne,sans-serif;font-weight:800;font-size:1.5rem;'
        'color:#e2e8f8;margin-bottom:6px;">Choose your area of interest</h2>'
        '<p style="color:#475569;font-size:14px;margin-bottom:1.4rem;">'
        'Select the domain you\'re most curious about. We\'ll ask you 5 questions tailored to that field.</p>',
        unsafe_allow_html=True
    )

    # Domain cards — 3 + 2 layout
    domain_names = list(DOMAINS.keys())
    row1 = domain_names[:3]
    row2 = domain_names[3:]

    for row in [row1, row2]:
        cols = st.columns(len(row))
        for col, dname in zip(cols, row):
            d = DOMAINS[dname]
            r,g,b = d["rgb"]
            with col:
                st.markdown(
                    f'<div style="background:rgba(15,23,42,0.65);'
                    f'border:1.5px solid rgba({r},{g},{b},0.3);'
                    f'border-radius:16px;padding:1.6rem 1.3rem;'
                    f'transition:all 0.2s;cursor:pointer;margin-bottom:4px;">'
                    f'<div style="font-size:36px;margin-bottom:10px;">{d["icon"]}</div>'
                    f'<div style="font-family:Syne,sans-serif;font-weight:700;font-size:15px;'
                    f'color:#e2e8f8;margin-bottom:6px;">{dname}</div>'
                    f'<div style="font-size:12px;color:#64748b;line-height:1.5;">{d["desc"]}</div>'
                    f'<div style="margin-top:12px;display:inline-block;'
                    f'background:rgba({r},{g},{b},0.15);border:1px solid rgba({r},{g},{b},0.35);'
                    f'border-radius:20px;padding:3px 12px;font-size:11px;color:{d["color"]};font-weight:600;">'
                    f'{d["career"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button(f"Start Quiz →", key=f"pick_{dname}", use_container_width=True):
                    st.session_state.selected_domain = dname
                    st.session_state.quiz_step       = 0
                    st.session_state.screen          = "quiz"
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# QUIZ SCREEN
# ─────────────────────────────────────────────────────────────────────────────
def show_quiz():
    dname = st.session_state.selected_domain
    d     = DOMAINS[dname]
    step  = st.session_state.quiz_step
    quiz  = d["quiz"]
    total = len(quiz)
    r,g,b = d["rgb"]

    top_nav(show_logout=True, show_retake=False)

    # Domain badge
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:8px;'
        f'background:rgba({r},{g},{b},0.12);border:1px solid rgba({r},{g},{b},0.3);'
        f'border-radius:20px;padding:4px 14px;font-size:13px;color:{d["color"]};'
        f'font-weight:600;margin-bottom:1.2rem;">'
        f'{d["icon"]} {dname} Quiz</div>',
        unsafe_allow_html=True
    )

    # Progress
    st.progress((step) / total)
    st.markdown(
        f'<p style="color:#475569;font-size:12px;text-align:right;margin-top:-4px;margin-bottom:1.5rem;">'
        f'Question {step+1} of {total}</p>',
        unsafe_allow_html=True
    )

    q = quiz[step]

    # Question card
    _, qcol, _ = st.columns([0.5, 3, 0.5])
    with qcol:
        st.markdown(
            f'<div style="background:rgba(15,23,42,0.65);border:1px solid rgba({r},{g},{b},0.2);'
            f'border-radius:18px;padding:2rem 2.2rem;margin-bottom:1.2rem;text-align:center;">'
            f'<div style="font-size:44px;margin-bottom:12px;">{d["icon"]}</div>'
            f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:.1em;'
            f'color:{d["color"]};font-weight:600;margin-bottom:10px;">{dname}</div>'
            f'<h2 style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:700;'
            f'color:#e2e8f8;line-height:1.4;">{q["q"]}</h2>'
            f'</div>',
            unsafe_allow_html=True
        )

        option_labels = [opt[0] for opt in q["opts"]]
        chosen = st.radio("Select your answer:", options=option_labels,
                          key=f"q_{dname}_{step}", label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns([1, 3])
        with b1:
            if step > 0:
                if st.button("← Back", use_container_width=True):
                    st.session_state.quiz_step -= 1
                    st.rerun()
        with b2:
            btn_lbl = "Next Question →" if step < total-1 else f"🚀 See My {d['career']} Path!"
            if st.button(btn_lbl, use_container_width=True):
                val = float(next(v for (lbl,v) in q["opts"] if lbl == chosen))
                # Store answer
                if dname not in st.session_state.domain_scores:
                    st.session_state.domain_scores[dname] = {}
                st.session_state.domain_scores[dname][f"q{step}"] = val

                if step < total-1:
                    st.session_state.quiz_step += 1
                else:
                    # Extract only quiz answers q0..qN, skip _computed key
                    raw = st.session_state.domain_scores[dname]
                    answers = [float(raw[f"q{i}"]) for i in range(total) if f"q{i}" in raw]
                    w = d["weights"]
                    gpa  = float(answers[-1]) if answers else 7.0
                    skill_vals = answers[:-1] if len(answers) > 1 else [5.0]
                    base = sum(skill_vals) / max(len(skill_vals), 1)
                    py   = min(10, max(1, round(base * max(w[0], 0.1))))
                    ml   = min(10, max(1, round(base * max(w[1], 0.1))))
                    web  = min(10, max(1, round(base * max(w[2], 0.1))))
                    ai   = min(10, max(1, round(base * max(w[3], 0.1))))
                    st.session_state.domain_scores[dname]["_computed"] = {
                        "gpa":gpa,"py":py,"ml":ml,"web":web,"ai":ai
                    }
                    career = predict_career(gpa, py, ml, web, ai)
                    save_prediction(st.session_state.username, dname, gpa, py, ml, web, ai, career)
                    st.session_state.career_result = career
                    st.session_state.screen = "results"
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS SCREEN
# ─────────────────────────────────────────────────────────────────────────────
def show_results():
    career    = st.session_state.career_result
    dname     = st.session_state.selected_domain
    d         = DOMAINS[dname]
    username  = st.session_state.username
    full_name = st.session_state.full_name

    computed  = st.session_state.domain_scores.get(dname, {}).get("_computed", {})
    gpa  = computed.get("gpa", 7)
    py   = computed.get("py", 5)
    ml   = computed.get("ml", 5)
    web  = computed.get("web", 5)
    ai   = computed.get("ai", 5)

    c_color = CAREER_COLORS.get(career, "#60a5fa")
    c_icon  = CAREER_ICONS.get(career, "🎯")
    r,g,b   = CAREER_RGB.get(career, (96,165,250))
    dr,dg,db= d["rgb"]

    # Determine overall skill level from average score
    avg_skill = (py + ml + web + ai) / 4
    overall_level = "Beginner" if avg_skill <= 4 else "Intermediate" if avg_skill <= 7 else "Advanced"

    top_nav(show_logout=True, show_retake=True)

    # ── PROFILE STRIP (top of page) ──────────────────────────────────────────
    hist_top = get_sessions(username)
    n_sess   = len(hist_top)
    domains_tried = hist_top["domain"].nunique() if "domain" in hist_top.columns and n_sess > 0 else 0

    st.markdown(
        f'''<div style="
            background:linear-gradient(135deg,rgba({r},{g},{b},0.12),rgba({dr},{dg},{db},0.08));
            border:1px solid rgba({r},{g},{b},0.25);border-radius:18px;
            padding:1rem 1.6rem;margin-bottom:1.2rem;
            display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
            <div style="width:48px;height:48px;border-radius:50%;flex-shrink:0;
                background:linear-gradient(135deg,#{r:02x}{g:02x}{b:02x},{c_color});
                display:flex;align-items:center;justify-content:center;
                font-family:Syne,sans-serif;font-size:20px;font-weight:800;color:#fff;">
                {full_name[0].upper()}</div>
            <div style="flex:1;min-width:160px;">
                <div style="font-family:Syne,sans-serif;font-weight:800;font-size:18px;color:#e2e8f8;">{full_name}</div>
                <div style="font-size:12px;color:#475569;">@{username}</div>
            </div>
            <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;">
                <div style="text-align:center;background:rgba(96,165,250,0.1);border-radius:10px;padding:6px 14px;">
                    <div style="font-family:Syne,sans-serif;font-size:17px;font-weight:700;color:#60a5fa;">{n_sess}</div>
                    <div style="font-size:10px;color:#475569;text-transform:uppercase;">Sessions</div>
                </div>
                <div style="text-align:center;background:rgba(167,139,250,0.1);border-radius:10px;padding:6px 14px;">
                    <div style="font-family:Syne,sans-serif;font-size:17px;font-weight:700;color:#a78bfa;">{domains_tried}</div>
                    <div style="font-size:10px;color:#475569;text-transform:uppercase;">Domains</div>
                </div>
                <div style="background:rgba({r},{g},{b},0.12);border:1px solid rgba({r},{g},{b},0.3);
                    border-radius:20px;padding:5px 14px;font-size:13px;color:{c_color};font-weight:700;">
                    {c_icon} {career}
                </div>
                <div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);
                    border-radius:20px;padding:5px 14px;font-size:12px;color:#34d399;font-weight:600;">
                    {overall_level} Level
                </div>
            </div>
        </div>''',
        unsafe_allow_html=True
    )

    # ── SKILL PILLS ──────────────────────────────────────────────────────────
    sc = st.columns(5)
    for col,(lbl,val,ico,clr) in zip(sc, [
        ("GPA",f"{gpa:.1f}","🎓","#94a3b8"),
        ("Python",py,"🐍","#60a5fa"),
        ("ML",ml,"🤖","#a78bfa"),
        ("Web Dev",web,"🌐","#34d399"),
        ("AI",ai,"🧠","#f59e0b"),
    ]):
        with col: st.markdown(metric_pill(lbl, str(val), ico, clr), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 6 TABS ───────────────────────────────────────────────────────────────
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "🗺️ Learning Roadmap",
        "📊 Skill Comparison",
        "📚 Courses",
        "📈 Progress",
        "👤 My Profile",
        "🔐 Login History",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — VISUAL ROADMAP
    # ══════════════════════════════════════════════════════════════════════════
    with t1:
        steps = ROADMAPS.get(career, [])
        total_wks = sum(int(s[1].replace(" wks","").replace(" wk","")) for s in steps if s[1] and "wk" in s[1])
        completed_steps = max(1, round((avg_skill / 10) * (len(steps)-1)))  # estimate progress

        # ── Header ──
        st.markdown(
            f'<div style="display:flex;align-items:center;justify-content:space-between;'
            f'flex-wrap:wrap;gap:12px;margin-bottom:1.4rem;">'
            f'<div>'
            f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:{c_color};font-weight:600;margin-bottom:4px;">Your Career Roadmap</div>'
            f'<h2 style="font-family:Syne,sans-serif;font-weight:800;font-size:1.6rem;color:#e2e8f8;margin:0;">{c_icon} {career}</h2>'
            f'</div>'
            f'<div style="display:flex;gap:12px;">'
            f'<div style="background:rgba({r},{g},{b},0.12);border:1px solid rgba({r},{g},{b},0.3);'
            f'border-radius:12px;padding:8px 16px;text-align:center;">'
            f'<div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:{c_color};">~{total_wks}</div>'
            f'<div style="font-size:10px;color:#475569;text-transform:uppercase;">Total Weeks</div>'
            f'</div>'
            f'<div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);'
            f'border-radius:12px;padding:8px 16px;text-align:center;">'
            f'<div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#34d399;">{len(steps)-1}</div>'
            f'<div style="font-size:10px;color:#475569;text-transform:uppercase;">Milestones</div>'
            f'</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

        # ── Overall progress bar ──
        progress_pct = int((avg_skill / 10) * 100)
        st.markdown(
            f'<div style="background:rgba(15,23,42,0.65);border:1px solid rgba({r},{g},{b},0.15);'
            f'border-radius:14px;padding:1rem 1.4rem;margin-bottom:1.4rem;">'
            f'<div style="display:flex;justify-content:space-between;margin-bottom:8px;">'
            f'<span style="font-size:13px;color:#94a3b8;font-weight:500;">Estimated Readiness</span>'
            f'<span style="font-family:Syne,sans-serif;font-weight:700;color:{c_color};">{progress_pct}%</span>'
            f'</div>'
            f'<div style="background:rgba(96,165,250,0.08);border-radius:100px;height:10px;">'
            f'<div style="background:linear-gradient(90deg,{c_color},rgba({r},{g},{b},0.55));'
            f'border-radius:100px;height:10px;width:{progress_pct}%;transition:width 1s;"></div>'
            f'</div>'
            f'<div style="display:flex;justify-content:space-between;margin-top:6px;">'
            f'<span style="font-size:11px;color:#475569;">Beginner</span>'
            f'<span style="font-size:11px;color:#475569;">Intermediate</span>'
            f'<span style="font-size:11px;color:#475569;">Advanced</span>'
            f'</div></div>',
            unsafe_allow_html=True
        )

        # ── Manual completion tracking ──
        if career not in st.session_state.completed_steps:
            st.session_state.completed_steps[career] = set()
        done_set = st.session_state.completed_steps[career]

        # ── Visual timeline (vertical cards with connector) ──
        for i, (sname, dur, sicon) in enumerate(steps):
            is_last    = (i == len(steps)-1)
            is_done    = (i in done_set) and not is_last
            # current = first step not yet marked done (excluding goal)
            non_last_done = [x for x in done_set if x != len(steps)-1]
            first_undone  = next((j for j in range(len(steps)-1) if j not in done_set), len(steps)-1)
            is_current = (i == first_undone) and not is_last

            if is_done:
                card_bg     = f"linear-gradient(135deg,rgba({r},{g},{b},0.22),rgba({r},{g},{b},0.10))"
                card_border = f"rgba({r},{g},{b},0.55)"
                num_bg      = c_color
                num_color   = "#fff"
                status_tag  = f'<span style="background:rgba({r},{g},{b},0.18);border:1px solid rgba({r},{g},{b},0.4);border-radius:20px;padding:2px 10px;font-size:10px;color:{c_color};font-weight:600;">✓ Completed</span>'
                name_color  = "#e2e8f8"
                dur_color   = c_color
            elif is_current:
                card_bg     = f"linear-gradient(135deg,rgba({r},{g},{b},0.28),rgba({r},{g},{b},0.14))"
                card_border = c_color
                num_bg      = c_color
                num_color   = "#fff"
                status_tag  = f'<span style="background:{c_color};border-radius:20px;padding:2px 10px;font-size:10px;color:#fff;font-weight:700;animation:pulse 2s infinite;">▶ Current</span>'
                name_color  = "#e2e8f8"
                dur_color   = c_color
            elif is_last:
                card_bg     = "linear-gradient(135deg,#064e3b,#065f46)"
                card_border = "#10b981"
                num_bg      = "#10b981"
                num_color   = "#fff"
                status_tag  = '<span style="background:#10b981;border-radius:20px;padding:2px 10px;font-size:10px;color:#fff;font-weight:700;">🎯 Goal</span>'
                name_color  = "#e2e8f8"
                dur_color   = "#34d399"
            else:
                card_bg     = "rgba(15,23,42,0.5)"
                card_border = "rgba(96,165,250,0.1)"
                num_bg      = "rgba(96,165,250,0.12)"
                num_color   = "#475569"
                status_tag  = '<span style="background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.15);border-radius:20px;padding:2px 10px;font-size:10px;color:#475569;font-weight:500;">Upcoming</span>'
                name_color  = "#64748b"
                dur_color   = "#475569"


            # Pre-compute to avoid nested f-strings (Python 3.10 compatibility)
            step_label = "✅" if is_last else ("▶" if is_current else ("✓" if is_done else str(i+1)))
            if is_last:
                connector_line = ""
            else:
                connector_line = (
                    f'<div style="width:2px;flex:1;min-height:20px;'
                    f'background:linear-gradient(180deg,{card_border},rgba(96,165,250,0.08));'
                    f'margin-top:2px;"></div>'
                )
            left_col, right_col = st.columns([0.06, 1])
            with left_col:
                st.markdown(
                    f'<div style="display:flex;flex-direction:column;align-items:center;height:100%;">'
                    f'<div style="width:36px;height:36px;border-radius:50%;background:{num_bg};'
                    f'display:flex;align-items:center;justify-content:center;'
                    f'font-family:Syne,sans-serif;font-weight:700;font-size:14px;color:{num_color};'
                    f'border:2px solid {card_border};flex-shrink:0;z-index:1;">'
                    f'{step_label}'
                    f'</div>'
                    f'{connector_line}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with right_col:
                card_col, btn_col = st.columns([1, 0.16])
                with card_col:
                    st.markdown(
                        f'<div style="background:{card_bg};border:1px solid {card_border};'
                        f'border-radius:14px;padding:0.85rem 1.2rem;margin-bottom:6px;'
                        f'display:flex;align-items:center;gap:14px;flex-wrap:wrap;">'
                        f'<div style="font-size:26px;">{sicon}</div>'
                        f'<div style="flex:1;min-width:140px;">'
                        f'<div style="font-family:Syne,sans-serif;font-weight:700;font-size:15px;color:{name_color};">{sname}</div>'
                        f'<div style="font-size:12px;color:{dur_color};margin-top:2px;">{dur if dur else "Final milestone"}</div>'
                        f'</div>'
                        f'{status_tag}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with btn_col:
                    if not is_last:
                        if is_done:
                            if st.button("↩ Undo", key=f"undo_{career}_{i}", use_container_width=True):
                                st.session_state.completed_steps[career].discard(i)
                                st.rerun()
                        else:
                            if st.button("✓ Done", key=f"done_{career}_{i}", use_container_width=True):
                                st.session_state.completed_steps[career].add(i)
                                st.rerun()

        st.markdown('<style>@keyframes pulse{0%,100%{opacity:1}50%{opacity:.7}}</style>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — SKILL COMPARISON
    # ══════════════════════════════════════════════════════════════════════════
    with t2:
        st.markdown(
            f'<h3 style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;margin-bottom:.6rem;">'
            f'📊 Your Skills vs Ideal {career} Profile</h3>',
            unsafe_allow_html=True
        )
        ideal      = IDEAL_PROFILES.get(career,[5,5,5,5])
        user_radar = [py, ml, web, ai]
        skill_labs = ["Python","Machine Learning","Web Dev","AI"]

        col_r, col_g2 = st.columns([1.3,1])
        with col_r:
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=ideal+[ideal[0]], theta=skill_labs+[skill_labs[0]],
                fill='toself', name='Ideal Profile',
                line_color='#10b981', fillcolor='rgba(16,185,129,0.15)', line_width=2,
            ))
            fig.add_trace(go.Scatterpolar(
                r=user_radar+[user_radar[0]], theta=skill_labs+[skill_labs[0]],
                fill='toself', name='Your Profile',
                line_color=c_color, fillcolor=f'rgba({r},{g},{b},0.2)', line_width=2,
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0,10], tickfont=dict(color='#64748b'), gridcolor='rgba(96,165,250,0.1)'),
                    angularaxis=dict(tickfont=dict(color='#94a3b8'), gridcolor='rgba(96,165,250,0.08)'),
                    bgcolor='rgba(0,0,0,0)',
                ),
                legend=dict(font=dict(color='#94a3b8'), bgcolor='rgba(0,0,0,0)'),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=20,b=20,l=30,r=30), height=350,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_g2:
            st.markdown("<br>", unsafe_allow_html=True)
            for i, sk in enumerate(skill_labs):
                gap = max(0, ideal[i]-user_radar[i])
                pct = int(user_radar[i]/10*100)
                ok  = gap == 0
                bc  = "#10b981" if ok else c_color
                note= "On track" if ok else f"Need +{gap} pts"
                st.markdown(
                    f'<div style="margin-bottom:16px;">'
                    f'<div style="display:flex;justify-content:space-between;margin-bottom:5px;">'
                    f'<span style="font-size:13px;color:#94a3b8;">{"✅" if ok else "⚠️"} {sk}</span>'
                    f'<span style="font-size:12px;color:{bc};font-weight:600;">{user_radar[i]}/10 · {note}</span>'
                    f'</div>'
                    f'<div style="background:rgba(96,165,250,0.08);border-radius:100px;height:7px;">'
                    f'<div style="background:{bc};border-radius:100px;height:7px;width:{pct}%;"></div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — SMART PROGRESSIVE COURSES
    # ══════════════════════════════════════════════════════════════════════════
    with t3:
        DOMAIN_COURSE_MAP = {
            "Data Science & Analytics": [("Python","Python",py),("Machine Learning","Machine Learning",ml),("AI Fundamentals","AI",ai)],
            "Machine Learning & AI":    [("Python","Python",py),("Machine Learning","Machine Learning",ml),("AI & Deep Learning","AI",ai)],
            "Web Development":          [("Python / Backend","Python",py),("Web Dev","Web Dev",web)],
            "AI Research":              [("Machine Learning","Machine Learning",ml),("AI & Deep Learning","AI",ai),("Python","Python",py)],
            "Full-Stack AI Dev":        [("Python","Python",py),("Web Dev","Web Dev",web),("Machine Learning","Machine Learning",ml),("AI & LLMs","AI",ai)],
        }
        domain_courses = DOMAIN_COURSE_MAP.get(dname, [("Python","Python",py),("Machine Learning","Machine Learning",ml)])

        # ── Header ──
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:.5rem;">'
            f'<h3 style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;margin:0;">'
            f'📚 Your Learning Path — {d["icon"]} {dname}</h3>'
            f'<span style="background:rgba({r},{g},{b},0.12);border:1px solid rgba({r},{g},{b},0.3);'
            f'border-radius:20px;padding:3px 12px;font-size:11px;color:{c_color};font-weight:600;">{career}</span>'
            f'<span style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);'
            f'border-radius:20px;padding:3px 12px;font-size:11px;color:#34d399;font-weight:600;">{overall_level}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<p style="color:#475569;font-size:13px;margin-bottom:1.4rem;">'
            f'Courses are ordered by level. Based on your quiz score, we start you at <strong style="color:#e2e8f8">{overall_level}</strong> level. '
            f'Beginner courses are {"shown as optional review" if overall_level != "Beginner" else "your starting point"}.</p>',
            unsafe_allow_html=True
        )

        LEVEL_ORDER = ["Beginner","Intermediate","Advanced"]
        LEVEL_COLORS = {"Beginner":"#f59e0b","Intermediate":"#60a5fa","Advanced":"#10b981"}
        LEVEL_ICONS  = {"Beginner":"🌱","Intermediate":"🚀","Advanced":"⚡"}

        for lbl, key, val in domain_courses:
            student_level = "Beginner" if val<=4 else "Intermediate" if val<=7 else "Advanced"
            student_idx   = LEVEL_ORDER.index(student_level)

            st.markdown(
                f'<div style="font-family:Syne,sans-serif;font-weight:700;font-size:15px;'
                f'color:#e2e8f8;margin:1.4rem 0 0.6rem;padding-bottom:6px;'
                f'border-bottom:1px solid rgba(96,165,250,0.1);">{lbl}</div>',
                unsafe_allow_html=True
            )

            for level_idx, level in enumerate(LEVEL_ORDER):
                lc       = LEVEL_COLORS[level]
                lic      = LEVEL_ICONS[level]
                lr,lg,lb = int(lc[1:3],16),int(lc[3:5],16),int(lc[5:7],16)
                items    = COURSES.get(key, {}).get(level, [])
                if not items:
                    continue  # skip levels with no courses

                is_current_level = (level_idx == student_idx)
                is_lower         = (level_idx < student_idx)

                if is_current_level:
                    exp_label = f"{lic} {level}  ·  Your Level ✓"
                    expanded  = True
                    badge_html = (
                        f'<div style="display:inline-block;background:{lc};'
                        f'border-radius:20px;padding:3px 12px;font-size:11px;'
                        f'color:#fff;font-weight:700;margin-bottom:10px;">🎯 Start here — matches your current skill level</div>'
                    )
                elif is_lower:
                    exp_label = f"{lic} {level}  ·  Optional Review"
                    expanded  = False
                    badge_html = (
                        f'<div style="display:inline-block;background:rgba({lr},{lg},{lb},0.15);'
                        f'border:1px solid {lc}55;border-radius:20px;padding:3px 12px;font-size:11px;'
                        f'color:{lc};font-weight:600;margin-bottom:10px;">💡 You are above this level — review to fill gaps</div>'
                    )
                else:
                    badge_txt = "⬆️ Next Step" if level_idx == student_idx+1 else "🏆 Advanced Goal"
                    exp_label = f"{lic} {level}  ·  {badge_txt}"
                    expanded  = (level_idx == student_idx+1)
                    badge_html = (
                        f'<div style="display:inline-block;background:rgba(167,139,250,0.15);'
                        f'border:1px solid rgba(167,139,250,0.3);border-radius:20px;padding:3px 12px;font-size:11px;'
                        f'color:#a78bfa;font-weight:600;margin-bottom:10px;">{badge_txt} — complete your current level first</div>'
                    )

                with st.expander(exp_label, expanded=expanded):
                    st.markdown(badge_html, unsafe_allow_html=True)

                    for title, url in items:
                        st.markdown(
                            f'<a href="{url}" target="_blank" style="display:flex;align-items:center;gap:10px;'
                            f'background:rgba(15,23,42,0.55);border:1px solid rgba(96,165,250,0.12);'
                            f'border-radius:10px;padding:10px 14px;margin:6px 0;color:#60a5fa;'
                            f'text-decoration:none;font-size:13px;">'
                            f'<span style="font-size:16px;">🔗</span>'
                            f'<span>{title}</span></a>',
                            unsafe_allow_html=True
                        )

        # Nudge
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="background:rgba(15,23,42,0.55);border:1px solid rgba(96,165,250,0.12);'
            'border-radius:14px;padding:1rem 1.4rem;">'
            '<div style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;font-size:14px;margin-bottom:4px;">'
            '💡 Want courses for another field?</div>'
            '<div style="font-size:12px;color:#475569;">Visit My Profile tab and take a quiz in a different domain to unlock its courses.</div>'
            '</div>',
            unsafe_allow_html=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — PROGRESS
    # ══════════════════════════════════════════════════════════════════════════
    with t4:
        st.markdown(
            '<h3 style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;margin-bottom:1rem;">'
            '📈 Your Progress Over Time</h3>',
            unsafe_allow_html=True
        )
        hist = get_sessions(username)
        if len(hist) == 0:
            st.info("No sessions yet. Take more quizzes to track your growth!")
        else:
            m1,m2,m3,m4 = st.columns(4)
            for col, lbl, key, clr in zip(
                [m1,m2,m3,m4],
                ["Python","ML","Web Dev","AI"],
                ["python_skill","ml_skill","web_interest","ai_interest"],
                ["#60a5fa","#a78bfa","#34d399","#f59e0b"]
            ):
                with col:
                    latest = int(hist[key].iloc[-1]) if key in hist.columns else 0
                    st.markdown(metric_pill(lbl, f"{latest}/10", "📊", clr), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            clr_map = {"python_skill":"#60a5fa","ml_skill":"#a78bfa","web_interest":"#34d399","ai_interest":"#f59e0b"}
            lbl_map = {"python_skill":"Python","ml_skill":"ML","web_interest":"Web Dev","ai_interest":"AI"}
            fig_p = go.Figure()
            for col_k, clr in clr_map.items():
                if col_k not in hist.columns: continue
                cr,cg,cb = int(clr[1:3],16),int(clr[3:5],16),int(clr[5:7],16)
                fig_p.add_trace(go.Scatter(
                    x=hist["timestamp"], y=hist[col_k],
                    mode="lines+markers", name=lbl_map[col_k],
                    line=dict(color=clr, width=2.5),
                    marker=dict(size=8, color=clr, line=dict(color='#04070f',width=2)),
                    fill='tozeroy', fillcolor=f'rgba({cr},{cg},{cb},0.07)',
                ))
            fig_p.update_layout(
                xaxis=dict(title="Session", tickfont=dict(color='#64748b'), gridcolor='rgba(96,165,250,0.06)', showgrid=True),
                yaxis=dict(title="Skill Level", range=[0,10], tickfont=dict(color='#64748b'), gridcolor='rgba(96,165,250,0.06)'                ),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(font=dict(color='#94a3b8'), bgcolor='rgba(0,0,0,0)', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                height=360, margin=dict(t=40,b=30,l=10,r=10),
            )
            st.plotly_chart(fig_p, use_container_width=True)
            log = hist[["timestamp","domain","gpa","predicted_career"]].copy()
            log.columns = ["Session","Domain","GPA","Predicted Career"]
            st.dataframe(log, use_container_width=True)
            if st.button("🗑️ Clear My History", type="secondary"):
                conn = sqlite3.connect(DB_PATH)
                conn.execute("DELETE FROM sessions WHERE username=?", (username,))
                conn.commit(); conn.close()
                st.success("History cleared."); st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 5 — MY PROFILE
    # ══════════════════════════════════════════════════════════════════════════
    with t5:
        st.markdown(
            f'<h3 style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;margin-bottom:1.2rem;">'
            f'👤 My Profile — {full_name}</h3>',
            unsafe_allow_html=True
        )
        hist_p = get_sessions(username)
        total_sessions = len(hist_p)
        domains_tried_p = hist_p["domain"].nunique() if "domain" in hist_p.columns and total_sessions > 0 else 0
        last_career_p   = hist_p["predicted_career"].iloc[-1] if total_sessions > 0 else "None yet"

        st.markdown(
            f'<div style="background:linear-gradient(135deg,rgba(29,78,216,0.14),rgba(124,58,237,0.14));'
            f'border:1px solid rgba(96,165,250,0.18);border-radius:18px;padding:1.4rem 1.8rem;margin-bottom:1.4rem;">'
            f'<div style="display:flex;align-items:center;gap:16px;margin-bottom:1rem;">'
            f'<div style="width:56px;height:56px;border-radius:50%;'
            f'background:linear-gradient(135deg,#1d4ed8,#7c3aed);'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-family:Syne,sans-serif;font-size:22px;font-weight:800;color:#fff;">{full_name[0].upper()}</div>'
            f'<div>'
            f'<div style="font-family:Syne,sans-serif;font-weight:800;font-size:20px;color:#e2e8f8;">{full_name}</div>'
            f'<div style="font-size:13px;color:#475569;">@{username}</div>'
            f'</div></div>'
            f'<div style="display:flex;gap:16px;flex-wrap:wrap;">'
            f'<div style="text-align:center;background:rgba(96,165,250,0.08);border-radius:10px;padding:8px 18px;">'
            f'<div style="font-family:Syne,sans-serif;font-size:20px;font-weight:700;color:#60a5fa;">{total_sessions}</div>'
            f'<div style="font-size:11px;color:#475569;text-transform:uppercase;">Sessions</div>'
            f'</div>'
            f'<div style="text-align:center;background:rgba(167,139,250,0.08);border-radius:10px;padding:8px 18px;">'
            f'<div style="font-family:Syne,sans-serif;font-size:20px;font-weight:700;color:#a78bfa;">{domains_tried_p}</div>'
            f'<div style="font-size:11px;color:#475569;text-transform:uppercase;">Domains Tried</div>'
            f'</div>'
            f'<div style="text-align:center;background:rgba(52,211,153,0.08);border-radius:10px;padding:8px 18px;">'
            f'<div style="font-family:Syne,sans-serif;font-size:15px;font-weight:700;color:#34d399;">{CAREER_ICONS.get(last_career_p,"🎯")} {last_career_p}</div>'
            f'<div style="font-size:11px;color:#475569;text-transform:uppercase;">Current Path</div>'
            f'</div>'
            f'<div style="text-align:center;background:rgba(16,185,129,0.08);border-radius:10px;padding:8px 18px;">'
            f'<div style="font-family:Syne,sans-serif;font-size:16px;font-weight:700;color:#10b981;">{overall_level}</div>'
            f'<div style="font-size:11px;color:#475569;text-transform:uppercase;">Skill Level</div>'
            f'</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;'
            'font-size:16px;margin-bottom:8px;">💡 Explore Another Domain</div>'
            '<p style="color:#475569;font-size:13px;margin-bottom:1.2rem;">'
            'Each quiz unlocks domain-specific courses and a tailored roadmap. '
            'Try a new domain to compare career paths.</p>',
            unsafe_allow_html=True
        )
        other_domains = [k for k in DOMAINS if k != dname]
        d_cols = st.columns(len(other_domains))
        for col, oname in zip(d_cols, other_domains):
            od = DOMAINS[oname]
            odr, odg, odb = od["rgb"]
            with col:
                st.markdown(
                    f'<div style="background:rgba(15,23,42,0.65);border:1px solid rgba({odr},{odg},{odb},0.25);'
                    f'border-radius:13px;padding:12px 10px;text-align:center;margin-bottom:4px;">'
                    f'<div style="font-size:24px;margin-bottom:6px;">{od["icon"]}</div>'
                    f'<div style="font-family:Syne,sans-serif;font-weight:700;font-size:12px;color:#e2e8f8;margin-bottom:4px;">{oname}</div>'
                    f'<div style="font-size:10px;color:{od["color"]};font-weight:600;">{od["career"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button("Take Quiz", key=f"profile_extra_{oname}", use_container_width=True):
                    st.session_state.selected_domain = oname
                    st.session_state.quiz_step       = 0
                    st.session_state.screen          = "quiz"
                    st.rerun()

        if total_sessions > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;font-size:15px;margin-bottom:10px;">📋 Quiz History</div>',
                unsafe_allow_html=True
            )
            log_df = hist_p[["timestamp","domain","predicted_career"]].copy()
            log_df.columns = ["Date & Time","Domain","Predicted Career"]
            st.dataframe(log_df, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 6 — LOGIN HISTORY
    # ══════════════════════════════════════════════════════════════════════════
    with t6:
        st.markdown(
            '<h3 style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;margin-bottom:1rem;">'
            '🔐 Your Login Activity</h3>',
            unsafe_allow_html=True
        )
        logs = get_login_logs(username)
        if len(logs) == 0:
            st.info("No login records found.")
        else:
            s_ok  = len(logs[logs["status"]=="success"])
            s_bad = len(logs[logs["status"]=="failed"])
            lc1, lc2, _ = st.columns([1,1,2])
            with lc1: st.markdown(metric_pill("Successful Logins", str(s_ok),  "✅","#10b981"), unsafe_allow_html=True)
            with lc2: st.markdown(metric_pill("Failed Attempts",   str(s_bad), "⚠️","#ef4444"), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            for _, row in logs.iterrows():
                ok_  = row["status"]=="success"
                dc   = "#10b981" if ok_ else "#ef4444"
                txt  = "✓ Successful login" if ok_ else "✗ Failed attempt"
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:14px;'
                    f'padding:10px 16px;background:rgba(15,23,42,0.5);'
                    f'border:1px solid rgba(96,165,250,0.09);border-radius:10px;margin-bottom:6px;">'
                    f'<div style="width:8px;height:8px;border-radius:50%;background:{dc};flex-shrink:0;"></div>'
                    f'<div style="flex:1;font-size:13px;color:#64748b;">{row["login_time"]}</div>'
                    f'<div style="font-size:13px;color:{dc};font-weight:600;">{txt}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

# ─────────────────────────────────────────────────────────────────────────────
# ROUTER — auto-restore last result if student already has sessions
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    show_auth()
else:
    # If student logged in fresh and has prior sessions, restore to results
    if (st.session_state.screen == "domain"
            and st.session_state.career_result is None
            and st.session_state.selected_domain is None):
        hist = get_sessions(st.session_state.username)
        if len(hist) > 0:
            last = hist.iloc[-1]
            st.session_state.selected_domain = last.get("domain", "Data Science & Analytics")
            if st.session_state.selected_domain not in DOMAINS:
                st.session_state.selected_domain = "Data Science & Analytics"
            # Restore computed scores from DB
            dname_r = st.session_state.selected_domain
            if dname_r not in st.session_state.domain_scores:
                st.session_state.domain_scores[dname_r] = {}
            st.session_state.domain_scores[dname_r]["_computed"] = {
                "gpa":  float(last.get("gpa", 7)),
                "py":   int(last.get("python_skill", 5)),
                "ml":   int(last.get("ml_skill", 5)),
                "web":  int(last.get("web_interest", 5)),
                "ai":   int(last.get("ai_interest", 5)),
            }
            st.session_state.career_result = last.get("predicted_career", "Data Scientist")
            st.session_state.screen = "results"

    if st.session_state.screen == "domain":
        show_domain_select()
    elif st.session_state.screen == "quiz":
        show_quiz()
    else:
        show_results()