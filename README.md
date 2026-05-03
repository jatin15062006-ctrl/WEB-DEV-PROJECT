<<<<<<< HEAD
# 💸 Expense Tracker

A full-stack personal expense tracking web app built with **Flask** and **PostgreSQL (Neon)**. Each user has their own account and sees only their own expenses.

---

## Features

- 🔐 User signup & login with hashed passwords
- 📊 Dashboard with total spent, monthly spent, and transaction count
- 🍩 Spending breakdown chart by category
- ➕ Add, edit, and delete expenses
- 🔍 Search, filter by category, and sort expenses
- 📱 Responsive design for mobile and desktop

---

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Backend  | Python, Flask, Flask-Login        |
| Database | PostgreSQL via [Neon](https://neon.tech) |
| Frontend | JS, HTML, CSS    |

---

## Project Structure

```
expense-tracker/
├── app.py                  # Flask app, routes, DB logic
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── templates/
│   ├── index.html          # Main dashboard
│   ├── login.html          # Login page
│   └── signup.html         # Signup page
└── static/
    ├── css/style.css
    └── js/script.js
```

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/expense-tracker.git
cd expense-tracker
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>?sslmode=require
SECRET_KEY=your_random_secret_key
```

### 4. Set up the database

The app auto-creates the required tables on startup. If you have an existing `expenses` table without `user_id`, run in your Neon console:

```sql
CREATE TABLE IF NOT EXISTS users (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password TEXT NOT NULL
);

ALTER TABLE expenses ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
```

### 5. Run the app

```bash
python app.py
```

Visit **http://localhost:5001**

---

## API Endpoints

| Method | Endpoint                  | Description              |
|--------|---------------------------|--------------------------|
| GET    | `/api/expenses`           | List user's expenses     |
| POST   | `/api/expenses`           | Add a new expense        |
| GET    | `/api/expenses/<id>`      | Get a single expense     |
| PUT    | `/api/expenses/<id>`      | Update an expense        |
| DELETE | `/api/expenses/<id>`      | Delete an expense        |
| GET    | `/api/stats`              | Dashboard stats          |

All API routes require the user to be logged in.

---

## Built by

**Jatin & Chirag**
=======
# 💸 Expense Tracker

A full-stack personal expense tracking web app built with **Flask** and **PostgreSQL (Neon)**. Each user has their own account and sees only their own expenses.

---

## Features

- 🔐 User signup & login with hashed passwords
- 📊 Dashboard with total spent, monthly spent, and transaction count
- 🍩 Spending breakdown chart by category
- ➕ Add, edit, and delete expenses
- 🔍 Search, filter by category, and sort expenses
- 📱 Responsive design for mobile and desktop

---

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Backend  | Python, Flask, Flask-Login        |
| Database | PostgreSQL via [Neon](https://neon.tech) |
| Frontend | JS, HTML, CSS    |

---

## Project Structure

```
expense-tracker/
├── app.py                  # Flask app, routes, DB logic
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── templates/
│   ├── index.html          # Main dashboard
│   ├── login.html          # Login page
│   └── signup.html         # Signup page
└── static/
    ├── css/style.css
    └── js/script.js
```

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/expense-tracker.git
cd expense-tracker
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>?sslmode=require
SECRET_KEY=your_random_secret_key
```

### 4. Set up the database

The app auto-creates the required tables on startup. If you have an existing `expenses` table without `user_id`, run in your Neon console:

```sql
CREATE TABLE IF NOT EXISTS users (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password TEXT NOT NULL
);

ALTER TABLE expenses ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
```

### 5. Run the app

```bash
python app.py
```

Visit **http://localhost:5001**

---

## API Endpoints

| Method | Endpoint                  | Description              |
|--------|---------------------------|--------------------------|
| GET    | `/api/expenses`           | List user's expenses     |
| POST   | `/api/expenses`           | Add a new expense        |
| GET    | `/api/expenses/<id>`      | Get a single expense     |
| PUT    | `/api/expenses/<id>`      | Update an expense        |
| DELETE | `/api/expenses/<id>`      | Delete an expense        |
| GET    | `/api/stats`              | Dashboard stats          |

All API routes require the user to be logged in.

---

## Built by

**Jatin & Chirag**
>>>>>>> dc5c830 (add Procfile and gunicorn for Render)
