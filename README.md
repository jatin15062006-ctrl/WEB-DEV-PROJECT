# 💰 Xpense — Expense Tracker

> Rishihood University | Web Development Capstone Project | 1st Semester

---

## 👥 Team
- **Contributor 1** — Frontend (index.html, add-expense.html, style.css)
- **Contributor 2** — Backend (app.py, Supabase database)

---

## 🗺️ Project Flow / Architecture

```
USER (Browser)
     |
     | opens index.html or add-expense.html
     ↓
FRONTEND  (HTML + CSS + Vanilla JS)
     |
     | fetch("http://localhost:5000/expenses")
     | GET / POST / PUT / DELETE
     ↓
BACKEND  (Python + Flask)   ← app.py
     |
     | SQL queries via psycopg2
     ↓
DATABASE  (Supabase - PostgreSQL)
     └── expenses table
```

---

## ✅ Features

- View all expenses on homepage
- Add new expense via form
- Edit any existing expense
- Delete expense with confirmation
- Search by title or note
- Filter by category
- Sort by date or amount
- Summary: total spent, total count, top category
- Form validation (frontend + backend)
- Responsive design (works on mobile)

---

## 🛠️ Tech Stack

| Part | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend | Python, Flask |
| Database | Supabase (PostgreSQL) |
| Deploy Frontend | Vercel |
| Deploy Backend | Render |

---

## 📁 Folder Structure

```
xpense/
├── frontend/
│   ├── index.html         ← Homepage (lists all expenses)
│   ├── add-expense.html   ← Add & Edit form
│   └── style.css          ← All styling
│
├── backend/
│   ├── app.py             ← Flask server (all API routes)
│   ├── create_table.sql   ← Run this in Supabase to set up DB
│   ├── requirements.txt   ← Python packages
│   └── .env.example       ← Environment variable template
│
└── README.md
```

---

## 🚀 How to Run Locally

### Step 1 — Set up Supabase Database
1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Go to **SQL Editor** and paste the contents of `create_table.sql` and click Run
4. Go to **Project Settings → Database → Connection String → URI**
5. Copy the URI (looks like `postgresql://postgres:...`)

### Step 2 — Run the Backend
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Create .env file and add your database URL
cp .env.example .env
# Open .env and paste your Supabase DATABASE_URL

# Run Flask server
python app.py
# Server runs at http://localhost:5000
```

### Step 3 — Open the Frontend
```bash
cd frontend
# Open index.html with VS Code Live Server
# OR just double-click index.html
```

---

## 📡 API Endpoints

| Method | URL | What it does |
|---|---|---|
| GET | /expenses | Get all expenses (supports search, filter, sort) |
| GET | /expenses/\<id\> | Get one expense |
| POST | /expenses | Create new expense |
| PUT | /expenses/\<id\> | Update expense |
| DELETE | /expenses/\<id\> | Delete expense |

### Example GET with filters:
```
GET /expenses?search=lunch&category=Food&sort=newest
```

### Example POST body:
```json
{
  "title": "Lunch at canteen",
  "amount": 80,
  "date": "2026-04-24",
  "category": "Food",
  "note": "Dal rice"
}
```

---

## 🌍 Deployment

### Frontend → Vercel
1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com) → New Project → Import your repo
3. Set root directory to `frontend`
4. Deploy → get live link ✅

### Backend → Render
1. Go to [render.com](https://render.com) → New Web Service
2. Connect your GitHub repo
3. Set root directory to `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `python app.py`
6. Add environment variable: `DATABASE_URL` = your Supabase URI
7. Deploy → get live link ✅

### After deployment — update frontend
In `index.html` and `add-expense.html`, change:
```js
const API = "http://localhost:5000";
// to:
const API = "https://your-app.onrender.com";
```

---

## 📊 Capstone Evaluation Coverage

| Criteria | Done |
|---|---|
| HTML Semantics (header, main, section, footer, nav) | ✅ |
| CSS Styling + Responsive Design | ✅ |
| JS Logic (DOM, fetch, events) | ✅ |
| Data Validation (client + server side) | ✅ |
| CRUD (Create, Read, Update, Delete) | ✅ |
| Search and Filter | ✅ |
| Flask Backend with Working APIs | ✅ |
| Database Integration (Supabase SQL) | ✅ |
| Frontend + Backend Integration | ✅ |
| Frontend Live Link (Vercel) | ✅ |
| Backend Live Link (Render) | ✅ |
