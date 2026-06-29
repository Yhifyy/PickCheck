"""
PickCheck Backend Server
Flask API för pallkontroll.

Kör med: python server.py
API finns på http://localhost:5000/api/...
Frontend serveras på http://localhost:5000/
"""
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import database as db

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# Initiera databasen vid start
db.init_db()


# ============ Frontend (servera statiska filer) ============

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)


# ============ API: Pallar ============

@app.route("/api/pallet/<sscc>", methods=["GET"])
def get_pallet(sscc):
    """Hämta en pall med alla produktrader."""
    pallet = db.get_pallet(sscc)
    if not pallet:
        return jsonify({"error": "Pall hittades inte", "sscc": sscc}), 404
    return jsonify(pallet)


@app.route("/api/pallet", methods=["POST"])
def create_pallet():
    """Skapa/uppdatera en pall (för import från IMI)."""
    data = request.get_json()
    if not data or not data.get("sscc"):
        return jsonify({"error": "SSCC krävs"}), 400

    db.save_pallet(
        sscc=data["sscc"],
        order_number=data.get("order"),
        two_pallets=data.get("twoPallets", False),
        lines=data.get("lines", [])
    )
    return jsonify({"success": True, "sscc": data["sscc"]})


# ============ API: Kontrollresultat ============

@app.route("/api/check", methods=["POST"])
def save_check():
    """Spara ett kontrollresultat."""
    data = request.get_json()
    if not data or not data.get("sscc"):
        return jsonify({"error": "SSCC krävs"}), 400

    check_id = db.save_check_result(data)
    return jsonify({"success": True, "checkId": check_id})


@app.route("/api/check/history", methods=["GET"])
def get_history():
    """Hämta kontrollhistorik."""
    sscc = request.args.get("sscc")
    limit = request.args.get("limit", 50, type=int)
    history = db.get_check_history(sscc=sscc, limit=limit)
    return jsonify(history)


@app.route("/api/check/search", methods=["GET"])
def search_checks():
    """Sök bland kontroller med filter."""
    sscc = request.args.get("sscc", "").strip()
    picker = request.args.get("picker", "").strip()
    checker = request.args.get("checker", "").strip()
    date_from = request.args.get("from", "")
    date_to = request.args.get("to", "")
    status = request.args.get("status", "")
    limit = request.args.get("limit", 100, type=int)

    conn = db.get_connection()
    c = conn.cursor()

    query = "SELECT * FROM check_logs WHERE 1=1"
    params = []

    if sscc:
        query += " AND sscc LIKE ?"
        params.append(f"%{sscc}%")
    if checker:
        query += " AND checked_by LIKE ?"
        params.append(f"%{checker}%")
    if date_from:
        query += " AND date(finished_at) >= ?"
        params.append(date_from)
    if date_to:
        query += " AND date(finished_at) <= ?"
        params.append(date_to)
    if status == "ok":
        query += " AND (wrong_amount_count + wrong_product_count + wrong_pallet_count + extra_count) = 0"
    elif status == "error":
        query += " AND (wrong_amount_count + wrong_product_count + wrong_pallet_count + extra_count) > 0"

    # If picker filter, join with line results
    if picker:
        query = f"""
            SELECT DISTINCT l.* FROM check_logs l
            JOIN check_line_results r ON r.check_log_id = l.id
            WHERE r.picker LIKE ? AND 1=1
        """
        params = [f"%{picker}%"]
        if sscc:
            query += " AND l.sscc LIKE ?"
            params.append(f"%{sscc}%")
        if checker:
            query += " AND l.checked_by LIKE ?"
            params.append(f"%{checker}%")
        if date_from:
            query += " AND date(l.finished_at) >= ?"
            params.append(date_from)
        if date_to:
            query += " AND date(l.finished_at) <= ?"
            params.append(date_to)
        if status == "ok":
            query += " AND (l.wrong_amount_count + l.wrong_product_count + l.wrong_pallet_count + l.extra_count) = 0"
        elif status == "error":
            query += " AND (l.wrong_amount_count + l.wrong_product_count + l.wrong_pallet_count + l.extra_count) > 0"

    query += " ORDER BY finished_at DESC LIMIT ?"
    params.append(limit)

    c.execute(query, params)
    results = [dict(r) for r in c.fetchall()]
    conn.close()

    return jsonify(results)


@app.route("/api/check/<int:check_id>", methods=["GET"])
def get_check_detail(check_id):
    """Hämta detaljer för en specifik kontroll."""
    conn = db.get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM check_logs WHERE id = ?", (check_id,))
    log = c.fetchone()
    if not log:
        conn.close()
        return jsonify({"error": "Kontroll hittades inte"}), 404

    c.execute("SELECT * FROM check_line_results WHERE check_log_id = ?", (check_id,))
    lines = [dict(r) for r in c.fetchall()]

    c.execute("SELECT * FROM check_extras WHERE check_log_id = ?", (check_id,))
    extras = [dict(r) for r in c.fetchall()]

    conn.close()

    return jsonify({
        "log": dict(log),
        "lines": lines,
        "extras": extras
    })


# ============ API: Statistik ============

@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    """Hämta statistik."""
    days = request.args.get("days", 30, type=int)
    stats = db.get_statistics(days=days)
    return jsonify(stats)


@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    """Hämta dashboard-data för idag."""
    conn = db.get_connection()
    c = conn.cursor()

    # Dagens statistik
    c.execute("""
        SELECT 
            COUNT(*) as checks_today,
            SUM(checked_lines) as lines_today,
            SUM(wrong_amount_count + wrong_product_count + wrong_pallet_count) as errors_today,
            AVG(duration_seconds) as avg_duration
        FROM check_logs 
        WHERE date(finished_at) = date('now')
    """)
    today = dict(c.fetchone())

    # Senaste 5 kontrollerna
    c.execute("""
        SELECT id, sscc, checked_by, finished_at, total_lines, checked_lines,
               (wrong_amount_count + wrong_product_count + wrong_pallet_count + extra_count) as total_errors
        FROM check_logs 
        ORDER BY finished_at DESC 
        LIMIT 5
    """)
    recent = [dict(r) for r in c.fetchall()]

    # Denna veckas totaler
    c.execute("""
        SELECT 
            COUNT(*) as checks_week,
            SUM(wrong_amount_count + wrong_product_count + wrong_pallet_count) as errors_week
        FROM check_logs 
        WHERE finished_at >= datetime('now', '-7 days')
    """)
    week = dict(c.fetchone())

    conn.close()

    return jsonify({
        "today": today,
        "recent": recent,
        "week": week
    })


@app.route("/api/statistics/picker/<picker>", methods=["GET"])
def get_picker_stats(picker):
    """Hämta statistik för en specifik plockare."""
    days = request.args.get("days", 30, type=int)
    conn = db.get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT 
            r.product_number,
            r.product_name,
            COUNT(*) as total,
            SUM(CASE WHEN r.checked_qty != r.picked_qty AND r.wrong_product = 0 THEN 1 ELSE 0 END) as wrong_amount,
            SUM(r.wrong_product) as wrong_product,
            SUM(CASE WHEN r.pallet_letter != r.correct_pallet THEN 1 ELSE 0 END) as wrong_pallet
        FROM check_line_results r
        JOIN check_logs l ON r.check_log_id = l.id
        WHERE r.picker = ? AND l.finished_at >= datetime('now', ?)
        GROUP BY r.product_number
        ORDER BY (wrong_amount + wrong_product + wrong_pallet) DESC
    """, (picker, f"-{days} days"))

    products = [dict(r) for r in c.fetchall()]

    c.execute("""
        SELECT 
            strftime('%Y-%m-%d', l.finished_at) as date,
            COUNT(DISTINCT l.id) as checks,
            SUM(CASE WHEN r.checked_qty != r.picked_qty AND r.wrong_product = 0 THEN 1 ELSE 0 END) as errors
        FROM check_line_results r
        JOIN check_logs l ON r.check_log_id = l.id
        WHERE r.picker = ? AND l.finished_at >= datetime('now', ?)
        GROUP BY date
        ORDER BY date DESC
    """, (picker, f"-{days} days"))

    per_day = [dict(r) for r in c.fetchall()]
    conn.close()

    return jsonify({
        "picker": picker,
        "products": products,
        "perDay": per_day
    })


# ============ API: Export ============

@app.route("/api/export/checks", methods=["GET"])
def export_checks():
    """Exportera kontroller som CSV."""
    days = request.args.get("days", 30, type=int)
    conn = db.get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT 
            l.finished_at,
            l.sscc,
            l.checked_by,
            l.total_lines,
            l.checked_lines,
            l.wrong_amount_count,
            l.wrong_product_count,
            l.wrong_pallet_count,
            l.extra_count,
            l.duration_seconds
        FROM check_logs l
        WHERE l.finished_at >= datetime('now', ?)
        ORDER BY l.finished_at DESC
    """, (f"-{days} days",))

    rows = c.fetchall()
    conn.close()

    csv_lines = ["finished_at,sscc,checked_by,total_lines,checked_lines,wrong_amount,wrong_product,wrong_pallet,extra,duration_s"]
    for r in rows:
        csv_lines.append(",".join(str(v) if v is not None else "" for v in r))

    return "\n".join(csv_lines), 200, {
        "Content-Type": "text/csv",
        "Content-Disposition": f"attachment; filename=pickcheck_export_{days}d.csv"
    }


# ============ API: Användare ============

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Registrera en ny användare."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Data saknas"}), 400
    
    username = data.get("username", "").strip()
    password = data.get("password", "")
    display_name = data.get("displayName", "").strip() or username
    
    if not username or len(username) < 2:
        return jsonify({"error": "Användarnamn måste vara minst 2 tecken"}), 400
    if not password or len(password) < 4:
        return jsonify({"error": "Lösenord måste vara minst 4 tecken"}), 400
    
    user = db.register_user(username, password, display_name)
    if not user:
        return jsonify({"error": "Användarnamnet är redan taget"}), 409
    
    return jsonify({"success": True, "user": user})


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Logga in en användare."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Data saknas"}), 400
    
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"error": "Användarnamn och lösenord krävs"}), 400
    
    user = db.login_user(username, password)
    if not user:
        return jsonify({"error": "Fel användarnamn eller lösenord"}), 401
    
    return jsonify({"success": True, "user": user})


@app.route("/api/users", methods=["GET"])
def list_users():
    """Lista alla användare (för admin)."""
    users = db.get_all_users()
    return jsonify(users)


@app.route("/api/auth/check-username/<username>", methods=["GET"])
def check_username(username):
    """Kolla om ett användarnamn är ledigt."""
    exists = db.user_exists(username)
    return jsonify({"available": not exists})


@app.route("/api/admin/reset-password", methods=["POST"])
def admin_reset_password():
    """Återställ lösenord för en användare (admin-funktion)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Data saknas"}), 400
    
    username = data.get("username", "").strip()
    new_password = data.get("newPassword", "")
    
    if not username:
        return jsonify({"error": "Användarnamn krävs"}), 400
    if not new_password or len(new_password) < 4:
        return jsonify({"error": "Lösenord måste vara minst 4 tecken"}), 400
    
    if not db.user_exists(username):
        return jsonify({"error": "Användaren finns inte"}), 404
    
    success = db.reset_password(username, new_password)
    if success:
        return jsonify({"success": True, "message": f"Lösenord återställt för {username}"})
    return jsonify({"error": "Kunde inte återställa lösenord"}), 500


@app.route("/api/admin/set-role", methods=["POST"])
def admin_set_role():
    """Sätt roll för en användare (admin-funktion)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Data saknas"}), 400
    
    username = data.get("username", "").strip()
    role = data.get("role", "user")
    
    if role not in ["user", "admin"]:
        return jsonify({"error": "Ogiltig roll (user eller admin)"}), 400
    
    success = db.set_user_role(username, role)
    if success:
        return jsonify({"success": True, "message": f"{username} är nu {role}"})
    return jsonify({"error": "Kunde inte ändra roll"}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("PickCheck Backend Server")
    print("=" * 50)
    print(f"Database: {db.DB_PATH}")
    print("API: http://localhost:5000/api/...")
    print("Frontend: http://localhost:5000/")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
