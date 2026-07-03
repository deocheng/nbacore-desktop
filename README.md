# NBACore Desktop

NBA data management platform built with Electron + Python Flask backend.

## Features

- **Dashboard** — Database overview, top scoring teams, recent games
- **Data Browser** — Browse any table with pagination and search
- **Visualizer** — League scoring rankings, team trends, radar charts, team comparison
- **Analysis** — Player leaderboards (Per Game / Totals / Advanced), player search
- **Crawler Control** — One-click crawl, stop crawl, backfill, full season, custom interval & duration
- **Live Logs** — Real-time SSE log streaming
- **i18n** — Chinese / English language toggle

## Architecture

```
Electron Main (main.js)
  ├── Auto-starts Python API Server (server/api_server.py)
  ├── Window Management (1400x900, dark theme)
  └── Preload Bridge (preload.js)

Python API Server (Flask, port 5577)
  ├── /api/status — Database overview
  ├── /api/tables — Table browser
  ├── /api/teams — Team data
  ├── /api/players — Player search
  ├── /api/leaderboard — Player rankings
  ├── /api/games — Game records
  ├── /api/charts/* — Visualization data
  ├── /api/crawl — Start crawl (subprocess)
  ├── /api/crawl/stop — Stop crawl (kill subprocess)
  ├── /api/crawl/status — Crawl status
  └── /api/logs/stream — SSE log stream

Frontend (renderer/)
  ├── index.html — 5-page dashboard
  ├── css/style.css — Dark theme
  └── js/app.js — i18n + API + ECharts
```

## Prerequisites

- Node.js 18+
- Python 3.10+ with Flask, psycopg2, flask-cors
- PostgreSQL (database: nba, port: 5433)

## Quick Start

```bash
# Install dependencies
npm install

# Install Python packages
pip install flask psycopg2-binary flask-cors

# Start the app
npx electron .

# Or use the launcher scripts
start.bat          # Windows CMD
start.ps1          # PowerShell
```

## Configuration

Edit `server/api_server.py` to change database settings:

```python
DB_CONFIG = {
    'host': 'localhost', 'port': 5433,
    'database': 'nba', 'user': 'postgres', 'password': 'postgres'
}
```

Edit `start.bat` or `start.ps1` to set Python path:

```
set NBA_PYTHON=C:\path\to\python.exe
```

## Crawler Settings

- **Request Interval** — Seconds between HTTP requests (default: 12s)
- **Max Duration** — Auto-stop after N seconds (0 = no limit)
- **Stop Crawl** — Immediately kill the running crawl process

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop | Electron 33 |
| Backend | Python Flask 3 |
| Database | PostgreSQL 17 |
| Charts | ECharts 5.5 |
| Frontend | Vanilla HTML/CSS/JS |
| i18n | Custom data-i18n system |

## License

MIT
