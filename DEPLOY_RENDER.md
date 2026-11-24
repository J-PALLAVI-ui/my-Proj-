# FujiNova — Render Public Deployment Guide

This guide documents how to deploy **FujiNova** (FastAPI backend + React Vite frontend) to [Render](https://render.com) using two connected services:
1. **Python Web Service** (FastAPI Backend + SQLite + Fujikyu Bus GTFS + Stage 3 CrowdSense)
2. **Static Site** (React + TypeScript + Vite Single Page Application)

---

## Architecture Overview

```
                      ┌──────────────────────────────────────────────┐
                      │             Render Static Site               │
                      │         (React + Vite + TypeScript)          │
                      │   https://fujinova-frontend.onrender.com     │
                      └──────────────────────┬───────────────────────┘
                                             │
                       VITE_API_BASE_URL     │ HTTPS REST / Stream
                                             ▼
                      ┌──────────────────────────────────────────────┐
                      │             Render Web Service               │
                      │           (FastAPI + Uvicorn 0.0.0.0)        │
                      │     https://fujinova-backend.onrender.com    │
                      └──────────────┬───────────────────────────────┘
                                     │
                 ┌───────────────────┼────────────────────┐
                 │                   │                    │
                 ▼                   ▼                    ▼
          ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
          │ SQLite (WAL)│     │ Fujikyu GTFS │     │   Hana AI    │
          │  35 Places  │     │ Bus Timetable│     │(Gemini Flash)│
          └─────────────┘     └──────────────┘     └──────────────┘
```

---

## Service 1: Backend (Python Web Service)

Deploy the backend first so you have its public URL ready for the frontend.

### 1. Create Web Service on Render
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** → **Web Service**.
3. Connect your repository: `J-PALLAVI-ui/FujiNova`.

### 2. Configure Service Settings
| Setting | Value |
|---|---|
| **Name** | `fujinova-backend` (or your preferred name) |
| **Region** | Singapore / Oregon / Frankfurt (select closest to target audience) |
| **Branch** | `main` |
| **Root Directory** | *(leave blank / repository root)* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `python -m backend.data.seed_places && uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free (or Starter) |

### 3. Advanced Settings & Health Check
- **Health Check Path**: `/health` (also supports `/api/v1/health`)
- **Auto-Deploy**: Yes

### 4. Backend Environment Variables
In the **Environment** tab of the service, add the following variables:

| Variable Key | Required | Value / Description |
|---|---|---|
| `GEMINI_API_KEY` | **Yes** (for AI chat) | Your Google AI Studio API key (kept strictly server-side). |
| `CORS_ALLOWED_ORIGINS` | **Yes** | Your frontend URL, e.g. `https://fujinova-frontend.onrender.com`. (Multiple URLs can be comma-separated). |
| `FUJINOVA_ENV` | Optional | `production` |
| `FUJINOVA_PRIMARY_MODEL`| Optional | `gemini-3.8-flash` (default) |
| `ENABLE_OPENAI_FALLBACK`| Optional | `False` (strictly disabled to prevent unexpected paid charges) |

> [!IMPORTANT]
> **API Key Security**: `GEMINI_API_KEY` is configured as a secret environment variable in Render. It is never checked into git, never bundled in the frontend, and never sent to the browser client.

---

## Service 2: Frontend (Static Site)

Once your backend service is created and you have its Render URL (e.g., `https://fujinova-backend.onrender.com`), create the static site.

### 1. Create Static Site on Render
1. In the Render Dashboard, click **New +** → **Static Site**.
2. Connect your repository: `J-PALLAVI-ui/FujiNova`.

### 2. Configure Static Site Settings
| Setting | Value |
|---|---|
| **Name** | `fujinova-frontend` (or your preferred name) |
| **Branch** | `main` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |

### 3. Frontend Environment Variables
In the **Environment** tab of the static site, add:

| Variable Key | Required | Value |
|---|---|---|
| `VITE_API_BASE_URL` | **Yes** | The public HTTPS URL of your deployed backend service without trailing slash (e.g. `https://fujinova-backend.onrender.com`). |

> [!NOTE]
> Vite automatically bakes `VITE_API_BASE_URL` into production assets during `npm run build`. In local development, leaving `VITE_API_BASE_URL` empty automatically defaults to using the Vite local proxy (`/health` and `/api` $\rightarrow$ `http://127.0.0.1:8000`).

### 4. SPA Routing & Redirects
The project includes [`frontend/public/_redirects`](file:///d:/FujiNova/frontend/public/_redirects):
```
/*    /index.html   200
```
This is automatically copied into `dist/_redirects` during build. Render reads this file and rewrites all route paths to `/index.html` with HTTP 200, enabling seamless single-page application routing and deep-linking without 404 errors.

---

## Post-Deployment Verification Checklist

Once both services are deployed on Render, verify the deployment:

1. **Backend Health Check:**
   Visit `https://<your-backend>.onrender.com/health` in your browser. Expected response:
   ```json
   {
     "status": "ok",
     "database": "connected (SQLite WAL)",
     "environment": "production",
     "primary_model": "gemini-3.8-flash"
   }
   ```

2. **Database Seeding Verification:**
   Visit `https://<your-backend>.onrender.com/api/attractions`. Expected response:
   - Status: HTTP 200
   - JSON array containing all 35 verified Mount Fuji & Yamanashi destinations.

3. **Stage 3 CrowdSense Status:**
   Visit `https://<your-backend>.onrender.com/api/crowd/status?scenario=high`. Expected response:
   - `classification`: `"SIMULATED"`
   - `real_time_telemetry_status`: `"UNAVAILABLE"`
   - `places`: array of 35 places with calibrated crowd scores.

4. **Frontend Live Application:**
   Open `https://<your-frontend>.onrender.com`.
   - The Mount Fuji hero and CrowdSense dashboard render without blank screens.
   - The 35 verified destinations load in the catalogue grid.
   - Hana AI companion responds to travel inquiries.
   - Deterministic transit routing computes genuine GTFS journeys (e.g. Kawaguchiko Station $\rightarrow$ Oishi Park via Bus 80611, 09:00 $\rightarrow$ 09:27).
