# 🚀 HireIQ

> **Turn your resume into your career roadmap.**

HireIQ is an AI-powered resume analyzer built to help students, fresh graduates, and job seekers understand how well their resume matches a target job role.

Instead of simply telling you whether your resume is "good" or "bad", HireIQ breaks it down into an actionable career report using **Google Gemini AI**.

---

## ✨ What is HireIQ?

Finding out why a resume is not getting shortlisted can be difficult.

HireIQ solves this by allowing a user to:

```text
📄 Upload Resume
       +
🎯 Enter Target Job Role
       ↓
   🤖 HireIQ AI
       ↓
┌─────────────────────────┐
│      ATS Score          │
│      Matched Skills     │
│      Missing Skills     │
│      Strengths          │
│      Weaknesses         │
│      Suggestions        │
└─────────────────────────┘
       ↓
🚀 Improve → Apply → Grow
```

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| 📄 Resume Upload | Upload your resume in PDF format |
| 🎯 Role Matching | Analyze your resume for a specific target role |
| 🤖 Gemini AI | Uses Google Gemini for intelligent resume analysis |
| 📊 ATS Score | Generates an ATS-style score from 0–100 |
| ✅ Matched Skills | Shows skills already relevant to the target role |
| ❌ Missing Skills | Identifies relevant skills that are missing |
| 💪 Strengths | Highlights strong areas in your resume |
| ⚠️ Weaknesses | Identifies potential gaps |
| 💡 Suggestions | Provides practical ways to improve |
| 🔐 Authentication | Secure registration and login |
| 🔑 JWT | Protects authenticated API endpoints |
| 🎨 Glassmorphism UI | Modern dark SaaS-style interface |
| ☁️ Vercel Ready | Designed for web deployment |

---

## 🧠 How HireIQ Works

```text
                    ┌──────────────────┐
                    │      USER        │
                    └────────┬─────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Register / Login     │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ JWT Authentication  │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ HireIQ Dashboard    │
                  └──────────┬──────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
          Upload Resume            Target Role
                 │                       │
                 └───────────┬───────────┘
                             ▼
                  ┌─────────────────────┐
                  │   FastAPI Backend   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Extract PDF Text    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Google Gemini AI  │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Resume Intelligence │
                  └──────────┬──────────┘
                             │
                             ▼
       ┌────────────┬────────┼────────┬────────────┐
       ▼            ▼        ▼        ▼            ▼
   ATS Score     Skills   Gaps    Strengths   Suggestions
```

---

## 🛠️ Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Glassmorphism UI

### Backend

- Python
- FastAPI
- Uvicorn
- PyPDF

### Artificial Intelligence

- Google Gemini API
- Google GenAI SDK

### Authentication

- JWT
- PyJWT
- pwdlib
- Argon2 password hashing

### Database

- SQLite for local development
- PostgreSQL recommended for production

### Deployment

- Vercel

---

## 📂 Project Structure

```text
HireIQ/
│
├── api/
│   └── index.py
│
├── backend/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   └── resume_parser.py
│
├── index.html
├── style.css
├── script.js
├── requirements.txt
├── vercel.json
├── .env
├── .gitignore
└── README.md
```

---

## ⚡ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/LASHMISIMAN-K/HireIQ.git
cd HireIQ
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=your_jwt_secret
```

Generate a secure JWT secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### ⚠️ Security

Never commit `.env` to GitHub.

Recommended `.gitignore`:

```gitignore
.env
hireiq.db
__pycache__/
*.pyc
```

---

## ▶️ Run HireIQ Locally

From the project root:

```bash
uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API health check:

```text
http://127.0.0.1:8000/api/
```

Expected response:

```json
{
  "message": "HireIQ API is running 🚀"
}
```

---

## 🔌 API Endpoints

### Register

```http
POST /api/register
```

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

### Login

```http
POST /api/login
```

```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

### Current User

```http
GET /api/me
```

Header:

```text
Authorization: Bearer <JWT_TOKEN>
```

### Analyze Resume

```http
POST /api/analyze
```

Requires:

```text
Authorization: Bearer <JWT_TOKEN>
```

Form data:

```text
resume: resume.pdf
job_role: Frontend Developer
```

---

## 📊 Example Analysis

For a target role such as:

```text
Frontend Developer
```

HireIQ can produce a report such as:

```json
{
  "ats_score": 82,
  "summary": "The resume is well aligned with the target role.",
  "matched_skills": [
    "HTML",
    "CSS",
    "JavaScript",
    "React"
  ],
  "missing_skills": [
    "TypeScript",
    "Testing"
  ],
  "strengths": [
    "Strong frontend development skills",
    "Relevant project experience"
  ],
  "weaknesses": [
    "Limited testing experience"
  ],
  "suggestions": [
    "Add TypeScript projects",
    "Include testing experience"
  ]
}
```

---

## 🔒 Authentication Flow

```text
Register
   ↓
Password hashed with Argon2
   ↓
User stored in database
   ↓
JWT token generated
   ↓
Token stored by frontend
   ↓
Authenticated API requests
   ↓
Protected HireIQ features
```

Plain-text passwords are not intended to be stored. Passwords are hashed before being saved.

---

## ☁️ Deployment

HireIQ is structured for deployment on Vercel.

FastAPI entry point:

```text
api/index.py
```

Contents:

```python
from backend.main import app
```

Set the Vercel project root directory to:

```text
./
```

Add these environment variables to Vercel:

```text
GEMINI_API_KEY
JWT_SECRET_KEY
```

For the current setup, `vercel.json` can contain:

```json
{}
```

### Production Database

SQLite is suitable for local development.

For production, use a persistent hosted PostgreSQL database instead of relying on a local SQLite file in the serverless environment.

---

## 🎯 Why HireIQ?

A resume is more than a document.

It is your **first conversation with a recruiter**.

HireIQ helps turn that conversation into something stronger by answering:

> **"How well does my resume fit the job I want?"**

Instead of blindly applying to jobs, users can identify gaps and improve their resume strategically.

---

## 🔮 Future Roadmap

### Phase 1 — Core AI

- [x] PDF resume parsing
- [x] Target role analysis
- [x] ATS-style scoring
- [x] Skill matching
- [x] Missing skill detection
- [x] Strengths and weaknesses
- [x] AI suggestions


---

## 💻 Example User Journey

```text
"I want a Frontend Developer job."

              ↓

        Upload Resume

              ↓

       HireIQ analyzes it

              ↓

          ATS: 82/100

              ↓

     ┌──────────────────┐
     │ Strong           │
     │ HTML              │
     │ CSS               │
     │ JavaScript        │
     │ React             │
     └──────────────────┘

              ↓

     Missing:
     TypeScript
     Testing

              ↓

     Improve Resume

              ↓

       Apply with confidence 🚀
```

---

## 👨‍💻 Author

### LASHMISIMAN K

B.Tech — Computer Science Engineering  
IoT and Automation

GitHub: https://github.com/LASHMISIMAN-K

---

## ⭐ Support

If you find HireIQ useful, consider giving the repository a ⭐ on GitHub.

---

## 📜 License

This project is currently intended for educational and development purposes.
