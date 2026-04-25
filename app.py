import os
from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime

# Load .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

# ── Database Connection ────────────────────────────────────────────────────────

def get_db():
    """Connect to Neon PostgreSQL. SSL is required and handled via the URL."""
    conn = psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=RealDictCursor,
        sslmode="require"
    )
    return conn


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# GET all expenses | POST new expense
@app.route("/api/expenses", methods=["GET", "POST"])
def expenses():
    conn = get_db()
    cur  = conn.cursor()

    if request.method == "GET":
        category = request.args.get("category", "")
        search   = request.args.get("search", "")
        sort_by  = request.args.get("sort_by", "date")
        order    = request.args.get("order", "desc").upper()

        # Whitelist to prevent SQL injection
        if sort_by not in ("date", "amount", "created_at"):
            sort_by = "date"
        if order not in ("ASC", "DESC"):
            order = "DESC"

        query  = "SELECT * FROM expenses WHERE 1=1"
        params = []

        if category:
            query += " AND category = %s"
            params.append(category)

        if search:
            query += " AND title ILIKE %s"
            params.append(f"%{search}%")

        query += f" ORDER BY {sort_by} {order}"

        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([dict(r) for r in rows])

    if request.method == "POST":
        data = request.get_json()

        if not data.get("title") or not data.get("amount") or not data.get("category"):
            return jsonify({"error": "title, amount and category are required"}), 400

        try:
            amount = float(data["amount"])
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"error": "amount must be a positive number"}), 400

        date = data.get("date") or datetime.today().strftime("%Y-%m-%d")

        cur.execute(
            "INSERT INTO expenses (title, amount, category, date) VALUES (%s, %s, %s, %s) RETURNING *",
            (data["title"].strip(), amount, data["category"], date)
        )
        new_row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(dict(new_row)), 201


# GET single | PUT update | DELETE
@app.route("/api/expenses/<int:expense_id>", methods=["GET", "PUT", "DELETE"])
def expense_detail(expense_id):
    conn = get_db()
    cur  = conn.cursor()

    if request.method == "GET":
        cur.execute("SELECT * FROM expenses WHERE id = %s", (expense_id,))
        row = cur.fetchone()
        cur.close(); conn.close()
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(dict(row))

    if request.method == "PUT":
        data = request.get_json()

        if not data.get("title") or not data.get("amount") or not data.get("category"):
            return jsonify({"error": "title, amount and category are required"}), 400

        try:
            amount = float(data["amount"])
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"error": "amount must be a positive number"}), 400

        date = data.get("date") or datetime.today().strftime("%Y-%m-%d")

        cur.execute(
            "UPDATE expenses SET title=%s, amount=%s, category=%s, date=%s WHERE id=%s RETURNING *",
            (data["title"].strip(), amount, data["category"], date, expense_id)
        )
        updated = cur.fetchone()
        conn.commit()
        cur.close(); conn.close()
        if not updated:
            return jsonify({"error": "Not found"}), 404
        return jsonify(dict(updated))

    if request.method == "DELETE":
        cur.execute("DELETE FROM expenses WHERE id = %s RETURNING id", (expense_id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close(); conn.close()
        if not deleted:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "Deleted successfully"})


# GET dashboard stats
@app.route("/api/stats", methods=["GET"])
def stats():
    conn = get_db()
    cur  = conn.cursor()

    # Total all-time spending
    cur.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses")
    total = float(cur.fetchone()["total"])

    # Current month spending
    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) AS monthly FROM expenses "
        "WHERE DATE_TRUNC('month', date) = DATE_TRUNC('month', CURRENT_DATE)"
    )
    monthly = float(cur.fetchone()["monthly"])

    # Per-category totals for chart
    cur.execute(
        "SELECT category, COALESCE(SUM(amount), 0) AS total "
        "FROM expenses GROUP BY category ORDER BY total DESC"
    )
    by_category = [dict(r) for r in cur.fetchall()]

    # Total transaction count
    cur.execute("SELECT COUNT(*) AS cnt FROM expenses")
    count = int(cur.fetchone()["cnt"])

    cur.close(); conn.close()
    return jsonify({
        "total":       total,
        "monthly":     monthly,
        "by_category": by_category,
        "count":       count
    })


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
