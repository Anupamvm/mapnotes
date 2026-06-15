# MapNotes — Land Parcel Evaluation System

A production-quality Django web app for tracking, evaluating, and comparing land parcels on an interactive Google Map.

## Features

- **Multiple Research Maps** — Isolated campaigns (e.g. "FarmLand Research 2026", "Commercial 2027")
- **Interactive Map** — Google Maps with colored priority markers; click map to add property
- **Full Property Profiles** — Location, pricing, ownership, comprehensive site evaluation, distances
- **Site Evaluation** — Water, access, utilities, terrain, legal, environment, future potential ratings
- **Infrastructure Distances** — Highway, dam, town, hospital, school, railway, airport, industrial zone
- **Visit Tracking** — Timeline of field visits per property
- **Rich Notes** — Quick notes + Quill.js rich text, categorized by topic (water/legal/access/price/agent...)
- **Follow-up Reminders** — Inline reminders with done/overdue tracking
- **File Attachments** — Photos, survey maps, PDFs, documents, videos
- **Smart Filtering** — Filter by status, priority, land type, price range, water rating, district, etc.
- **Filter ↔ Map Sync** — HTMX filters update both list and map markers simultaneously
- **Investment Score** — Auto-computed 0–100 score from evaluation ratings (water/access/legal/potential/utilities)
- **Property Comparison** — Select multiple properties for side-by-side comparison
- **Dashboard** — Stats + Chart.js charts by district, status, priority
- **Global Search** — Searches name, address, agent, village, notes
- **Dark Mode** — Toggle with localStorage persistence
- **Keyboard Shortcuts** — `n` (new), `/` (search), `d` (dashboard), `p` (properties)

## Quick Start (Local)

### Prerequisites

- Python 3.11+
- PostgreSQL 14+

### Setup

```bash
# 1. Clone and create virtualenv
git clone https://github.com/Anupamvm/mapnotes.git
cd mapnotes
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements/dev.txt

# 3. Create PostgreSQL database
psql postgres -c "CREATE USER mapnotes WITH PASSWORD 'mapnotes_password';"
psql postgres -c "CREATE DATABASE mapnotes OWNER mapnotes;"

# 4. Configure environment
cp .env.example .env
# Edit .env — add your GOOGLE_MAPS_API_KEY (optional, app works without it)

# 5. Run migrations
python manage.py migrate

# 6. Create admin user
python manage.py createsuperuser

# 7. (Optional) Seed 25 sample Maharashtra properties
python manage.py seed_data

# 8. Start server
python manage.py runserver 8002
```

Open http://localhost:8002 — log in, create or enter a research map.

## Docker

```bash
cp .env.example .env
# Edit .env — set DB_HOST=db for Docker

docker-compose up --build

# First time setup
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py seed_data
```

App runs at http://localhost:8002

## Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Maps JavaScript API** and **Places API**
3. Create an API key and add to `.env`:
   ```
   GOOGLE_MAPS_API_KEY=AIza...
   ```

Without a key the app works fully — map panels are blank.

## Default Dev Credentials

```
URL:      http://localhost:8002
Admin:    http://localhost:8002/admin/
Username: admin
Password: admin123  (if you used createsuperuser --noinput as shown in setup)
```

## Project Structure

```
mapnotes/           Django project config (settings, urls, wsgi)
apps/
  core/             Project (research map) model, dashboard, search, compare
  properties/       Property, SiteEvaluation, Distance, Attachment + views + REST API
  activity/         Visit, Note, FollowUp models + HTMX inline views
templates/          All HTML templates
static/
  js/               map.js (MapManager), filters.js, property_form.js, app.js
  css/              app.css
requirements/
  base.txt          Production dependencies
  dev.txt           + debug toolbar, factory-boy, pytest
  prod.txt          + Sentry
Dockerfile
docker-compose.yml
.env.example
```

## REST API

Available at `/api/properties/` — requires login session.

| Endpoint | Method | Description |
|---|---|---|
| `/api/properties/` | GET | List (mini serializer, filterable, searchable) |
| `/api/properties/<id>/` | GET/PUT/PATCH/DELETE | Full detail |
| `/api/properties/<id>/compute-score/` | POST | Auto-compute investment score |
| `/api/stats/` | GET | Dashboard aggregates for active project |

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `n` | New property |
| `/` | Focus search bar |
| `d` | Go to Dashboard |
| `p` | Go to Properties |
| `Esc` | Go back |

## Marker Colors (by Priority)

| Priority | Color |
|---|---|
| Hot | Red `#ef4444` |
| High | Orange `#f97316` |
| Medium | Yellow `#eab308` |
| Low | Green `#22c55e` |
| Rejected | Gray `#6b7280` |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.1, PostgreSQL |
| API | Django REST Framework |
| Frontend interactivity | HTMX (no page reloads for inline forms) |
| UI | Bootstrap 5.3, Bootstrap Icons |
| Map | Google Maps JavaScript API + Places |
| Charts | Chart.js 4 |
| Rich text | Quill.js |
| Static files | Whitenoise |
| Production server | Gunicorn |
| Container | Docker + PostgreSQL 16 |
