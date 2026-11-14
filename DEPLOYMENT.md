# FlameLens — Production Deployment

This document covers deploying the existing FlameLens app without changing its
architecture:

| Layer    | Technology                     | Recommended host | Config file            |
| -------- | ------------------------------ | ---------------- | ---------------------- |
| Frontend | React 18 + TypeScript + Vite 6 | Vercel           | `frontend/vercel.json` |
| Backend  | FastAPI (Python 3.13)          | Render (Docker)  | `render.yaml`          |
| Data     | Read-only NASA PSI JSON files  | Baked into image | root `Dockerfile`      |

No database, worker, or external object storage is required. The four Stage 1
inventories (`investigations_inventory.json`, `datasets_inventory.json`,
`files_inventory.json`, `storage_summary.json`) are copied into the backend
image at `/app/data/metadata`. Local files outside the repository are never
needed at runtime.

---

## 1. Backend on Render

### Option A — Blueprint (recommended)

1. Push this repository to GitHub.
2. In Render: **New → Blueprint**, select the repository. Render reads
   `render.yaml`.
3. When prompted, set `CORS_ORIGINS` to the Vercel URL (see section 2). AI keys
   are optional.
4. Deploy. The service builds the root `Dockerfile` and exposes:
   - Health: `https://<service>.onrender.com/api/v1/health`
   - OpenAPI: `https://<service>.onrender.com/docs`

### Option B — Manual web service

- Runtime: **Docker**
- Dockerfile path: `./Dockerfile`
- Docker build context: `.` (repository root — required for `data/metadata`)
- Health check path: `/api/v1/health`
- Plan: free (the instance sleeps after inactivity and cold-starts on the next
  request)

### Backend environment variables

| Variable                 | Required | Production value                                   | Notes |
| ------------------------ | -------- | -------------------------------------------------- | ----- |
| `ENVIRONMENT`            | yes      | `production`                                       | Enables production logging/CORS warnings. |
| `DEBUG`                  | yes      | `false`                                            | Image default; keep false. |
| `CORS_ORIGINS`           | yes      | `https://<your-frontend>.vercel.app`               | Comma-separated or JSON list. No trailing slash. |
| `FLAMELENS_METADATA_DIR` | no       | `/app/data/metadata`                               | Already set in the image. |
| `LOG_LEVEL`              | no       | `INFO`                                             | Use `DEBUG` only while troubleshooting. |
| `GEMINI_API_KEY`         | no       | —                                                  | Optional; server-side only. |
| `GEMINI_MODEL`           | no       | `gemini-2.0-flash`                                 | Optional. |
| `GROQ_API_KEY`           | no       | —                                                  | Optional; server-side only. |
| `GROQ_MODEL`             | no       | `llama-3.3-70b-versatile`                          | Optional. |
| `PORT`                   | no       | assigned by Render                                 | The container binds `0.0.0.0:$PORT`. |

Without any AI key the assistant still works using the deterministic,
metadata-grounded fallback. The frontend never receives provider keys.

### Why CORS must be set

The backend allows only `CORS_ORIGINS`. With the default localhost list, the
deployed site's requests are blocked by the browser. After Vercel assigns the
frontend URL, set:

```text
CORS_ORIGINS=https://<your-frontend>.vercel.app
```

Redeploy/restart the Render service. Startup logs a warning while CORS remains
localhost-only in production. Wildcards are supported but `allow_credentials`
is automatically disabled and not recommended.

---

## 2. Frontend on Vercel

### Steps

1. In Vercel: **Add New → Project**, import the repository.
2. Set **Root Directory** to `frontend`.
3. Framework preset: **Vite** (auto-detected). Build command `npm run build`,
   output directory `dist` — also recorded in `frontend/vercel.json`.
4. Add environment variable for **Production** (and Preview if desired):

   ```text
   VITE_API_BASE_URL=https://<your-api>.onrender.com
   ```

   No trailing slash. Vite inlines this at build time, so changing it requires
   a new deployment.
5. Deploy. `frontend/vercel.json` supplies the SPA rewrite
   (`/(.*) → /index.html`), so direct navigation to `/overview`,
   `/investigations`, `/investigations/PSI-25`, `/files`, `/storage`,
   `/comparison`, and `/assistant` all load the app shell.
6. Copy the resulting frontend URL into Render's `CORS_ORIGINS` and restart the
   backend.

### Frontend environment variables

| Variable            | Required in production | Example                            |
| ------------------- | ---------------------- | ---------------------------------- |
| `VITE_API_BASE_URL` | yes                    | `https://flamelens-api.onrender.com` |

The localhost fallback exists only for `vite dev`. A production build without
`VITE_API_BASE_URL` shows a configuration error instead of calling the
visitor's own machine, and export links are disabled.

---

## 3. Local production verification

```powershell
# Build the production backend image from the repository root
docker build -t flamelens-api .

# Run it with production settings
docker run --rm -p 8001:8000 `
  -e ENVIRONMENT=production `
  -e DEBUG=false `
  -e CORS_ORIGINS=http://127.0.0.1:4173 `
  flamelens-api

# In another shell
curl.exe http://127.0.0.1:8001/api/v1/health
curl.exe "http://127.0.0.1:8001/api/v1/analytics/overview"
curl.exe -o nul -w "%{http_code}" "http://127.0.0.1:8001/api/v1/files/export?format=csv"
```

```powershell
# Build/preview the frontend against the container
cd frontend
$env:VITE_API_BASE_URL = "http://127.0.0.1:8001"
npm run build
npm run preview -- --port 4173
```

Then open `http://127.0.0.1:4173/overview` directly (and the other six routes),
confirm data renders, CSV/JSON exports download, comparison works, and the
assistant responds.

### Quick API smoke test

| Check                 | Endpoint |
| --------------------- | -------- |
| Health                | `GET /api/v1/health` |
| Dashboard statistics  | `GET /api/v1/analytics/overview` |
| Investigation list    | `GET /api/v1/investigations` |
| Investigation detail  | `GET /api/v1/investigations/PSI-25` |
| File explorer         | `GET /api/v1/files?page=1&page_size=10` |
| Storage analytics     | `GET /api/v1/analytics/storage` |
| CSV export            | `GET /api/v1/files/export?format=csv` |
| JSON export           | `GET /api/v1/files/export?format=json` |
| Comparison            | `GET /api/v1/comparison?ids=PSI-22,PSI-25` |
| Assistant             | `POST /api/v1/assistant/query` |

---

## 4. Security notes

- `.env` and `frontend/.env` are gitignored; only `.env.example` files are
  committed.
- AI provider keys are read by the backend only. `VITE_*` variables are public
  by definition — never put a secret in one.
- CORS is restricted to `CORS_ORIGINS`; methods are limited to `GET`, `POST`,
  `OPTIONS`.
- Unhandled errors return a generic JSON error; stack traces remain in server
  logs.
- Startup fails fast if any of the four metadata inventories is missing or
  unreadable. Logs include the inventory directory, never HTTP responses.
- `data/knowledge/` (research documents) and offline audit scratch files are
  excluded from the image by `.dockerignore`.

---

## 5. Deployment status

Configuration is prepared and verified locally. **No public deployment has been
performed from this environment**: no Vercel/Render credentials or CLIs are
available, and both hosts require an authenticated account connection.

Manual actions still required:

1. Connect the GitHub repository to Render (Blueprint or Docker service) and
   set `CORS_ORIGINS`.
2. Import `frontend/` into Vercel and set `VITE_API_BASE_URL`.
3. Update Render's `CORS_ORIGINS` with the Vercel URL and restart.
4. Run the verification steps above against the two public URLs.
