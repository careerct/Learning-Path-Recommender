import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import datetime
import hashlib
import time
import random

st.set_page_config(
    page_title="Learning Path — AI Career Recommender",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
.stApp{background:#04070f;font-family:'DM Sans',sans-serif;color:#e2e8f8}
.stApp::before{content:'';position:fixed;inset:0;
  background-image:linear-gradient(rgba(96,165,250,0.03) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(96,165,250,0.03) 1px,transparent 1px);
  background-size:52px 52px;animation:gridScroll 30s linear infinite;pointer-events:none;z-index:0}
@keyframes gridScroll{to{background-position:52px 52px}}
.stApp::after{content:'';position:fixed;inset:0;
  background:radial-gradient(ellipse 55% 45% at 8% 12%,rgba(56,189,248,0.055) 0%,transparent 65%),
             radial-gradient(ellipse 45% 40% at 92% 78%,rgba(139,92,246,0.055) 0%,transparent 65%);
  pointer-events:none;z-index:0}
.main .block-container{position:relative;z-index:1;padding:0 2.4rem 4rem;max-width:1380px}
h1,h2,h3,h4{font-family:'Syne',sans-serif !important;letter-spacing:-0.02em}
#MainMenu,footer,header{visibility:hidden}
.stDeployButton{display:none}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:#0d1117}
::-webkit-scrollbar-thumb{background:#1e40af;border-radius:4px}
.stButton>button{
  background:linear-gradient(135deg,#1d4ed8 0%,#7c3aed 100%) !important;
  color:#fff !important;border:none !important;border-radius:11px !important;
  font-family:'Syne',sans-serif !important;font-weight:700 !important;font-size:14px !important;
  padding:0.62rem 1.5rem !important;transition:all 0.22s ease !important;
  box-shadow:0 4px 18px rgba(29,78,216,0.3) !important}
.stButton>button:hover{transform:translateY(-2px) !important;box-shadow:0 8px 28px rgba(29,78,216,0.5) !important}
.stTextInput>div>div>input,.stPasswordInput>div>div>input{
  background:rgba(15,23,42,0.85) !important;border:1px solid rgba(96,165,250,0.2) !important;
  border-radius:11px !important;color:#e2e8f8 !important;font-family:'DM Sans',sans-serif !important;
  padding:0.65rem 1rem !important;transition:border 0.2s !important}
.stTextInput>div>div>input:focus,.stPasswordInput>div>div>input:focus{
  border-color:rgba(96,165,250,0.5) !important;box-shadow:0 0 0 3px rgba(96,165,250,0.1) !important}
.stRadio>div{gap:10px !important}
.stRadio>div>label{
  background:rgba(15,23,42,0.7) !important;border:1px solid rgba(96,165,250,0.15) !important;
  border-radius:11px !important;padding:12px 18px !important;cursor:pointer !important;
  transition:all 0.18s !important;color:#94a3b8 !important;font-size:14px !important;
  width:100% !important;display:block !important}
.stRadio>div>label:hover{
  border-color:rgba(96,165,250,0.42) !important;color:#e2e8f8 !important;
  background:rgba(29,78,216,0.13) !important}
.stTabs [data-baseweb="tab-list"]{
  background:rgba(15,23,42,0.6) !important;border-radius:13px !important;
  padding:4px !important;border:1px solid rgba(96,165,250,0.12) !important;gap:3px !important}
.stTabs [data-baseweb="tab"]{
  background:transparent !important;color:#64748b !important;border-radius:10px !important;
  font-family:'Syne',sans-serif !important;font-weight:600 !important;
  padding:9px 18px !important;transition:all 0.2s !important}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#1d4ed8,#7c3aed) !important;color:#fff !important}
.stSuccess{border-radius:12px !important;border-left:3px solid #10b981 !important;background:rgba(16,185,129,0.08) !important}
.stError{border-radius:12px !important;border-left:3px solid #ef4444 !important}
.stInfo{border-radius:12px !important;border-left:3px solid #3b82f6 !important;background:rgba(59,130,246,0.08) !important}
hr{border-color:rgba(96,165,250,0.08) !important}
.stProgress>div>div>div{background:linear-gradient(90deg,#1d4ed8,#7c3aed) !important;border-radius:100px !important}
.stRadio label,.stSelectbox label,.stTextInput label{
  color:#64748b !important;font-size:11px !important;font-weight:500 !important;
  letter-spacing:.06em !important;text-transform:uppercase !important}
.streamlit-expanderHeader{
  background:rgba(15,23,42,0.6) !important;border:1px solid rgba(96,165,250,0.13) !important;
  border-radius:11px !important;color:#94a3b8 !important}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.7}}
@keyframes fadeSlideUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
.fade-in{animation:fadeSlideUp 0.5s ease forwards}
</style>
""", unsafe_allow_html=True)

# ── DATABASE ──────────────────────────────────────────────────────────────────
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
    existing = [row[1] for row in c.execute("PRAGMA table_info(sessions)").fetchall()]
    if "domain" not in existing:
        try: c.execute("ALTER TABLE sessions ADD COLUMN domain TEXT DEFAULT 'General'")
        except: pass
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
        return True, "Account created! Please sign in."
    except sqlite3.IntegrityError:
        return False, "Username already taken. Choose another."

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
        if row:
            conn.execute("INSERT INTO login_logs VALUES (NULL,?,?,?)", (username, now, "failed"))
            conn.commit()
        conn.close(); return False, None

def save_prediction(username, domain, gpa, py, ml, web, ai, career):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO sessions (username,timestamp,domain,gpa,python_skill,ml_skill,web_interest,ai_interest,predicted_career) VALUES (?,?,?,?,?,?,?,?,?)",
        (username, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
         str(domain), float(gpa), int(py), int(ml), int(web), int(ai), str(career)))
    conn.commit(); conn.close()

def get_sessions(username):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM sessions WHERE username=? ORDER BY timestamp", conn, params=(username,))
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

# ── DOMAIN DATA ───────────────────────────────────────────────────────────────
DOMAINS = {
    "Data Science & Analytics": {
        "icon":"📊","color":"#3b82f6","rgb":(59,130,246),
        "desc":"Work with data, statistics & machine learning to uncover insights",
        "career":"Data Scientist",
        "quiz":[
            {"q":"How comfortable are you with maths & statistics?",
             "opts":[("I avoid maths wherever possible","1"),("Basic arithmetic & percentages only","3"),
                     ("Comfortable with algebra & basic stats","5"),("Know probability, distributions & hypothesis testing","7"),
                     ("Love linear algebra, calculus & statistical inference","10")]},
            {"q":"Have you ever explored a dataset to find patterns?",
             "opts":[("Never heard of datasets","1"),("Opened a CSV file in Excel","3"),
                     ("Used pandas/R to explore data","5"),("Built dashboards or visualisations","7"),
                     ("Done end-to-end EDA with statistical insights","10")]},
            {"q":"How much Python or R programming do you know?",
             "opts":[("No coding experience","1"),("Know variables and basic loops","3"),
                     ("Write small scripts independently","5"),("Use data libraries (pandas, numpy, ggplot)","7"),
                     ("Write clean, reusable data pipelines","10")]},
            {"q":"Have you trained any machine learning models?",
             "opts":[("What is ML?","1"),("Watched tutorials but not tried","3"),
                     ("Trained a simple model (e.g. linear regression)","5"),("Tuned hyperparameters & evaluated models","7"),
                     ("Deploy models and monitor them in production","10")]},
            {"q":"What is your academic/GPA performance?",
             "opts":[("Below average","4"),("Average","5.5"),("Good","6.5"),("Very good","7.5"),("Excellent","9")]},
        ],
        "weights":[1.0,1.0,0.1,0.5],
        "course_sections":[("Python Programming","Python"),("Machine Learning","Machine Learning"),("AI & Data","AI")],
        "course_vals":["py","ml","ai"],
    },
    "Machine Learning & AI": {
        "icon":"🤖","color":"#8b5cf6","rgb":(139,92,246),
        "desc":"Build intelligent systems, neural networks & AI-powered products",
        "career":"ML Engineer",
        "quiz":[
            {"q":"How well do you understand linear algebra & calculus?",
             "opts":[("Not at all","1"),("Recall school basics","3"),("Comfortable with matrices & derivatives","5"),
                     ("Apply them in ML context (gradients, PCA)","7"),("Research-level understanding","10")]},
            {"q":"Have you built any deep learning models?",
             "opts":[("Never tried","1"),("Followed a YouTube tutorial","3"),("Built a CNN or RNN from scratch","5"),
                     ("Fine-tuned pre-trained models (BERT, ResNet)","7"),("Designed novel architectures","10")]},
            {"q":"How familiar are you with PyTorch or TensorFlow?",
             "opts":[("Never used them","1"),("Installed but confused","3"),("Train basic models with them","5"),
                     ("Custom training loops, optimisers","7"),("Contribute to or extend frameworks","10")]},
            {"q":"How do you approach reading AI research papers?",
             "opts":[("I don't read papers","1"),("Read abstracts sometimes","3"),("Read full papers with effort","5"),
                     ("Reproduce results from papers","7"),("Publish or peer-review papers","10")]},
            {"q":"What is your academic/GPA performance?",
             "opts":[("Below average","4"),("Average","5.5"),("Good","6.5"),("Very good","7.5"),("Excellent","9")]},
        ],
        "weights":[0.8,1.0,0.0,1.0],
        "course_sections":[("Python Programming","Python"),("Machine Learning","Machine Learning"),("AI & Deep Learning","AI")],
        "course_vals":["py","ml","ai"],
    },
    "Web Development": {
        "icon":"🌐","color":"#10b981","rgb":(16,185,129),
        "desc":"Create websites, apps & digital products people love to use",
        "career":"Web Developer",
        "quiz":[
            {"q":"How comfortable are you with HTML & CSS?",
             "opts":[("Never written a tag","1"),("Can make a simple page","3"),("Build responsive layouts","5"),
                     ("Use frameworks like Tailwind","7"),("Pixel-perfect, accessible UIs","10")]},
            {"q":"How much JavaScript do you know?",
             "opts":[("What is JS?","1"),("Basic DOM manipulation","3"),("Async/await, fetch, ES6+","5"),
                     ("React / Vue / frameworks","7"),("TypeScript, state management, performance","10")]},
            {"q":"Have you built a backend or API?",
             "opts":[("Never","1"),("Used drag-and-drop builders","3"),("Simple Flask/Express routes","5"),
                     ("REST API with auth & database","7"),("Microservices, GraphQL, scalable architecture","10")]},
            {"q":"How familiar are you with databases?",
             "opts":[("No idea","1"),("Used spreadsheets as data","3"),("Written basic SQL queries","5"),
                     ("Designed schemas, used ORMs","7"),("Optimised queries, handles migrations","10")]},
            {"q":"What is your academic/GPA performance?",
             "opts":[("Below average","4"),("Average","5.5"),("Good","6.5"),("Very good","7.5"),("Excellent","9")]},
        ],
        "weights":[0.3,0.0,1.0,0.0],
        "course_sections":[("Web Development","Web Dev"),("Python / Backend","Python")],
        "course_vals":["web","py"],
    },
    "AI Research": {
        "icon":"🔬","color":"#f59e0b","rgb":(245,158,11),
        "desc":"Push the boundaries of AI through experiments, papers & breakthroughs",
        "career":"AI Research Scientist",
        "quiz":[
            {"q":"How deeply do you understand backpropagation?",
             "opts":[("Never heard of it","1"),("Know it updates weights","3"),("Can derive it manually","5"),
                     ("Implement custom gradient flows","7"),("Research novel optimisation methods","10")]},
            {"q":"How many AI/ML papers have you read end-to-end?",
             "opts":[("Zero","1"),("1-2 casually","3"),("10+ with understanding","5"),
                     ("50+ and implemented some","7"),("Hundreds; I follow arxiv daily","10")]},
            {"q":"Have you reproduced or extended research results?",
             "opts":[("Never tried","1"),("Followed someone else's code","3"),("Reproduced a paper independently","5"),
                     ("Extended a paper with new experiments","7"),("Published original research","10")]},
            {"q":"How strong is your mathematics background?",
             "opts":[("School level only","1"),("Some university maths","3"),("Probability theory & linear algebra solid","5"),
                     ("Measure theory, convex optimisation","7"),("Research-grade mathematical maturity","10")]},
            {"q":"What is your academic/GPA performance?",
             "opts":[("Below average","4"),("Average","5.5"),("Good","6.5"),("Very good","7.5"),("Excellent","9")]},
        ],
        "weights":[0.7,1.0,0.0,1.0],
        "course_sections":[("AI & Deep Learning","AI"),("Machine Learning","Machine Learning"),("Python Programming","Python")],
        "course_vals":["ai","ml","py"],
    },
    # ✅ CHANGED: Full-Stack AI Dev → Full-Stack Development (pure web + backend, no AI courses)
    "Full-Stack Development": {
        "icon":"🚀","color":"#ef4444","rgb":(239,68,68),
        "desc":"Build complete web apps — frontend, backend, databases & cloud deployment",
        "career":"Full-Stack Developer",
        "quiz":[
            {"q":"How comfortable are you building frontend UIs?",
             "opts":[("Never built a UI","1"),("Basic HTML/CSS pages only","3"),
                     ("Build responsive UIs with React or Vue","5"),
                     ("Complex state management, animations, accessibility","7"),
                     ("Production-grade component libraries and design systems","10")]},
            {"q":"How experienced are you with backend development?",
             "opts":[("No backend experience","1"),("Simple scripts with print statements","3"),
                     ("REST APIs with Node.js or Django","5"),
                     ("Auth, caching, queues, microservices","7"),
                     ("Architected large-scale distributed backends","10")]},
            {"q":"How well do you handle databases?",
             "opts":[("What is a database?","1"),("Basic SELECT queries","3"),
                     ("Designed schemas, used ORMs, joins","5"),
                     ("Optimised queries, indexes, migrations","7"),
                     ("Horizontal scaling, replication, sharding","10")]},
            {"q":"How comfortable are you with cloud & DevOps?",
             "opts":[("Never deployed anything","1"),("Used Heroku or Netlify once","3"),
                     ("Deployed on AWS / GCP / Azure","5"),
                     ("CI/CD pipelines, containers, serverless","7"),
                     ("Kubernetes, IaC, monitoring, auto-scaling","10")]},
            {"q":"What is your academic/GPA performance?",
             "opts":[("Below average","4"),("Average","5.5"),("Good","6.5"),("Very good","7.5"),("Excellent","9")]},
        ],
        "weights":[0.3,0.0,1.0,0.0],
        "course_sections":[
            ("Web Development","Web Dev"),
            ("Python / Backend","Python"),
            ("Databases","Databases"),
            ("Cloud & DevOps","Cloud"),
        ],
        "course_vals":["web","py","web","web"],
    },
}

CAREER_ICONS  = {"Data Scientist":"📊","ML Engineer":"⚙️","Web Developer":"🌐",
                 "AI Research Scientist":"🔬","Full-Stack Developer":"🚀"}
CAREER_COLORS = {"Data Scientist":"#3b82f6","ML Engineer":"#8b5cf6","Web Developer":"#10b981",
                 "AI Research Scientist":"#f59e0b","Full-Stack Developer":"#ef4444"}
CAREER_RGB    = {"Data Scientist":(59,130,246),"ML Engineer":(139,92,246),
                 "Web Developer":(16,185,129),"AI Research Scientist":(245,158,11),
                 "Full-Stack Developer":(239,68,68)}

ROADMAPS = {
    "Data Scientist":[
        ("Python Basics","2 wks","🐍"),("Statistics & Probability","3 wks","📐"),
        ("Data Wrangling with pandas","2 wks","🗃️"),("Exploratory Data Analysis","2 wks","🔍"),
        ("ML Fundamentals","4 wks","🤖"),("Data Visualisation","2 wks","📈"),
        ("Portfolio Projects","4 wks","💼"),("Job Ready!","","🎯"),
    ],
    "ML Engineer":[
        ("Python & OOP","2 wks","🐍"),("Linear Algebra & Calculus","3 wks","📐"),
        ("Core ML Algorithms","4 wks","🧠"),("Deep Learning (PyTorch)","5 wks","🔥"),
        ("MLOps & Deployment","3 wks","☁️"),("Model Optimisation","2 wks","⚡"),
        ("End-to-End ML Pipeline","4 wks","🔄"),("Job Ready!","","🎯"),
    ],
    "Web Developer":[
        ("HTML & CSS","2 wks","🎨"),("JavaScript Fundamentals","3 wks","⚡"),
        ("React / Vue Framework","4 wks","⚛️"),("Backend (Node/Flask)","3 wks","🔧"),
        ("Databases (SQL & NoSQL)","2 wks","🗄️"),("REST APIs & Auth","2 wks","🔐"),
        ("Deploy Full-Stack App","3 wks","🚀"),("Job Ready!","","🎯"),
    ],
    "AI Research Scientist":[
        ("Advanced Python","1 wk","🐍"),("Advanced Mathematics","4 wks","📐"),
        ("ML Theory Deep Dive","5 wks","📚"),("Deep Learning Papers","5 wks","🔬"),
        ("Research Methodology","3 wks","🧪"),("Reproduce a Paper","6 wks","✏️"),
        ("PhD / MS Applications","Ongoing","🎓"),("Job Ready!","","🎯"),
    ],
    # ✅ NEW roadmap for Full-Stack Developer — no AI steps
    "Full-Stack Developer":[
        ("HTML, CSS & Responsive Design","2 wks","🎨"),
        ("JavaScript & TypeScript","3 wks","⚡"),
        ("React or Vue (Frontend)","4 wks","⚛️"),
        ("Backend with Node.js or Django","4 wks","🔧"),
        ("Databases — SQL & NoSQL","3 wks","🗄️"),
        ("REST APIs, Auth & Security","2 wks","🔐"),
        ("Cloud Deployment & CI/CD","3 wks","☁️"),
        ("Job Ready!","","🎯"),
    ],
}

IDEAL_PROFILES = {
    "Data Scientist":[7,8,3,6],"ML Engineer":[9,9,2,7],
    "Web Developer":[5,2,9,2],"AI Research Scientist":[8,9,2,10],
    "Full-Stack Developer":[6,1,10,1],
}

# ── COURSES ───────────────────────────────────────────────────────────────────
COURSES = {
    "Python":{
        "Beginner":[
            ("Python for Everybody – Coursera","https://www.coursera.org/specializations/python"),
            ("Automate the Boring Stuff (Free)","https://automatetheboringstuff.com"),
            ("Python Basics – Codecademy","https://www.codecademy.com/learn/learn-python-3"),
            ("100 Days of Code – Udemy","https://www.udemy.com/course/100-days-of-code/"),
        ],
        "Intermediate":[
            ("Intermediate Python – Udemy","https://www.udemy.com/course/python-beyond-the-basics/"),
            ("Real Python Tutorials","https://realpython.com"),
            ("Python OOP – Corey Schafer YouTube","https://www.youtube.com/playlist?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc"),
            ("Python Testing with pytest","https://testdriven.io/blog/pytest-for-beginners/"),
        ],
        "Advanced":[
            ("Python Design Patterns","https://refactoring.guru/design-patterns/python"),
            ("High Performance Python – O'Reilly","https://www.oreilly.com/library/view/high-performance-python/9781492055013/"),
            ("Fluent Python – Book","https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/"),
            ("Python Concurrency & Async IO","https://realpython.com/async-io-python/"),
        ],
    },
    "Machine Learning":{
        "Beginner":[
            ("ML Crash Course – Google (Free)","https://developers.google.com/machine-learning/crash-course"),
            ("Intro to ML – Kaggle (Free)","https://www.kaggle.com/learn/intro-to-machine-learning"),
            ("ML for Beginners – Microsoft","https://github.com/microsoft/ML-For-Beginners"),
            ("Supervised ML – Coursera","https://www.coursera.org/learn/machine-learning"),
        ],
        "Intermediate":[
            ("ML Specialization – Andrew Ng","https://www.coursera.org/specializations/machine-learning-introduction"),
            ("Hands-On ML with Sklearn & TF","https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/"),
            ("Feature Engineering – Kaggle","https://www.kaggle.com/learn/feature-engineering"),
            ("Applied ML – Coursera","https://www.coursera.org/learn/python-machine-learning"),
        ],
        "Advanced":[
            ("Deep Learning Specialization","https://www.coursera.org/specializations/deep-learning"),
            ("Fast.ai – Practical Deep Learning","https://course.fast.ai"),
            ("MLOps Specialization – Coursera","https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops"),
            ("Full Stack Deep Learning","https://fullstackdeeplearning.com"),
        ],
    },
    "Web Dev":{
        "Beginner":[
            ("The Odin Project (Free)","https://www.theodinproject.com"),
            ("freeCodeCamp (Free)","https://www.freecodecamp.org"),
            ("HTML & CSS – Codecademy","https://www.codecademy.com/learn/learn-html"),
            ("Web Dev Bootcamp – Udemy","https://www.udemy.com/course/the-web-developer-bootcamp/"),
        ],
        "Intermediate":[
            ("Full-Stack Open (Free)","https://fullstackopen.com"),
            ("React Official Docs","https://react.dev"),
            ("Node.js – The Complete Guide","https://www.udemy.com/course/nodejs-the-complete-guide/"),
            ("CS50 Web Programming","https://cs50.harvard.edu/web/"),
        ],
        "Advanced":[
            ("System Design for Web Apps","https://www.educative.io/courses/web-application-software-architecture-101"),
            ("Advanced React Patterns","https://www.patterns.dev"),
            ("Next.js Official Docs","https://nextjs.org/docs"),
            ("Web Security Academy (Free)","https://portswigger.net/web-security"),
        ],
    },
    "AI":{
        "Beginner":[
            ("AI for Everyone – Andrew Ng","https://www.coursera.org/learn/ai-for-everyone"),
            ("Elements of AI (Free)","https://www.elementsofai.com"),
            ("Intro to AI – Udacity","https://www.udacity.com/course/intro-to-artificial-intelligence--cs271"),
            ("ChatGPT Prompt Eng. – DeepLearning.AI","https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/"),
        ],
        "Intermediate":[
            ("HuggingFace NLP Course (Free)","https://huggingface.co/learn/nlp-course/chapter1/1"),
            ("LangChain – Build LLM Apps","https://www.youtube.com/watch?v=lG7Uxts9SXs"),
            ("Generative AI with LLMs – Coursera","https://www.coursera.org/learn/generative-ai-with-llms"),
            ("Practical AI – Fast.ai","https://course.fast.ai"),
        ],
        "Advanced":[
            ("Attention is All You Need (Paper)","https://arxiv.org/abs/1706.03762"),
            ("Stanford CS224N – NLP with DL","https://web.stanford.edu/class/cs224n/"),
            ("Stanford CS231N – CNNs","http://cs231n.stanford.edu/"),
            ("The Little Book of Deep Learning","https://fleuret.org/public/lbdl.pdf"),
        ],
    },
    # ✅ NEW: Databases courses for Full-Stack Development
    "Databases":{
        "Beginner":[
            ("SQL for Beginners – W3Schools (Free)","https://www.w3schools.com/sql/"),
            ("Intro to SQL – Khan Academy (Free)","https://www.khanacademy.org/computing/computer-programming/sql"),
            ("Database Design – Lucidchart Guide","https://www.lucidchart.com/pages/database-diagram/database-design"),
            ("MongoDB Basics – MongoDB University (Free)","https://learn.mongodb.com/learning-paths/introduction-to-mongodb"),
        ],
        "Intermediate":[
            ("SQL & PostgreSQL – Udemy","https://www.udemy.com/course/sql-and-postgresql/"),
            ("Databases & SQL for Data Science – Coursera","https://www.coursera.org/learn/sql-data-science"),
            ("SQLAlchemy ORM Docs","https://docs.sqlalchemy.org/en/14/orm/"),
            ("Prisma ORM (Node.js)","https://www.prisma.io/docs/getting-started"),
        ],
        "Advanced":[
            ("Database Internals – Book","https://www.oreilly.com/library/view/database-internals/9781492040330/"),
            ("Designing Data-Intensive Applications","https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/"),
            ("Redis Caching Deep Dive","https://redis.io/learn"),
            ("PostgreSQL Performance Tuning","https://www.postgresql.org/docs/current/performance-tips.html"),
        ],
    },
    # ✅ NEW: Cloud & DevOps courses for Full-Stack Development
    "Cloud":{
        "Beginner":[
            ("AWS Cloud Practitioner – Free Tier","https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/"),
            ("Google Cloud Fundamentals – Coursera","https://www.coursera.org/learn/gcp-fundamentals"),
            ("Netlify Deploy Guide","https://docs.netlify.com/get-started/"),
            ("Vercel Deployment Docs","https://vercel.com/docs"),
        ],
        "Intermediate":[
            ("Docker for Developers – Udemy","https://www.udemy.com/course/docker-mastery/"),
            ("GitHub Actions CI/CD","https://docs.github.com/en/actions"),
            ("AWS Solutions Architect – Coursera","https://www.coursera.org/specializations/aws-fundamentals"),
            ("Linux Command Line Basics","https://ubuntu.com/tutorials/command-line-for-beginners"),
        ],
        "Advanced":[
            ("Kubernetes Certified Administrator","https://www.cncf.io/certification/cka/"),
            ("Terraform Infrastructure as Code","https://developer.hashicorp.com/terraform/tutorials"),
            ("AWS DevOps Professional Cert","https://aws.amazon.com/certification/certified-devops-engineer-professional/"),
            ("System Design Interview Guide","https://github.com/donnemartin/system-design-primer"),
        ],
    },
}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "logged_in":False,"username":"","full_name":"",
    "screen":"domain","selected_domain":None,"quiz_step":0,
    "domain_scores":{},"career_result":None,"completed_steps":{},
    "show_confetti":False,
}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k]=v

# ── HELPERS ───────────────────────────────────────────────────────────────────
def metric_pill(label,value,icon,color):
    return (f'<div style="background:rgba(15,23,42,0.7);border:1px solid {color}33;'
            f'border-radius:14px;padding:1rem 1.2rem;text-align:center;">'
            f'<div style="font-size:24px;margin-bottom:3px;">{icon}</div>'
            f'<div style="font-family:Syne,sans-serif;font-size:19px;font-weight:700;color:{color};">{value}</div>'
            f'<div style="font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:.07em;margin-top:2px;">{label}</div>'
            f'</div>')

def top_nav(show_retake=False):
    fname=st.session_state.get("full_name",""); uname=st.session_state.get("username","")
    logged_in=st.session_state.get("logged_in",False)
    left,right=st.columns([1,0.6])
    with left:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;padding:0.9rem 0 0.7rem;">'
            '<span style="font-size:26px;">🧠</span>'
            '<span style="font-family:Syne,sans-serif;font-weight:800;font-size:20px;'
            'background:linear-gradient(135deg,#60a5fa,#a78bfa);'
            '-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Learning Path</span>'
            '<span style="background:rgba(96,165,250,0.12);border:1px solid rgba(96,165,250,0.22);'
            'border-radius:20px;padding:2px 11px;font-size:11px;color:#60a5fa;font-weight:600;">AI Career Advisor</span>'
            '</div>',unsafe_allow_html=True)
    with right:
        if logged_in:
            initial=fname[0].upper() if fname else "?"
            btn_cols=st.columns([1.6,1,1] if show_retake else [2,1])
            with btn_cols[0]:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:9px;'
                    f'background:rgba(15,23,42,0.7);border:1px solid rgba(96,165,250,0.18);'
                    f'border-radius:40px;padding:5px 14px 5px 6px;margin-top:10px;">'
                    f'<div style="width:30px;height:30px;border-radius:50%;'
                    f'background:linear-gradient(135deg,#1d4ed8,#7c3aed);'
                    f'display:flex;align-items:center;justify-content:center;'
                    f'font-family:Syne,sans-serif;font-size:13px;font-weight:700;color:#fff;">{initial}</div>'
                    f'<div><div style="font-family:Syne,sans-serif;font-weight:700;font-size:13px;color:#e2e8f8;line-height:1.1;">{fname}</div>'
                    f'<div style="font-size:10px;color:#475569;">@{uname}</div></div></div>',
                    unsafe_allow_html=True)
            if show_retake:
                with btn_cols[1]:
                    st.markdown("<div style='margin-top:8px;'>",unsafe_allow_html=True)
                    if st.button("🔄 Retake",use_container_width=True):
                        st.session_state.screen=st.session_state.selected_domain=None
                        st.session_state.screen="domain"; st.session_state.quiz_step=0
                        st.session_state.domain_scores={}; st.session_state.career_result=None
                        st.rerun()
                    st.markdown("</div>",unsafe_allow_html=True)
                with btn_cols[2]:
                    st.markdown("<div style='margin-top:8px;'>",unsafe_allow_html=True)
                    if st.button("Logout →",use_container_width=True):
                        for k,v in DEFAULTS.items(): st.session_state[k]=v
                        st.rerun()
                    st.markdown("</div>",unsafe_allow_html=True)
            else:
                with btn_cols[1]:
                    st.markdown("<div style='margin-top:8px;'>",unsafe_allow_html=True)
                    if st.button("Logout →",use_container_width=True):
                        for k,v in DEFAULTS.items(): st.session_state[k]=v
                        st.rerun()
                    st.markdown("</div>",unsafe_allow_html=True)
    st.markdown('<hr style="margin:0 0 0.8rem;">',unsafe_allow_html=True)

# ── AUTH SCREEN ───────────────────────────────────────────────────────────────
def show_auth():
    top_nav(show_retake=False)

    # ── Animated hero ──
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 1rem;animation:fadeSlideUp 0.6s ease;">
        <div style="font-size:56px;margin-bottom:12px;">🧠</div>
        <h1 style="font-family:Syne,sans-serif;font-size:clamp(2rem,5vw,3.2rem);font-weight:800;
            background:linear-gradient(135deg,#60a5fa 0%,#a78bfa 50%,#34d399 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
            margin:0 0 10px;line-height:1.1;">Learning Path</h1>
        <p style="color:#64748b;font-size:16px;margin:0;">
            Pick your domain &middot; Take a 5-question quiz &middot; Get your personalised career roadmap
        </p>
    </div>
    """,unsafe_allow_html=True)

    # ── Stats ──
    total=count_users()
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(metric_pill("Students Joined",str(total),"👩‍🎓","#60a5fa"),unsafe_allow_html=True)
    with c2: st.markdown(metric_pill("Career Paths","5","🎯","#a78bfa"),unsafe_allow_html=True)
    with c3: st.markdown(metric_pill("Domain Quizzes","5","⚡","#34d399"),unsafe_allow_html=True)
    with c4: st.markdown(metric_pill("Courses Mapped","60+","📚","#f59e0b"),unsafe_allow_html=True)

    # ── How it works ──
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(15,23,42,0.6);border:1px solid rgba(96,165,250,0.12);
                border-radius:16px;padding:1.4rem 1.8rem;margin-bottom:1.6rem;">
        <div style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;font-size:15px;margin-bottom:1rem;">
            How it works in 3 steps
        </div>
        <div style="display:flex;gap:16px;flex-wrap:wrap;">
            <div style="flex:1;min-width:160px;text-align:center;padding:12px;">
                <div style="font-size:32px;margin-bottom:8px;">🎯</div>
                <div style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;font-size:13px;">Choose Domain</div>
                <div style="font-size:12px;color:#475569;margin-top:4px;">Pick the field that excites you most</div>
            </div>
            <div style="font-size:20px;color:#334155;align-self:center;">→</div>
            <div style="flex:1;min-width:160px;text-align:center;padding:12px;">
                <div style="font-size:32px;margin-bottom:8px;">📝</div>
                <div style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;font-size:13px;">Take Quiz</div>
                <div style="font-size:12px;color:#475569;margin-top:4px;">5 tailored questions — no maths required</div>
            </div>
            <div style="font-size:20px;color:#334155;align-self:center;">→</div>
            <div style="flex:1;min-width:160px;text-align:center;padding:12px;">
                <div style="font-size:32px;margin-bottom:8px;">🗺️</div>
                <div style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;font-size:13px;">Get Your Roadmap</div>
                <div style="font-size:12px;color:#475569;margin-top:4px;">Personalised courses + step-by-step path</div>
            </div>
        </div>
    </div>
    """,unsafe_allow_html=True)

    # ── Auth forms ──
    _,col_form,_=st.columns([1,1.5,1])
    with col_form:
        tab_in,tab_reg=st.tabs(["🔑  Sign In","✨  Register"])
        with tab_in:
            with st.form("login_form",clear_on_submit=False):
                uname=st.text_input("Username",placeholder="your_username")
                pwd=st.text_input("Password",type="password",placeholder="••••••••")
                sub=st.form_submit_button("Sign In →",use_container_width=True)
            if sub:
                if not uname or not pwd: st.error("Please fill in both fields.")
                else:
                    ok,name=login_user(uname,pwd)
                    if ok:
                        st.session_state.logged_in=True; st.session_state.username=uname
                        st.session_state.full_name=name or uname; st.session_state.screen="domain"
                        st.success(f"Welcome back, {name or uname}! 🎉")
                        time.sleep(0.5); st.rerun()
                    else: st.error("Invalid username or password.")

        with tab_reg:
            reg_ok=st.session_state.get("_reg_ok",None); reg_msg=st.session_state.get("_reg_msg","")
            if reg_ok is True: st.success(reg_msg); st.session_state["_reg_ok"]=None
            elif reg_ok is False: st.error(reg_msg); st.session_state["_reg_ok"]=None
            with st.form("reg_form",clear_on_submit=False):
                rn=st.text_input("Full Name",placeholder="Alex Kumar")
                re=st.text_input("Email",placeholder="alex@example.com")
                ru=st.text_input("Username",placeholder="alex_kumar")
                rp=st.text_input("Password",type="password",placeholder="min 6 characters")
                rp2=st.text_input("Confirm Password",type="password",placeholder="repeat password")
                rbtn=st.form_submit_button("Create Account →",use_container_width=True)
                if rbtn:
                    if not all([rn,re,ru,rp,rp2]): st.error("Please fill in all fields.")
                    elif len(rp)<6: st.error("Password must be at least 6 characters.")
                    elif rp!=rp2: st.error("Passwords do not match.")
                    else:
                        ok,msg=register_user(ru,rp,rn,re)
                        st.session_state["_reg_ok"]=ok; st.session_state["_reg_msg"]=msg
                        st.rerun()

# ── DOMAIN SELECTION ──────────────────────────────────────────────────────────
def show_domain_select():
    top_nav(show_retake=False)
    fname=st.session_state.full_name; username=st.session_state.username
    sessions=get_sessions(username)
    last_c=sessions["predicted_career"].iloc[-1] if len(sessions)>0 else "None yet"
    is_new=(len(sessions)==0)

    # Welcome banner — special for first-timers
    if is_new:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,rgba(16,185,129,0.18),rgba(59,130,246,0.12));'
            f'border:1px solid rgba(16,185,129,0.35);border-radius:18px;'
            f'padding:1.4rem 1.8rem;margin-bottom:1.8rem;animation:fadeSlideUp 0.5s ease;">'
            f'<div style="font-size:12px;color:#34d399;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;">First time here? Welcome!</div>'
            f'<div style="font-family:Syne,sans-serif;font-size:22px;font-weight:800;color:#e2e8f8;">'
            f'Hi {fname}! 👋 Let\'s find your perfect career path.</div>'
            f'<div style="font-size:13px;color:#64748b;margin-top:6px;">'
            f'Choose a domain below and answer 5 quick questions. Takes less than 2 minutes.</div>'
            f'</div>',unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,rgba(29,78,216,0.14),rgba(124,58,237,0.14));'
            f'border:1px solid rgba(96,165,250,0.16);border-radius:18px;'
            f'padding:1.4rem 1.8rem;margin-bottom:1.8rem;'
            f'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">'
            f'<div>'
            f'<div style="font-size:12px;color:#475569;text-transform:uppercase;letter-spacing:.08em;">Welcome back</div>'
            f'<div style="font-family:Syne,sans-serif;font-size:24px;font-weight:800;color:#e2e8f8;">{fname} 👋</div>'
            f'<div style="font-size:13px;color:#475569;margin-top:2px;">@{username}</div>'
            f'</div>'
            f'<div style="text-align:right;">'
            f'<div style="font-size:12px;color:#475569;text-transform:uppercase;letter-spacing:.07em;">Last prediction</div>'
            f'<div style="font-size:16px;font-weight:600;color:#60a5fa;margin-top:2px;">{last_c}</div>'
            f'</div></div>',unsafe_allow_html=True)

    st.markdown(
        '<h2 style="font-family:Syne,sans-serif;font-weight:800;font-size:1.5rem;color:#e2e8f8;margin-bottom:6px;">'
        'Choose your area of interest</h2>'
        '<p style="color:#475569;font-size:14px;margin-bottom:1.4rem;">'
        "Each domain has 5 tailored questions. Your answers shape a personalised roadmap and course list.</p>",
        unsafe_allow_html=True)

    domain_names=list(DOMAINS.keys())
    for row in [domain_names[:3],domain_names[3:]]:
        cols=st.columns(len(row))
        for col,dname in zip(cols,row):
            d=DOMAINS[dname]; r,g,b=d["rgb"]
            with col:
                st.markdown(
                    f'<div style="background:rgba(15,23,42,0.65);'
                    f'border:1.5px solid rgba({r},{g},{b},0.3);border-radius:16px;'
                    f'padding:1.6rem 1.3rem;margin-bottom:4px;transition:all 0.2s;">'
                    f'<div style="font-size:36px;margin-bottom:10px;">{d["icon"]}</div>'
                    f'<div style="font-family:Syne,sans-serif;font-weight:700;font-size:15px;'
                    f'color:#e2e8f8;margin-bottom:6px;">{dname}</div>'
                    f'<div style="font-size:12px;color:#64748b;line-height:1.5;margin-bottom:10px;">{d["desc"]}</div>'
                    f'<div style="display:inline-block;'
                    f'background:rgba({r},{g},{b},0.15);border:1px solid rgba({r},{g},{b},0.35);'
                    f'border-radius:20px;padding:3px 12px;font-size:11px;color:{d["color"]};font-weight:600;">'
                    f'→ {d["career"]}</div>'
                    f'</div>',unsafe_allow_html=True)
                if st.button("Start Quiz →",key=f"pick_{dname}",use_container_width=True):
                    st.session_state.selected_domain=dname; st.session_state.quiz_step=0
                    st.session_state.screen="quiz"; st.rerun()
        st.markdown("<br>",unsafe_allow_html=True)

# ── QUIZ SCREEN ───────────────────────────────────────────────────────────────
def show_quiz():
    dname=st.session_state.selected_domain; d=DOMAINS[dname]
    step=st.session_state.quiz_step; quiz=d["quiz"]; total=len(quiz); r,g,b=d["rgb"]
    top_nav(show_retake=False)
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:8px;'
        f'background:rgba({r},{g},{b},0.12);border:1px solid rgba({r},{g},{b},0.3);'
        f'border-radius:20px;padding:4px 14px;font-size:13px;color:{d["color"]};'
        f'font-weight:600;margin-bottom:1.2rem;">'
        f'{d["icon"]} {dname} — {d["career"]} Path</div>',unsafe_allow_html=True)
    st.progress(step/total)
    st.markdown(f'<p style="color:#475569;font-size:12px;text-align:right;margin-top:-4px;margin-bottom:1.5rem;">'
                f'Question {step+1} of {total}</p>',unsafe_allow_html=True)
    q=quiz[step]
    _,qcol,_=st.columns([0.5,3,0.5])
    with qcol:
        st.markdown(
            f'<div style="background:rgba(15,23,42,0.65);border:1px solid rgba({r},{g},{b},0.2);'
            f'border-radius:18px;padding:2rem 2.2rem;margin-bottom:1.2rem;text-align:center;">'
            f'<div style="font-size:44px;margin-bottom:12px;">{d["icon"]}</div>'
            f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:{d["color"]};font-weight:600;margin-bottom:10px;">{dname}</div>'
            f'<h2 style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:700;color:#e2e8f8;line-height:1.4;">{q["q"]}</h2>'
            f'</div>',unsafe_allow_html=True)
        option_labels=[opt[0] for opt in q["opts"]]
        chosen=st.radio("",options=option_labels,key=f"q_{dname}_{step}",label_visibility="collapsed")
        st.markdown("<br>",unsafe_allow_html=True)
        b1,b2=st.columns([1,3])
        with b1:
            if step>0:
                if st.button("← Back",use_container_width=True):
                    st.session_state.quiz_step-=1; st.rerun()
        with b2:
            btn_lbl="Next Question →" if step<total-1 else f"🚀 See My {d['career']} Path!"
            if st.button(btn_lbl,use_container_width=True):
                val=float(next(v for (lbl,v) in q["opts"] if lbl==chosen))
                if dname not in st.session_state.domain_scores:
                    st.session_state.domain_scores[dname]={}
                st.session_state.domain_scores[dname][f"q{step}"]=val
                if step<total-1:
                    st.session_state.quiz_step+=1
                else:
                    raw=st.session_state.domain_scores[dname]
                    answers=[float(raw[f"q{i}"]) for i in range(total) if f"q{i}" in raw]
                    w=d["weights"]; gpa=float(answers[-1]) if answers else 7.0
                    skill_vals=answers[:-1] if len(answers)>1 else [5.0]
                    base=sum(skill_vals)/max(len(skill_vals),1)
                    py_s=min(10,max(1,round(base*max(w[0],0.1))))
                    ml_s=min(10,max(1,round(base*max(w[1],0.1))))
                    web_s=min(10,max(1,round(base*max(w[2],0.1))))
                    ai_s=min(10,max(1,round(base*max(w[3],0.1))))
                    career=d["career"]
                    st.session_state.domain_scores[dname]["_computed"]={"gpa":gpa,"py":py_s,"ml":ml_s,"web":web_s,"ai":ai_s}
                    save_prediction(st.session_state.username,dname,gpa,py_s,ml_s,web_s,ai_s,career)
                    st.session_state.career_result=career
                    st.session_state.screen="results"
                    st.session_state.show_confetti=True
                st.rerun()

# ── RESULTS SCREEN ────────────────────────────────────────────────────────────
def show_results():
    career=st.session_state.career_result; dname=st.session_state.selected_domain
    d=DOMAINS[dname]; username=st.session_state.username; full_name=st.session_state.full_name
    computed=st.session_state.domain_scores.get(dname,{}).get("_computed",{})
    gpa=computed.get("gpa",7.0); py=computed.get("py",5); ml=computed.get("ml",5)
    web=computed.get("web",5);   ai=computed.get("ai",5)
    c_color=d["color"]; c_icon=d["icon"]; r,g,b=d["rgb"]
    avg_skill=(py+ml+web+ai)/4
    overall_level="Beginner" if avg_skill<=4 else "Intermediate" if avg_skill<=7 else "Advanced"

    top_nav(show_retake=True)

    # ── Confetti burst on first result view ──
    if st.session_state.get("show_confetti",False):
        st.balloons()
        st.session_state.show_confetti=False

    # ── Result hero ──
    st.markdown(
        f'<div style="background:linear-gradient(135deg,rgba({r},{g},{b},0.15),rgba({r},{g},{b},0.06));'
        f'border:1.5px solid rgba({r},{g},{b},0.35);border-radius:20px;'
        f'padding:1.4rem 1.8rem;margin-bottom:1.2rem;animation:fadeSlideUp 0.5s ease;'
        f'display:flex;align-items:center;gap:20px;flex-wrap:wrap;">'
        f'<div style="font-size:52px;">{c_icon}</div>'
        f'<div style="flex:1;">'
        f'<div style="font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:{c_color};font-weight:600;margin-bottom:4px;">Your Recommended Career Path</div>'
        f'<div style="font-family:Syne,sans-serif;font-size:2rem;font-weight:800;color:#e2e8f8;">{career}</div>'
        f'<div style="font-size:13px;color:#475569;margin-top:3px;">Domain: {dname} &nbsp;·&nbsp; GPA {gpa:.1f}/10 &nbsp;·&nbsp; Level: {overall_level}</div>'
        f'</div>'
        f'<div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);'
        f'border-radius:20px;padding:6px 16px;font-size:13px;color:#34d399;font-weight:600;">{overall_level} Level</div>'
        f'</div>',unsafe_allow_html=True)

    # ── Skill pills ──
    sc=st.columns(5)
    for col,(lbl,val,ico,clr) in zip(sc,[
        ("GPA",f"{gpa:.1f}","🎓","#94a3b8"),("Python",py,"🐍","#60a5fa"),
        ("ML",ml,"🤖","#a78bfa"),("Web Dev",web,"🌐","#34d399"),("AI",ai,"🧠","#f59e0b"),
    ]): 
        with col: st.markdown(metric_pill(lbl,str(val),ico,clr),unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)

    t1,t2,t3,t4,t5,t6=st.tabs(["🗺️ Learning Roadmap","📊 Skill Comparison","📚 Courses","📈 Progress","👤 My Profile","🔐 Login History"])

    # ── TAB 1: ROADMAP ────────────────────────────────────────────────────────
    with t1:
        steps=ROADMAPS.get(career,[]); total_wks=sum(int(s[1].replace(" wks","").replace(" wk","")) for s in steps if s[1] and "wk" in s[1])
        st.markdown(
            f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:1.2rem;">'
            f'<div><div style="font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:{c_color};font-weight:600;margin-bottom:4px;">Your Career Roadmap</div>'
            f'<h2 style="font-family:Syne,sans-serif;font-weight:800;font-size:1.6rem;color:#e2e8f8;margin:0;">{c_icon} {career}</h2>'
            f'<div style="font-size:12px;color:#475569;margin-top:4px;">Domain: {dname}</div></div>'
            f'<div style="display:flex;gap:10px;">'
            f'<div style="background:rgba({r},{g},{b},0.12);border:1px solid rgba({r},{g},{b},0.3);border-radius:12px;padding:8px 16px;text-align:center;">'
            f'<div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:{c_color};">~{total_wks}</div>'
            f'<div style="font-size:10px;color:#475569;text-transform:uppercase;">Weeks</div></div>'
            f'<div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:12px;padding:8px 16px;text-align:center;">'
            f'<div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#34d399;">{len(steps)-1}</div>'
            f'<div style="font-size:10px;color:#475569;text-transform:uppercase;">Milestones</div></div>'
            f'</div></div>',unsafe_allow_html=True)

        progress_pct=min(99,int(avg_skill/10*100))
        st.markdown(
            f'<div style="background:rgba(15,23,42,0.65);border:1px solid rgba({r},{g},{b},0.15);border-radius:14px;padding:1rem 1.4rem;margin-bottom:1.2rem;">'
            f'<div style="display:flex;justify-content:space-between;margin-bottom:8px;">'
            f'<span style="font-size:13px;color:#94a3b8;font-weight:500;">Estimated Readiness</span>'
            f'<span style="font-family:Syne,sans-serif;font-weight:700;color:{c_color};">{progress_pct}%</span></div>'
            f'<div style="background:rgba(96,165,250,0.08);border-radius:100px;height:10px;">'
            f'<div style="background:linear-gradient(90deg,{c_color},rgba({r},{g},{b},0.5));border-radius:100px;height:10px;width:{progress_pct}%;"></div></div>'
            f'<div style="display:flex;justify-content:space-between;margin-top:5px;">'
            f'<span style="font-size:11px;color:#475569;">Beginner</span>'
            f'<span style="font-size:11px;color:#475569;">Intermediate</span>'
            f'<span style="font-size:11px;color:#475569;">Advanced</span></div></div>',unsafe_allow_html=True)

        if career not in st.session_state.completed_steps: st.session_state.completed_steps[career]=set()
        done_set=st.session_state.completed_steps[career]
        for i,(sname,dur,sicon) in enumerate(steps):
            is_last=(i==len(steps)-1); is_done=(i in done_set) and not is_last
            first_undone=next((j for j in range(len(steps)-1) if j not in done_set),len(steps)-1)
            is_current=(i==first_undone) and not is_last
            if is_done:
                card_bg=f"linear-gradient(135deg,rgba({r},{g},{b},0.22),rgba({r},{g},{b},0.10))"; card_border=f"rgba({r},{g},{b},0.55)"
                num_bg=c_color; num_color="#fff"; name_color="#e2e8f8"; dur_color=c_color
                status_tag=f'<span style="background:rgba({r},{g},{b},0.18);border:1px solid rgba({r},{g},{b},0.4);border-radius:20px;padding:2px 10px;font-size:10px;color:{c_color};font-weight:600;">✓ Completed</span>'
            elif is_current:
                card_bg=f"linear-gradient(135deg,rgba({r},{g},{b},0.28),rgba({r},{g},{b},0.14))"; card_border=c_color
                num_bg=c_color; num_color="#fff"; name_color="#e2e8f8"; dur_color=c_color
                status_tag=f'<span style="background:{c_color};border-radius:20px;padding:2px 10px;font-size:10px;color:#fff;font-weight:700;animation:pulse 2s infinite;">▶ Current</span>'
            elif is_last:
                card_bg="linear-gradient(135deg,#064e3b,#065f46)"; card_border="#10b981"
                num_bg="#10b981"; num_color="#fff"; name_color="#e2e8f8"; dur_color="#34d399"
                status_tag='<span style="background:#10b981;border-radius:20px;padding:2px 10px;font-size:10px;color:#fff;font-weight:700;">🎯 Goal</span>'
            else:
                card_bg="rgba(15,23,42,0.5)"; card_border="rgba(96,165,250,0.1)"
                num_bg="rgba(96,165,250,0.12)"; num_color="#475569"; name_color="#64748b"; dur_color="#475569"
                status_tag='<span style="background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.15);border-radius:20px;padding:2px 10px;font-size:10px;color:#475569;">Upcoming</span>'
            step_label="✅" if is_last else ("▶" if is_current else ("✓" if is_done else str(i+1)))
            connector="" if is_last else f'<div style="width:2px;flex:1;min-height:18px;background:linear-gradient(180deg,{card_border},rgba(96,165,250,0.06));margin-top:2px;"></div>'
            lc,rc=st.columns([0.06,1])
            with lc:
                st.markdown(f'<div style="display:flex;flex-direction:column;align-items:center;height:100%;">'
                            f'<div style="width:36px;height:36px;border-radius:50%;background:{num_bg};display:flex;align-items:center;justify-content:center;font-family:Syne,sans-serif;font-weight:700;font-size:13px;color:{num_color};border:2px solid {card_border};flex-shrink:0;">{step_label}</div>'
                            f'{connector}</div>',unsafe_allow_html=True)
            with rc:
                cc,bc=st.columns([1,0.16])
                with cc:
                    st.markdown(f'<div style="background:{card_bg};border:1px solid {card_border};border-radius:14px;padding:0.85rem 1.2rem;margin-bottom:4px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;">'
                                f'<div style="font-size:24px;">{sicon}</div>'
                                f'<div style="flex:1;"><div style="font-family:Syne,sans-serif;font-weight:700;font-size:14px;color:{name_color};">{sname}</div>'
                                f'<div style="font-size:11px;color:{dur_color};margin-top:2px;">{dur if dur else "Final milestone"}</div></div>'
                                f'{status_tag}</div>',unsafe_allow_html=True)
                with bc:
                    if not is_last:
                        if is_done:
                            if st.button("↩ Undo",key=f"undo_{career}_{i}",use_container_width=True): done_set.discard(i); st.rerun()
                        else:
                            if st.button("✓ Done",key=f"done_{career}_{i}",use_container_width=True): done_set.add(i); st.rerun()

    # ── TAB 2: SKILL COMPARISON ───────────────────────────────────────────────
    with t2:
        st.markdown(f'<h3 style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;margin-bottom:.6rem;">📊 Your Skills vs Ideal {career} Profile</h3>',unsafe_allow_html=True)
        ideal=IDEAL_PROFILES.get(career,[5,5,5,5]); user_radar=[py,ml,web,ai]; skill_labs=["Python","Machine Learning","Web Dev","AI"]
        col_r,col_g2=st.columns([1.3,1])
        with col_r:
            fig=go.Figure()
            fig.add_trace(go.Scatterpolar(r=ideal+[ideal[0]],theta=skill_labs+[skill_labs[0]],fill='toself',name='Ideal Profile',line_color='#10b981',fillcolor='rgba(16,185,129,0.15)',line_width=2))
            fig.add_trace(go.Scatterpolar(r=user_radar+[user_radar[0]],theta=skill_labs+[skill_labs[0]],fill='toself',name='Your Profile',line_color=c_color,fillcolor=f'rgba({r},{g},{b},0.2)',line_width=2))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,10],tickfont=dict(color='#64748b'),gridcolor='rgba(96,165,250,0.1)'),angularaxis=dict(tickfont=dict(color='#94a3b8'),gridcolor='rgba(96,165,250,0.08)'),bgcolor='rgba(0,0,0,0)'),legend=dict(font=dict(color='#94a3b8'),bgcolor='rgba(0,0,0,0)'),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',margin=dict(t=20,b=20,l=30,r=30),height=350)
            st.plotly_chart(fig,use_container_width=True)
        with col_g2:
            st.markdown("<br>",unsafe_allow_html=True)
            for i,sk in enumerate(skill_labs):
                gap=max(0,ideal[i]-user_radar[i]); pct=int(user_radar[i]/10*100); ok=gap==0; bc="#10b981" if ok else c_color
                st.markdown(f'<div style="margin-bottom:16px;"><div style="display:flex;justify-content:space-between;margin-bottom:5px;"><span style="font-size:13px;color:#94a3b8;">{"✅" if ok else "⚠️"} {sk}</span><span style="font-size:12px;color:{bc};font-weight:600;">{user_radar[i]}/10 · {"On track" if ok else f"Need +{gap} pts"}</span></div><div style="background:rgba(96,165,250,0.08);border-radius:100px;height:7px;"><div style="background:{bc};border-radius:100px;height:7px;width:{pct}%;"></div></div></div>',unsafe_allow_html=True)

    # ── TAB 3: COURSES ────────────────────────────────────────────────────────
    with t3:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:.5rem;">'
            f'<h3 style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;margin:0;">📚 Courses for {d["icon"]} {dname}</h3>'
            f'<span style="background:rgba({r},{g},{b},0.12);border:1px solid rgba({r},{g},{b},0.3);border-radius:20px;padding:3px 12px;font-size:11px;color:{c_color};font-weight:600;">{career}</span>'
            f'<span style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:20px;padding:3px 12px;font-size:11px;color:#34d399;font-weight:600;">{overall_level}</span>'
            f'</div>',unsafe_allow_html=True)
        st.markdown(f'<p style="color:#475569;font-size:13px;margin-bottom:1.4rem;">Courses below are for the <strong style="color:#e2e8f8">{dname}</strong> path only. Your level is <strong style="color:#e2e8f8">{overall_level}</strong> — that section is expanded. Other levels are available for reference.</p>',unsafe_allow_html=True)

        LEVEL_ORDER=["Beginner","Intermediate","Advanced"]
        LEVEL_COLORS={"Beginner":"#f59e0b","Intermediate":"#60a5fa","Advanced":"#10b981"}
        LEVEL_ICONS={"Beginner":"🌱","Intermediate":"🚀","Advanced":"⚡"}
        skill_val_map={"py":py,"ml":ml,"web":web,"ai":ai}
        sections=d["course_sections"]; val_keys=d["course_vals"]

        for idx,(section_label,course_key) in enumerate(sections):
            val_key=val_keys[idx] if idx<len(val_keys) else "py"
            skill_val=skill_val_map.get(val_key,5)
            student_level="Beginner" if skill_val<=4 else "Intermediate" if skill_val<=7 else "Advanced"
            student_idx=LEVEL_ORDER.index(student_level)
            st.markdown(f'<div style="font-family:Syne,sans-serif;font-weight:700;font-size:15px;color:#e2e8f8;margin:1.4rem 0 0.6rem;padding-bottom:6px;border-bottom:1px solid rgba(96,165,250,0.1);">{section_label} <span style="font-size:12px;color:#475569;font-weight:400;">(your level: {skill_val}/10)</span></div>',unsafe_allow_html=True)
            for level_idx,level in enumerate(LEVEL_ORDER):
                lc2=LEVEL_COLORS[level]; lic=LEVEL_ICONS[level]
                lr,lg,lb=int(lc2[1:3],16),int(lc2[3:5],16),int(lc2[5:7],16)
                items=COURSES.get(course_key,{}).get(level,[])
                if not items: continue
                is_current=(level_idx==student_idx); is_lower=(level_idx<student_idx)
                if is_current:
                    exp_label=f"{lic} {level}  ·  Your Level ✓"; expanded=True
                    badge_html=f'<div style="display:inline-block;background:{lc2};border-radius:20px;padding:3px 12px;font-size:11px;color:#fff;font-weight:700;margin-bottom:10px;">🎯 Start here — matches your current skill level</div>'
                elif is_lower:
                    exp_label=f"{lic} {level}  ·  Optional Review"; expanded=False
                    badge_html=f'<div style="display:inline-block;background:rgba({lr},{lg},{lb},0.15);border:1px solid {lc2}55;border-radius:20px;padding:3px 12px;font-size:11px;color:{lc2};font-weight:600;margin-bottom:10px;">💡 You are above this level — use to fill gaps</div>'
                else:
                    badge_txt="Next Step" if level_idx==student_idx+1 else "Advanced Goal"
                    exp_label=f"{lic} {level}  ·  {badge_txt}"; expanded=(level_idx==student_idx+1)
                    badge_html=f'<div style="display:inline-block;background:rgba(167,139,250,0.15);border:1px solid rgba(167,139,250,0.3);border-radius:20px;padding:3px 12px;font-size:11px;color:#a78bfa;font-weight:600;margin-bottom:10px;">{"⬆️ Complete current level first" if level_idx==student_idx+1 else "🏆 Long-term goal"}</div>'
                with st.expander(exp_label,expanded=expanded):
                    st.markdown(badge_html,unsafe_allow_html=True)
                    for title,url in items:
                        st.markdown(f'<a href="{url}" target="_blank" style="display:flex;align-items:center;gap:10px;background:rgba(15,23,42,0.55);border:1px solid rgba(96,165,250,0.12);border-radius:10px;padding:10px 14px;margin:6px 0;color:#60a5fa;text-decoration:none;font-size:13px;"><span style="font-size:16px;">🔗</span><span>{title}</span></a>',unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div style="background:rgba(15,23,42,0.55);border:1px solid rgba(96,165,250,0.12);border-radius:14px;padding:1rem 1.4rem;"><div style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;font-size:14px;margin-bottom:4px;">💡 Want courses for another field?</div><div style="font-size:12px;color:#475569;">Go to My Profile tab → Take a different domain quiz → Unlock its specific courses.</div></div>',unsafe_allow_html=True)

    # ── TAB 4: PROGRESS ───────────────────────────────────────────────────────
    with t4:
        st.markdown('<h3 style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;margin-bottom:1rem;">📈 Your Progress Over Time</h3>',unsafe_allow_html=True)
        hist=get_sessions(username)
        if len(hist)==0: st.info("No sessions yet. Complete quizzes to start tracking!")
        else:
            m1,m2,m3,m4=st.columns(4)
            for col,lbl,key,clr in zip([m1,m2,m3,m4],["Python","ML","Web Dev","AI"],["python_skill","ml_skill","web_interest","ai_interest"],["#60a5fa","#a78bfa","#34d399","#f59e0b"]):
                with col:
                    latest=int(hist[key].iloc[-1]) if key in hist.columns else 0
                    st.markdown(metric_pill(lbl,f"{latest}/10","📊",clr),unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
            fig_p=go.Figure()
            for col_k,clr,lbl_k in [("python_skill","#60a5fa","Python"),("ml_skill","#a78bfa","ML"),("web_interest","#34d399","Web Dev"),("ai_interest","#f59e0b","AI")]:
                if col_k not in hist.columns: continue
                cr,cg,cb=int(clr[1:3],16),int(clr[3:5],16),int(clr[5:7],16)
                fig_p.add_trace(go.Scatter(x=hist["timestamp"],y=hist[col_k],mode="lines+markers",name=lbl_k,line=dict(color=clr,width=2.5),marker=dict(size=8,color=clr,line=dict(color='#04070f',width=2)),fill='tozeroy',fillcolor=f'rgba({cr},{cg},{cb},0.07)'))
            fig_p.update_layout(xaxis=dict(title="Session",tickfont=dict(color='#64748b'),gridcolor='rgba(96,165,250,0.06)',showgrid=True),yaxis=dict(title="Skill Level",range=[0,10],tickfont=dict(color='#64748b'),gridcolor='rgba(96,165,250,0.06)'),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',legend=dict(font=dict(color='#94a3b8'),bgcolor='rgba(0,0,0,0)',orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1),height=360,margin=dict(t=40,b=30,l=10,r=10))
            st.plotly_chart(fig_p,use_container_width=True)
            log=hist[["timestamp","domain","gpa","predicted_career"]].copy(); log.columns=["Session","Domain","GPA","Career"]
            st.dataframe(log,use_container_width=True)
            if st.button("🗑️ Clear My History",type="secondary"):
                conn=sqlite3.connect(DB_PATH); conn.execute("DELETE FROM sessions WHERE username=?",(username,)); conn.commit(); conn.close()
                st.success("History cleared."); st.rerun()

    # ── TAB 5: MY PROFILE ─────────────────────────────────────────────────────
    with t5:
        hist_p=get_sessions(username); total_sessions=len(hist_p)
        domains_tried=hist_p["domain"].nunique() if "domain" in hist_p.columns and total_sessions>0 else 0
        last_career_p=hist_p["predicted_career"].iloc[-1] if total_sessions>0 else "None yet"
        st.markdown(f'<h3 style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;margin-bottom:1.2rem;">👤 My Profile</h3>',unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:linear-gradient(135deg,rgba(29,78,216,0.14),rgba(124,58,237,0.14));border:1px solid rgba(96,165,250,0.18);border-radius:18px;padding:1.4rem 1.8rem;margin-bottom:1.4rem;">'
            f'<div style="display:flex;align-items:center;gap:16px;margin-bottom:1rem;">'
            f'<div style="width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#1d4ed8,#7c3aed);display:flex;align-items:center;justify-content:center;font-family:Syne,sans-serif;font-size:22px;font-weight:800;color:#fff;">{full_name[0].upper()}</div>'
            f'<div><div style="font-family:Syne,sans-serif;font-weight:800;font-size:20px;color:#e2e8f8;">{full_name}</div><div style="font-size:13px;color:#475569;">@{username}</div></div></div>'
            f'<div style="display:flex;gap:14px;flex-wrap:wrap;">'
            +"".join([f'<div style="text-align:center;background:{bg};border-radius:10px;padding:8px 16px;"><div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:{clr};">{val}</div><div style="font-size:11px;color:#475569;text-transform:uppercase;">{lbl}</div></div>'
                      for lbl,val,clr,bg in [("Sessions",str(total_sessions),"#60a5fa","rgba(96,165,250,0.08)"),("Domains",str(domains_tried),"#a78bfa","rgba(167,139,250,0.08)"),("Current Path",f"{CAREER_ICONS.get(last_career_p,'🎯')} {last_career_p}","#34d399","rgba(52,211,153,0.08)"),("Level",overall_level,"#10b981","rgba(16,185,129,0.08)")]])
            +f'</div></div>',unsafe_allow_html=True)

        st.markdown('<div style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;font-size:16px;margin-bottom:6px;">💡 Explore Another Domain</div><p style="color:#475569;font-size:13px;margin-bottom:1.2rem;">Each quiz unlocks a domain-specific roadmap and courses. Take a new quiz to compare paths.</p>',unsafe_allow_html=True)
        other_domains=[k for k in DOMAINS if k!=dname]; d_cols=st.columns(len(other_domains))
        for col,oname in zip(d_cols,other_domains):
            od=DOMAINS[oname]; or_,og,ob=od["rgb"]
            with col:
                st.markdown(f'<div style="background:rgba(15,23,42,0.65);border:1px solid rgba({or_},{og},{ob},0.25);border-radius:13px;padding:12px 10px;text-align:center;margin-bottom:4px;"><div style="font-size:24px;margin-bottom:6px;">{od["icon"]}</div><div style="font-family:Syne,sans-serif;font-weight:700;font-size:12px;color:#e2e8f8;margin-bottom:4px;">{oname}</div><div style="font-size:10px;color:{od["color"]};font-weight:600;">{od["career"]}</div></div>',unsafe_allow_html=True)
                if st.button("Take Quiz",key=f"prof_{oname}",use_container_width=True):
                    st.session_state.selected_domain=oname; st.session_state.quiz_step=0
                    st.session_state.screen="quiz"; st.rerun()
        if total_sessions>0:
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;font-size:15px;margin-bottom:10px;">📋 Quiz History</div>',unsafe_allow_html=True)
            log_df=hist_p[["timestamp","domain","predicted_career"]].copy(); log_df.columns=["Date & Time","Domain","Career Prediction"]
            st.dataframe(log_df,use_container_width=True)

    # ── TAB 6: LOGIN HISTORY ──────────────────────────────────────────────────
    with t6:
        st.markdown('<h3 style="font-family:Syne,sans-serif;font-weight:700;color:#e2e8f8;margin-bottom:1rem;">🔐 Your Login Activity</h3>',unsafe_allow_html=True)
        logs=get_login_logs(username)
        if len(logs)==0: st.info("No login records found.")
        else:
            s_ok=len(logs[logs["status"]=="success"]); s_bad=len(logs[logs["status"]=="failed"])
            lc1,lc2,_=st.columns([1,1,2])
            with lc1: st.markdown(metric_pill("Successful Logins",str(s_ok),"✅","#10b981"),unsafe_allow_html=True)
            with lc2: st.markdown(metric_pill("Failed Attempts",str(s_bad),"⚠️","#ef4444"),unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
            for _,row in logs.iterrows():
                ok_=row["status"]=="success"; dc="#10b981" if ok_ else "#ef4444"; txt="Successful login" if ok_ else "Failed attempt"
                st.markdown(f'<div style="display:flex;align-items:center;gap:14px;padding:10px 16px;background:rgba(15,23,42,0.5);border:1px solid rgba(96,165,250,0.09);border-radius:10px;margin-bottom:6px;"><div style="width:8px;height:8px;border-radius:50%;background:{dc};flex-shrink:0;"></div><div style="flex:1;font-size:13px;color:#64748b;">{row["login_time"]}</div><div style="font-size:13px;color:{dc};font-weight:600;">{"✓" if ok_ else "✗"} {txt}</div></div>',unsafe_allow_html=True)

# ── ROUTER ────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    show_auth()
else:
    if (st.session_state.screen=="domain"
            and st.session_state.career_result is None
            and st.session_state.selected_domain is None):
        hist=get_sessions(st.session_state.username)
        if len(hist)>0:
            last=hist.iloc[-1]; restored_domain=str(last.get("domain",""))
            if restored_domain in DOMAINS:
                st.session_state.selected_domain=restored_domain; d_r=DOMAINS[restored_domain]
                if restored_domain not in st.session_state.domain_scores:
                    st.session_state.domain_scores[restored_domain]={}
                st.session_state.domain_scores[restored_domain]["_computed"]={
                    "gpa":float(last.get("gpa",7)),"py":int(last.get("python_skill",5)),
                    "ml":int(last.get("ml_skill",5)),"web":int(last.get("web_interest",5)),
                    "ai":int(last.get("ai_interest",5))}
                st.session_state.career_result=d_r["career"]; st.session_state.screen="results"

    if st.session_state.screen=="domain": show_domain_select()
    elif st.session_state.screen=="quiz": show_quiz()
    else: show_results()