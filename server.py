"""
PickCheck Backend Server
Flask API för pallkontroll.

Kör med: python server.py
API finns på http://localhost:5000/api/...
Frontend serveras på http://localhost:5000/
"""
import os
from flask import Flask, request, jsonify, send_from_directory, make_response
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
    """Hämta en pall med alla produktrader + senaste check om den finns."""
    pallet = db.get_pallet(sscc)
    if not pallet:
        return jsonify({"error": "Pall hittades inte", "sscc": sscc}), 404

    latest_check = db.get_latest_check_for_pallet(sscc)
    if latest_check:
        pallet["lastCheck"] = latest_check

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
        lines=data.get("lines", []),
        port=data.get("port"),
        status=data.get("status"),
        pallet_letter=data.get("palletLetter") or data.get("pallet_letter")
    )
    return jsonify({"success": True, "sscc": data["sscc"]})


@app.route("/api/pallet/<sscc>/status", methods=["PUT"])
def update_pallet_status(sscc):
    """Uppdatera pallens status: picking → dropped → on_port."""
    data = request.get_json()
    status = data.get("status")
    if status not in ("picking", "dropped", "on_port"):
        return jsonify({"error": "Ogiltig status. Använd: picking, dropped, on_port"}), 400
    port = data.get("port")
    if status == "on_port" and not port:
        return jsonify({"error": "Port krävs vid status on_port"}), 400
    db.update_pallet_status(sscc, status, port)
    return jsonify({"success": True, "sscc": sscc, "status": status})


@app.route("/api/wms/drop", methods=["POST"])
def wms_drop():
    """WMS/Vocollect: plockaren har droppat pallen vid plastmaskinen."""
    data = request.get_json() or {}
    sscc = (data.get("sscc") or "").strip()
    if not sscc:
        return jsonify({"error": "SSCC krävs"}), 400
    pallet = db.get_pallet(sscc)
    if not pallet:
        return jsonify({"error": "Pall hittades inte"}), 404
    db.update_pallet_status(sscc, "dropped")
    return jsonify({"success": True, "sscc": sscc, "status": "dropped"})


@app.route("/api/wms/scan-port", methods=["POST"])
def wms_scan_port():
    """WMS: outbound har skannat pallen och kört ut den till en port."""
    data = request.get_json() or {}
    sscc = (data.get("sscc") or "").strip()
    port = (data.get("port") or "").strip()
    if not sscc or not port:
        return jsonify({"error": "SSCC och port krävs"}), 400
    pallet = db.get_pallet(sscc)
    if not pallet:
        return jsonify({"error": "Pall hittades inte"}), 404
    db.update_pallet_status(sscc, "on_port", port)
    return jsonify({"success": True, "sscc": sscc, "status": "on_port", "port": port})


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

    if picker:
        query += " ORDER BY l.finished_at DESC LIMIT ?"
    else:
        query += " ORDER BY finished_at DESC LIMIT ?"
    params.append(limit)

    c.execute(query, params)
    results = [dict(r) for r in c.fetchall()]
    db.attach_pickers_to_checks(results, picker_filter=picker)
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
    """Hämta dashboard-data (idag + denna kalendervecka)."""
    return jsonify(db.get_dashboard_data())


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

    c.execute("SELECT name FROM pickers WHERE picker_id = ?", (picker,))
    name_row = c.fetchone()
    conn.close()

    return jsonify({
        "picker": picker,
        "picker_name": name_row["name"] if name_row else None,
        "products": products,
        "perDay": per_day
    })


# ============ API: Export ============

@app.route("/api/statistics/pickers-ranking", methods=["GET"])
def get_pickers_ranking():
    """Hämta plockare-ranking sorterad efter felfrekvens."""
    days = request.args.get("days", 30, type=int)
    conn = db.get_connection()
    c = conn.cursor()

    # Hämta alla plockare med deras statistik
    c.execute("""
        SELECT 
            r.picker,
            pk.name as picker_name,
            COUNT(*) as total_lines,
            SUM(CASE WHEN r.checked_qty IS NOT NULL THEN 1 ELSE 0 END) as checked_lines,
            SUM(CASE WHEN r.checked_qty != r.picked_qty AND r.wrong_product = 0 THEN 1 ELSE 0 END) as wrong_amount,
            SUM(r.wrong_product) as wrong_product,
            SUM(CASE WHEN r.pallet_letter != r.correct_pallet AND r.correct_pallet IS NOT NULL THEN 1 ELSE 0 END) as wrong_pallet,
            COUNT(DISTINCT l.id) as total_checks,
            COUNT(DISTINCT l.sscc) as unique_pallets
        FROM check_line_results r
        JOIN check_logs l ON r.check_log_id = l.id
        LEFT JOIN pickers pk ON pk.picker_id = r.picker
        WHERE l.finished_at >= datetime('now', ?)
        AND r.picker IS NOT NULL AND r.picker != ''
        GROUP BY r.picker, pk.name
        ORDER BY (wrong_amount + wrong_product + wrong_pallet) DESC
    """, (f"-{days} days",))
    
    pickers = []
    for row in c.fetchall():
        picker = dict(row)
        total_errors = (picker['wrong_amount'] or 0) + (picker['wrong_product'] or 0) + (picker['wrong_pallet'] or 0)
        total_lines = picker['total_lines'] or 1
        picker['total_errors'] = total_errors
        picker['error_rate'] = round((total_errors / total_lines) * 100, 1)
        pickers.append(picker)

    # Hämta trend data (jämför denna vecka med förra veckan)
    c.execute("""
        SELECT 
            r.picker,
            SUM(CASE WHEN l.finished_at >= datetime('now', '-7 days') THEN 
                (CASE WHEN r.checked_qty != r.picked_qty AND r.wrong_product = 0 THEN 1 ELSE 0 END) +
                r.wrong_product +
                (CASE WHEN r.pallet_letter != r.correct_pallet AND r.correct_pallet IS NOT NULL THEN 1 ELSE 0 END)
            ELSE 0 END) as errors_this_week,
            SUM(CASE WHEN l.finished_at >= datetime('now', '-14 days') AND l.finished_at < datetime('now', '-7 days') THEN 
                (CASE WHEN r.checked_qty != r.picked_qty AND r.wrong_product = 0 THEN 1 ELSE 0 END) +
                r.wrong_product +
                (CASE WHEN r.pallet_letter != r.correct_pallet AND r.correct_pallet IS NOT NULL THEN 1 ELSE 0 END)
            ELSE 0 END) as errors_last_week,
            SUM(CASE WHEN l.finished_at >= datetime('now', '-7 days') THEN 1 ELSE 0 END) as lines_this_week,
            SUM(CASE WHEN l.finished_at >= datetime('now', '-14 days') AND l.finished_at < datetime('now', '-7 days') THEN 1 ELSE 0 END) as lines_last_week
        FROM check_line_results r
        JOIN check_logs l ON r.check_log_id = l.id
        WHERE l.finished_at >= datetime('now', '-14 days')
        AND r.picker IS NOT NULL AND r.picker != ''
        GROUP BY r.picker
    """)
    
    trends = {row['picker']: dict(row) for row in c.fetchall()}
    
    # Lägg till trend-info till varje plockare
    for picker in pickers:
        trend_data = trends.get(picker['picker'], {})
        this_week = trend_data.get('errors_this_week', 0) or 0
        last_week = trend_data.get('errors_last_week', 0) or 0
        lines_this = trend_data.get('lines_this_week', 0) or 1
        lines_last = trend_data.get('lines_last_week', 0) or 1
        
        rate_this = (this_week / lines_this) * 100 if lines_this > 0 else 0
        rate_last = (last_week / lines_last) * 100 if lines_last > 0 else 0
        
        if rate_this < rate_last:
            picker['trend'] = 'improving'
        elif rate_this > rate_last:
            picker['trend'] = 'worsening'
        else:
            picker['trend'] = 'stable'
        
        picker['errors_this_week'] = this_week
        picker['errors_last_week'] = last_week

    conn.close()

    # Statistik-sammanfattning
    total_pickers = len(pickers)
    pickers_with_errors = len([p for p in pickers if p['total_errors'] > 0])
    avg_error_rate = round(sum(p['error_rate'] for p in pickers) / total_pickers, 1) if total_pickers > 0 else 0

    return jsonify({
        "pickers": pickers,
        "summary": {
            "total_pickers": total_pickers,
            "pickers_with_errors": pickers_with_errors,
            "pickers_without_errors": total_pickers - pickers_with_errors,
            "avg_error_rate": avg_error_rate
        }
    })


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

    # Använd semikolon som separator (standard i svenska Excel)
    csv_lines = ["finished_at;sscc;checked_by;total_lines;checked_lines;wrong_amount;wrong_product;wrong_pallet;extra;duration_s"]
    for r in rows:
        csv_lines.append(";".join(str(v) if v is not None else "" for v in r))

    response = make_response("\n".join(csv_lines))
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=pickcheck_export_{days}d.csv"
    return response


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


@app.route("/api/auth/user/<username>", methods=["GET"])
def get_user_profile(username):
    """Hämta uppdaterat visningsnamn för inloggad användare."""
    user = db.get_user_profile(username)
    if not user:
        return jsonify({"error": "Användare hittades inte"}), 404
    return jsonify(user)


@app.route("/api/auth/check-username/<username>", methods=["GET"])
def check_username(username):
    """Kolla om ett användarnamn är ledigt."""
    exists = db.user_exists(username)
    return jsonify({"available": not exists})


@app.route("/api/admin/reset-password", methods=["POST"])
def admin_reset_password():
    """Återställ lösenord för en användare. Bara admin-användare får göra detta."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Data saknas"}), 400

    requester = data.get("requester", "").strip()
    if not requester:
        return jsonify({"error": "Ingen behörighet (requester saknas)"}), 403
    requester_info = db.get_user_profile(requester)
    if not requester_info or requester_info.get("role") != "admin":
        return jsonify({"error": "Ingen behörighet – bara administratörer kan återställa lösenord"}), 403

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
    """Sätt roll för en användare. Bara admin-användare får ändra roller."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Data saknas"}), 400

    requester = data.get("requester", "").strip()
    if not requester:
        return jsonify({"error": "Ingen behörighet (requester saknas)"}), 403

    requester_info = db.get_user_profile(requester)
    if not requester_info or requester_info.get("role") != "admin":
        return jsonify({"error": "Ingen behörighet – bara administratörer kan ändra roller"}), 403

    username = data.get("username", "").strip()
    role = data.get("role", "user")
    
    if role not in ["user", "admin"]:
        return jsonify({"error": "Ogiltig roll (user eller admin)"}), 400
    
    success = db.set_user_role(username, role)
    if success:
        return jsonify({"success": True, "message": f"{username} är nu {role}"})
    return jsonify({"error": "Kunde inte ändra roll"}), 500


## ---------- Kontrollista API ---------- ##

@app.route("/api/targets", methods=["GET"])
def get_targets():
    """Hämta aktiva kontrollmål med automatisk pall- och port-info."""
    targets = db.get_targets_with_pallets()
    return jsonify(targets)


@app.route("/api/targets", methods=["POST"])
def add_target():
    """Lägg till ett plockare-ID som ska kontrolleras. Bara admin."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Data saknas"}), 400

    requester = data.get("requester", "").strip()
    requester_info = db.get_user_profile(requester) if requester else None
    if not requester_info or requester_info.get("role") != "admin":
        return jsonify({"error": "Ingen behörighet"}), 403

    picker_id = data.get("pickerId", "").strip()
    if not picker_id:
        return jsonify({"error": "Plockare-ID krävs"}), 400

    note = data.get("note", "").strip() or None

    db.add_check_target(picker_id, note=note, added_by=requester)
    return jsonify({"success": True})


@app.route("/api/targets/<int:target_id>", methods=["DELETE"])
def remove_target(target_id):
    """Ta bort ett kontrollmål. Bara admin."""
    requester = request.args.get("requester", "").strip()
    requester_info = db.get_user_profile(requester) if requester else None
    if not requester_info or requester_info.get("role") != "admin":
        return jsonify({"error": "Ingen behörighet"}), 403

    success = db.remove_check_target(target_id)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Kontrollmål hittades inte"}), 404


@app.route("/api/targets/clear", methods=["POST"])
def clear_targets():
    """Rensa alla kontrollmål (nytt skift). Bara admin."""
    data = request.get_json() or {}
    requester = data.get("requester", "").strip()
    requester_info = db.get_user_profile(requester) if requester else None
    if not requester_info or requester_info.get("role") != "admin":
        return jsonify({"error": "Ingen behörighet"}), 403

    db.clear_all_targets()
    return jsonify({"success": True})


## ---------- Port-info API ---------- ##

@app.route("/api/pallets-on-ports", methods=["GET"])
def get_pallets_on_ports():
    """Hämta pallar som står på portar med automatiska avgångstider."""
    pallets = db.get_pallets_on_ports()
    return jsonify({"pallets": pallets})


@app.route("/api/suggest-pallet", methods=["GET"])
def suggest_pallet():
    """Föreslå en random pall att kontrollera (när targets-pallar inte är tillgängliga)."""
    exclude = request.args.get("exclude", "")
    exclude_pickers = [p.strip() for p in exclude.split(",") if p.strip()]
    pallet = db.get_random_available_pallet(exclude_pickers=exclude_pickers)
    if pallet:
        return jsonify({"suggestion": pallet})
    return jsonify({"suggestion": None})


if __name__ == "__main__":
    print("=" * 50)
    print("PickCheck Backend Server")
    print("=" * 50)
    print(f"Database: {db.DB_PATH}")
    print("API: http://localhost:5000/api/...")
    print("Frontend: http://localhost:5000/")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
