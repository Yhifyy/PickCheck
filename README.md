# PickCheck

Lagerkontrollsystem för Dollarstore - används för att kontrollera pallar efter att order har plockats.

![PickCheck Dashboard](https://img.shields.io/badge/version-1.0-blue) ![Python](https://img.shields.io/badge/python-3.8+-green) ![License](https://img.shields.io/badge/license-MIT-orange)

## Funktioner

- **Dashboard** - Översikt med dagens statistik och senaste kontroller
- **Pallkontroll** - Kontrollera plockade varor med A/B-pall filter
- **Fel-pall-varning** - Automatisk varning när varor ligger på fel pall
- **Sök historik** - Sök bland tidigare kontroller (SSCC, plockare, datum, status)
- **Statistik** - Per vecka och per plockare med CSV-export
- **Admin** - Återställ lösenord och hantera användarroller
- **Dark/Light mode** - Anpassat för lagerbelysning
- **Tangentbordsgenvägar** - Snabb kontroll utan mus

## Tangentbordsgenvägar

| Tangent | Funktion |
|---------|----------|
| `Enter` | Bekräfta antal och hoppa till nästa rad |
| `↑` / `↓` | Byt rad |
| `Shift+Enter` | Flagga fel produkt |
| `F2` | Ny pall (SSCC) |
| `F4` | Finish Check |
| `F6` | Ångra check |

## Installation

### Krav
- Python 3.8+
- pip

### Steg

1. **Klona repot**
   ```bash
   git clone https://github.com/Yhifyy/PickCheck.git
   cd PickCheck
   ```

2. **Installera beroenden**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initiera databasen med testdata**
   ```bash
   python seed_data.py
   ```

4. **Starta servern**
   ```bash
   python server.py
   ```

5. **Öppna i webbläsaren**
   ```
   http://localhost:5000
   ```

## Inloggning

Skapa ett konto via "Skapa konto"-fliken eller använd testanvändare:
- **Användarnamn:** `kennart`
- **Lösenord:** `test`

## Projektstruktur

```
PickCheck/
├── index.html      # Huvudsida (login + pallkontroll)
├── app.js          # Frontend-logik
├── styles.css      # Styling med dark mode
├── history.html    # Sök historik
├── stats.html      # Statistik
├── admin.html      # Användarhantering
├── server.py       # Flask backend
├── database.py     # SQLite databashantering
├── seed_data.py    # Testdata
└── requirements.txt
```

## API-endpoints

| Metod | Endpoint | Beskrivning |
|-------|----------|-------------|
| GET | `/pallet/<sscc>` | Hämta palldata |
| POST | `/check` | Spara kontrollresultat |
| GET | `/api/dashboard` | Hämta dashboard-data |
| GET | `/api/statistics` | Hämta statistik |
| GET | `/api/check/search` | Sök kontroller |
| POST | `/api/auth/login` | Logga in |
| POST | `/api/auth/register` | Registrera användare |
| POST | `/api/admin/reset-password` | Återställ lösenord |

## Skärmdumpar

### Dashboard (Dark mode)
- Visar dagens kontroller, fel, och snitt kontrolltid
- Senaste kontroller med status
- Wrong pallet-varningar

### Pallkontroll
- A/B-pall filter
- Produktlista med plockare och antal
- Visuell markering av fel pall

## Teknisk stack

- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **Backend:** Python, Flask
- **Databas:** SQLite
- **Autentisering:** SHA-256 lösenordshashning

## Licens

MIT License - Fritt att använda och modifiera.

---

Utvecklat för Dollarstore lager.
