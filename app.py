import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

login_manager = LoginManager(app)
login_manager.login_view = "login_page"




def get_db():
    return psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor, sslmode="require")


def init_db():
    conn = get_db(); cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id         SERIAL PRIMARY KEY,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title      VARCHAR(80) NOT NULL,
            amount     NUMERIC(12,2) NOT NULL,
            category   VARCHAR(40) NOT NULL,
            date       DATE NOT NULL DEFAULT CURRENT_DATE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.commit(); cur.close(); conn.close()


with app.app_context():
    init_db()




class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone(); cur.close(); conn.close()
    return User(row["id"], row["username"]) if row else None




@app.route("/")
@login_required
def index():
    return render_template("index.html", username=current_user.username)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        data = request.get_json()
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM users WHERE username = %s", (data["username"],))
        row = cur.fetchone(); cur.close(); conn.close()
        if row and check_password_hash(row["password"], data["password"]):
            login_user(User(row["id"], row["username"]))
            return jsonify({"ok": True})
        return jsonify({"error": "Invalid username or password"}), 401
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "")
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        conn = get_db(); cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id",
                (username, generate_password_hash(password))
            )
            user_id = cur.fetchone()["id"]
            conn.commit()
            login_user(User(user_id, username))
            return jsonify({"ok": True})
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            return jsonify({"error": "Username already taken"}), 409
        finally:
            cur.close(); conn.close()
    return render_template("signup.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_page"))




@app.route("/api/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    conn = get_db(); cur = conn.cursor()
    uid = current_user.id

    if request.method == "GET":
        category = request.args.get("category", "")
        search   = request.args.get("search", "")
        sort_by  = request.args.get("sort_by", "date")
        order    = request.args.get("order", "desc").upper()

        if sort_by not in ("date", "amount", "created_at"):
            sort_by = "date"
        if order not in ("ASC", "DESC"):
            order = "DESC"

        query  = "SELECT * FROM expenses WHERE user_id = %s"
        params = [uid]

        if category:
            query += " AND category = %s"; params.append(category)
        if search:
            query += " AND title ILIKE %s"; params.append(f"%{search}%")

        query += f" ORDER BY {sort_by} {order}"
        cur.execute(query, params)
        rows = cur.fetchall(); cur.close(); conn.close()
        return jsonify([dict(r) for r in rows])

    if request.method == "POST":
        data = request.get_json()
        if not data.get("title") or not data.get("amount") or not data.get("category"):
            return jsonify({"error": "title, amount and category are required"}), 400
        try:
            amount = float(data["amount"])
            if amount <= 0: raise ValueError
        except (ValueError, TypeError):
            return jsonify({"error": "amount must be a positive number"}), 400

        date = data.get("date") or datetime.today().strftime("%Y-%m-%d")
        cur.execute(
            "INSERT INTO expenses (user_id, title, amount, category, date) VALUES (%s,%s,%s,%s,%s) RETURNING *",
            (uid, data["title"].strip(), amount, data["category"], date)
        )
        new_row = cur.fetchone(); conn.commit(); cur.close(); conn.close()
        return jsonify(dict(new_row)), 201


@app.route("/api/expenses/<int:expense_id>", methods=["GET", "PUT", "DELETE"])
@login_required
def expense_detail(expense_id):
    conn = get_db(); cur = conn.cursor()
    uid = current_user.id

    if request.method == "GET":
        cur.execute("SELECT * FROM expenses WHERE id = %s AND user_id = %s", (expense_id, uid))
        row = cur.fetchone(); cur.close(); conn.close()
        return jsonify(dict(row)) if row else (jsonify({"error": "Not found"}), 404)

    if request.method == "PUT":
        data = request.get_json()
        if not data.get("title") or not data.get("amount") or not data.get("category"):
            return jsonify({"error": "title, amount and category are required"}), 400
        try:
            amount = float(data["amount"])
            if amount <= 0: raise ValueError
        except (ValueError, TypeError):
            return jsonify({"error": "amount must be a positive number"}), 400

        date = data.get("date") or datetime.today().strftime("%Y-%m-%d")
        cur.execute(
            "UPDATE expenses SET title=%s, amount=%s, category=%s, date=%s WHERE id=%s AND user_id=%s RETURNING *",
            (data["title"].strip(), amount, data["category"], date, expense_id, uid)
        )
        updated = cur.fetchone(); conn.commit(); cur.close(); conn.close()
        return jsonify(dict(updated)) if updated else (jsonify({"error": "Not found"}), 404)

    if request.method == "DELETE":
        cur.execute("DELETE FROM expenses WHERE id = %s AND user_id = %s RETURNING id", (expense_id, uid))
        deleted = cur.fetchone(); conn.commit(); cur.close(); conn.close()
        return jsonify({"message": "Deleted"}) if deleted else (jsonify({"error": "Not found"}), 404)


@app.route("/api/stats")
@login_required
def stats():
    conn = get_db(); cur = conn.cursor()
    uid = current_user.id

    cur.execute("SELECT COALESCE(SUM(amount),0) AS total FROM expenses WHERE user_id=%s", (uid,))
    total = float(cur.fetchone()["total"])

    cur.execute(
        "SELECT COALESCE(SUM(amount),0) AS monthly FROM expenses "
        "WHERE user_id=%s AND DATE_TRUNC('month',date)=DATE_TRUNC('month',CURRENT_DATE)", (uid,)
    )
    monthly = float(cur.fetchone()["monthly"])

    cur.execute(
        "SELECT category, COALESCE(SUM(amount),0) AS total FROM expenses "
        "WHERE user_id=%s GROUP BY category ORDER BY total DESC", (uid,)
    )
    by_category = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT COUNT(*) AS cnt FROM expenses WHERE user_id=%s", (uid,))
    count = int(cur.fetchone()["cnt"])

    cur.close(); conn.close()
    return jsonify({"total": total, "monthly": monthly, "by_category": by_category, "count": count})


if __name__ == "__main__":
    app.run(debug=True)
