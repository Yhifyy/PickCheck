"""
PickCheck Database Module
SQLite-databas för att spara pallar, kontrollresultat och statistik.
"""
import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "pickcheck.db")


def hash_password(password):
    """Enkel lösenordshashning med SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Skapa alla tabeller om de inte finns."""
    conn = get_connection()
    c = conn.cursor()

    # Användare
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT,
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")

    # Pallar (grunddata från IMI/ordersystem)
    c.execute("""
        CREATE TABLE IF NOT EXISTS pallets (
            sscc TEXT PRIMARY KEY,
            order_number TEXT,
            two_pallets INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Produktrader per pall
    c.execute("""
        CREATE TABLE IF NOT EXISTS pallet_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sscc TEXT NOT NULL,
            product_number TEXT NOT NULL,
            product_name TEXT,
            picker TEXT,
            picked_qty INTEGER DEFAULT 0,
            pallet_letter TEXT DEFAULT 'A',
            correct_pallet TEXT DEFAULT 'A',
            FOREIGN KEY (sscc) REFERENCES pallets(sscc)
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_lines_sscc ON pallet_lines(sscc)")

    # Kontrollloggar (en rad per inskickad check)
    c.execute("""
        CREATE TABLE IF NOT EXISTS check_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sscc TEXT NOT NULL,
            checked_by TEXT,
            finished_at TEXT DEFAULT CURRENT_TIMESTAMP,
            total_lines INTEGER DEFAULT 0,
            checked_lines INTEGER DEFAULT 0,
            wrong_amount_count INTEGER DEFAULT 0,
            wrong_product_count INTEGER DEFAULT 0,
            wrong_pallet_count INTEGER DEFAULT 0,
            extra_count INTEGER DEFAULT 0,
            duration_seconds INTEGER DEFAULT 0,
            FOREIGN KEY (sscc) REFERENCES pallets(sscc)
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_logs_sscc ON check_logs(sscc)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_logs_date ON check_logs(finished_at)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_logs_user ON check_logs(checked_by)")

    # Resultat per produktrad i en check
    c.execute("""
        CREATE TABLE IF NOT EXISTS check_line_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            check_log_id INTEGER NOT NULL,
            product_number TEXT NOT NULL,
            product_name TEXT,
            picker TEXT,
            picked_qty INTEGER DEFAULT 0,
            checked_qty INTEGER,
            pallet_letter TEXT,
            correct_pallet TEXT,
            wrong_product INTEGER DEFAULT 0,
            check_time TEXT,
            FOREIGN KEY (check_log_id) REFERENCES check_logs(id)
        )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS idx_results_log ON check_line_results(check_log_id)")

    # Extra/okända produkter som skannats
    c.execute("""
        CREATE TABLE IF NOT EXISTS check_extras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            check_log_id INTEGER NOT NULL,
            product_code TEXT NOT NULL,
            scan_count INTEGER DEFAULT 1,
            FOREIGN KEY (check_log_id) REFERENCES check_logs(id)
        )
    """)

    conn.commit()
    conn.close()


# ============ Pall-funktioner ============

def get_pallet(sscc):
    """Hämta en pall med alla produktrader."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM pallets WHERE sscc = ?", (sscc,))
    pallet_row = c.fetchone()
    if not pallet_row:
        conn.close()
        return None

    c.execute("SELECT * FROM pallet_lines WHERE sscc = ? ORDER BY id", (sscc,))
    lines = [dict(row) for row in c.fetchall()]
    conn.close()

    return {
        "sscc": pallet_row["sscc"],
        "order": pallet_row["order_number"],
        "twoPallets": bool(pallet_row["two_pallets"]),
        "lines": [{
            "productNumber": l["product_number"],
            "product": l["product_name"],
            "picker": l["picker"],
            "pickedQty": l["picked_qty"],
            "pallet": l["pallet_letter"],
            "correctPallet": l["correct_pallet"]
        } for l in lines]
    }


def save_pallet(sscc, order_number, two_pallets, lines):
    """Spara eller uppdatera en pall med produktrader."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT OR REPLACE INTO pallets (sscc, order_number, two_pallets)
        VALUES (?, ?, ?)
    """, (sscc, order_number, 1 if two_pallets else 0))

    c.execute("DELETE FROM pallet_lines WHERE sscc = ?", (sscc,))

    for line in lines:
        c.execute("""
            INSERT INTO pallet_lines 
            (sscc, product_number, product_name, picker, picked_qty, pallet_letter, correct_pallet)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            sscc,
            line.get("productNumber"),
            line.get("product"),
            line.get("picker"),
            line.get("pickedQty", 0),
            line.get("pallet", "A"),
            line.get("correctPallet", line.get("pallet", "A"))
        ))

    conn.commit()
    conn.close()


# ============ Check-logg-funktioner ============

def save_check_result(data):
    """
    Spara ett kontrollresultat.
    data = {
        sscc, checkedBy, finishedAt, durationSeconds,
        lines: [{productNumber, checkedQty, wrongProduct, checkTime, ...}],
        extras: [{code, count}]
    }
    """
    conn = get_connection()
    c = conn.cursor()

    lines = data.get("lines", [])
    extras = data.get("extras", [])

    total_lines = len(lines)
    checked_lines = sum(1 for l in lines if l.get("checked"))
    wrong_amount = sum(1 for l in lines if l.get("checked") and not l.get("wrongProduct")
                       and l.get("checkedQty") != l.get("pickedQty"))
    wrong_product = sum(1 for l in lines if l.get("wrongProduct"))
    wrong_pallet = sum(1 for l in lines if l.get("pallet") != l.get("correctPallet")
                       and l.get("correctPallet"))
    extra_count = sum(e.get("count", 1) for e in extras)

    c.execute("""
        INSERT INTO check_logs 
        (sscc, checked_by, finished_at, total_lines, checked_lines,
         wrong_amount_count, wrong_product_count, wrong_pallet_count, extra_count, duration_seconds)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("sscc"),
        data.get("checkedBy"),
        data.get("finishedAt", datetime.now().isoformat()),
        total_lines,
        checked_lines,
        wrong_amount,
        wrong_product,
        wrong_pallet,
        extra_count,
        data.get("durationSeconds", 0)
    ))

    check_log_id = c.lastrowid

    for line in lines:
        c.execute("""
            INSERT INTO check_line_results
            (check_log_id, product_number, product_name, picker, picked_qty, checked_qty,
             pallet_letter, correct_pallet, wrong_product, check_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            check_log_id,
            line.get("productNumber"),
            line.get("product"),
            line.get("picker"),
            line.get("pickedQty"),
            line.get("checkedQty"),
            line.get("pallet"),
            line.get("correctPallet"),
            1 if line.get("wrongProduct") else 0,
            line.get("checkTime")
        ))

    for extra in extras:
        c.execute("""
            INSERT INTO check_extras (check_log_id, product_code, scan_count)
            VALUES (?, ?, ?)
        """, (check_log_id, extra.get("code"), extra.get("count", 1)))

    conn.commit()
    conn.close()
    return check_log_id


def get_check_history(sscc=None, limit=50):
    """Hämta kontrollhistorik, valfritt filtrerad på SSCC."""
    conn = get_connection()
    c = conn.cursor()

    if sscc:
        c.execute("""
            SELECT * FROM check_logs WHERE sscc = ?
            ORDER BY finished_at DESC LIMIT ?
        """, (sscc, limit))
    else:
        c.execute("""
            SELECT * FROM check_logs ORDER BY finished_at DESC LIMIT ?
        """, (limit,))

    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ============ Statistik ============

def get_statistics(days=30):
    """Hämta statistik för de senaste N dagarna."""
    conn = get_connection()
    c = conn.cursor()

    stats = {}

    # Totaler
    c.execute("""
        SELECT 
            COUNT(*) as total_checks,
            SUM(wrong_amount_count) as total_wrong_amount,
            SUM(wrong_product_count) as total_wrong_product,
            SUM(wrong_pallet_count) as total_wrong_pallet,
            SUM(extra_count) as total_extra,
            AVG(duration_seconds) as avg_duration
        FROM check_logs
        WHERE finished_at >= datetime('now', ?)
    """, (f"-{days} days",))
    row = c.fetchone()
    stats["totals"] = dict(row) if row else {}

    # Per vecka
    c.execute("""
        SELECT 
            strftime('%Y-%W', finished_at) as week,
            COUNT(*) as checks,
            SUM(wrong_amount_count + wrong_product_count + wrong_pallet_count + extra_count) as errors
        FROM check_logs
        WHERE finished_at >= datetime('now', ?)
        GROUP BY week
        ORDER BY week DESC
    """, (f"-{days} days",))
    stats["perWeek"] = [dict(r) for r in c.fetchall()]

    # Per plockare (mest fel)
    c.execute("""
        SELECT 
            r.picker,
            COUNT(*) as total_lines,
            SUM(CASE WHEN r.checked_qty != r.picked_qty AND r.wrong_product = 0 THEN 1 ELSE 0 END) as wrong_amount,
            SUM(r.wrong_product) as wrong_product,
            SUM(CASE WHEN r.pallet_letter != r.correct_pallet AND r.correct_pallet IS NOT NULL THEN 1 ELSE 0 END) as wrong_pallet
        FROM check_line_results r
        JOIN check_logs l ON r.check_log_id = l.id
        WHERE l.finished_at >= datetime('now', ?)
        GROUP BY r.picker
        ORDER BY (wrong_amount + wrong_product + wrong_pallet) DESC
        LIMIT 20
    """, (f"-{days} days",))
    stats["perPicker"] = [dict(r) for r in c.fetchall()]

    # Produkter med mest fel
    c.execute("""
        SELECT 
            r.product_number,
            r.product_name,
            COUNT(*) as total_checks,
            SUM(CASE WHEN r.checked_qty != r.picked_qty AND r.wrong_product = 0 THEN 1 ELSE 0 END) as wrong_amount,
            SUM(r.wrong_product) as wrong_product
        FROM check_line_results r
        JOIN check_logs l ON r.check_log_id = l.id
        WHERE l.finished_at >= datetime('now', ?)
        GROUP BY r.product_number
        HAVING (wrong_amount + wrong_product) > 0
        ORDER BY (wrong_amount + wrong_product) DESC
        LIMIT 20
    """, (f"-{days} days",))
    stats["productsWithErrors"] = [dict(r) for r in c.fetchall()]

    conn.close()
    return stats


# ---------- Användarhantering ----------

def register_user(username, password, display_name=None, role="user"):
    """Registrera en ny användare. Returnerar användar-dict eller None om användarnamn finns."""
    conn = get_connection()
    c = conn.cursor()
    
    # Kolla om användaren redan finns
    c.execute("SELECT id FROM users WHERE username = ?", (username.lower(),))
    if c.fetchone():
        conn.close()
        return None  # Användarnamn upptaget
    
    password_hash = hash_password(password)
    display = display_name or username
    
    c.execute("""
        INSERT INTO users (username, password_hash, display_name, role)
        VALUES (?, ?, ?, ?)
    """, (username.lower(), password_hash, display, role))
    
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "id": user_id,
        "username": username.lower(),
        "displayName": display,
        "role": role
    }


def login_user(username, password):
    """Verifiera inloggning. Returnerar användar-dict eller None om fel."""
    conn = get_connection()
    c = conn.cursor()
    
    password_hash = hash_password(password)
    
    c.execute("""
        SELECT id, username, display_name, role 
        FROM users 
        WHERE username = ? AND password_hash = ?
    """, (username.lower(), password_hash))
    
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row["id"],
            "username": row["username"],
            "displayName": row["display_name"],
            "role": row["role"]
        }
    return None


def get_all_users():
    """Hämta alla användare (utan lösenord)."""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT id, username, display_name, role, created_at FROM users ORDER BY username")
    users = [dict(r) for r in c.fetchall()]
    conn.close()
    
    return users


def user_exists(username):
    """Kolla om ett användarnamn redan finns."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username.lower(),))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def reset_password(username, new_password):
    """Återställ lösenord för en användare. Returnerar True om lyckades."""
    conn = get_connection()
    c = conn.cursor()
    
    password_hash = hash_password(new_password)
    c.execute("UPDATE users SET password_hash = ? WHERE username = ?", 
              (password_hash, username.lower()))
    
    updated = c.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def set_user_role(username, role):
    """Sätt roll för en användare (user/admin)."""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("UPDATE users SET role = ? WHERE username = ?", 
              (role, username.lower()))
    
    updated = c.rowcount > 0
    conn.commit()
    conn.close()
    return updated


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
