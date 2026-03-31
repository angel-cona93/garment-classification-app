# Fashion AI

AI-powered garment classification for fashion designers. Upload photos of clothing, get automatic classification (type, style, material, color, season, etc.), then search and filter your collection by any attribute. Add your own annotations on top.

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running
- An API key for your chosen model provider (see below)

### 1. Clone and configure

```bash
cp .env.example .env
```

Open `.env` and set your provider and API key:

```bash
# Pick one: claude | openai | ollama
MODEL_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 2. Run

```bash
docker compose up --build
```

That's it. Open **http://localhost:3000** in your browser.

### 3. Use it

1. Click **Upload** and drop in a garment photo
2. The image is sent to your chosen AI model for classification
3. Once classified, you can filter and search across all your images
4. Click any image to see full details and add your own annotations

---

## Switching Model Providers

The app supports three vision model providers. Change `MODEL_PROVIDER` in `.env` and restart.

| Provider | `MODEL_PROVIDER` | Required env var | Default model |
|----------|-----------------|------------------|---------------|
| Anthropic Claude | `claude` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514` |
| OpenAI | `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| Ollama (local) | `ollama` | `OLLAMA_HOST` (optional) | `llava` |

For Ollama:
- Install Ollama via installer or terminal:
`curl -fsSL https://ollama.com/install.sh | sh` (linux)
`brew install ollama` (macOS)
`winget install Ollama.Ollama` (Windows)
- Start Ollama service:
`sudo systemctl1 start ollama` (Linux)
`brew services start ollama` (macOS or desktop app)
`ollama serve` (Windows or desktop app)
- Pull the model on your host machine (`ollama pull llava`). Docker connects to it via `host.docker.internal`.

To restart after changing providers:

```bash
docker compose down && docker compose up --build
```

### Adding a custom provider

1. Create `app/backend/providers/my_provider.py` subclassing `ImageClassificationProvider`
2. Implement `classify_image(image_path) -> dict`
3. Add one entry to `PROVIDERS` in `app/backend/providers/factory.py`

---

## Local Development (without Docker)

If you prefer running outside Docker:

### Backend

```bash
cd app/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...
uvicorn main:app --reload --port 8000
```

Requires Python 3.11+.

### Frontend

```bash
cd app/frontend
npm install
npm run dev
```

Opens at http://localhost:5173. API calls are proxied to the backend on port 8000.

Requires Node.js 18+.

---

## Running Tests

```bash
pip install pytest httpx Pillow
python3 -m pytest tests/ -v
```

29 tests covering:
- **Parser** (9 tests) — well-formatted, malformed, and edge-case model output
- **Filters** (16 tests) — location, time, combined filters, dynamic filter values, FTS search
- **End-to-end** (4 tests) — upload-classify-filter workflow, annotations, deletion, health check

---

## Project Structure

```
fashion-ai/
├── app/
│   ├── backend/                # Python / FastAPI
│   │   ├── main.py             # App entry, CORS, logging setup
│   │   ├── database.py         # SQLite schema + FTS5
│   │   ├── classifier.py       # Delegates to active provider
│   │   ├── parser.py           # Parses model response → structured attributes
│   │   ├── models.py           # Pydantic models, ImageStatus enum
│   │   ├── providers/          # Plug-and-play model providers
│   │   │   ├── base.py         # Abstract base class + shared image I/O
│   │   │   ├── claude_provider.py
│   │   │   ├── openai_provider.py
│   │   │   ├── ollama_provider.py
│   │   │   └── factory.py      # Provider registry
│   │   ├── routes/             # API endpoints
│   │   └── Dockerfile
│   └── frontend/               # React + TypeScript + Tailwind (Vite)
│       ├── src/
│       │   ├── components/     # UI components
│       │   ├── hooks/          # Data fetching
│       │   └── services/       # API client
│       ├── nginx.conf          # Proxies /api → backend
│       └── Dockerfile
├── tests/                      # pytest suite
├── eval/                       # Model evaluation pipeline
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/images/upload` | Upload image + optional context metadata |
| `GET` | `/api/images` | List images with filter query params |
| `GET` | `/api/images/{id}` | Single image detail |
| `DELETE` | `/api/images/{id}` | Delete image and all associated data |
| `GET` | `/api/images/{id}/file` | Serve the image file |
| `GET` | `/api/filters` | Dynamic filter options (generated from data) |
| `GET` | `/api/search?q=...` | Full-text search |
| `POST` | `/api/images/{id}/annotations` | Add annotation (tag + note) |
| `GET` | `/api/images/{id}/annotations` | List annotations for an image |
| `DELETE` | `/api/annotations/{id}` | Delete an annotation |
| `GET` | `/api/health` | Health check |

## How Classification Works

1. You upload an image via the UI (with optional metadata: location, designer, date)
2. The backend saves the file and returns immediately (`202 Accepted`)
3. A background task sends the image to the configured AI model
4. The model returns a description and structured attributes (garment type, style, material, colors, pattern, season, occasion, consumer profile, trend notes)
5. Results are saved to SQLite and indexed for full-text search
6. The frontend polls until classification completes — or shows the error if it fails

## Design Decisions

- **SQLite + FTS5** — zero-dependency database with built-in full-text search. No external DB service needed.
- **Background classification** — upload returns immediately, frontend polls. Simple and reliable without WebSocket complexity.
- **Dynamic filters** — filter options are generated from `SELECT DISTINCT` queries, never hardcoded. New data surfaces new filters automatically.
- **Comma-separated values** for multi-value attributes — pragmatic for a POC. A production system would use normalized join tables.

---

## Evaluation

The `eval/` directory contains a pipeline for measuring classification accuracy.

```bash
cd eval
python3 download_images.py              # Download 60 test images from Pexels
python3 eval_runner.py                   # Classify + compare to ground truth
python3 eval_runner.py --max-images 10   # Quick run
python3 eval_runner.py --dry-run         # Preview without API calls
cat report.md                            # View results
```

**Dataset:** 60 fashion images from Pexels (free license), 25 hand-labeled with expected attributes.

**Methodology:**
- Single-value fields (garment_type, style, etc.): case-insensitive substring match
- Multi-value fields (color_palette): Jaccard similarity on tokenized color sets

**Expected accuracy ranges:**

| Attribute | Accuracy | Why |
|-----------|----------|-----|
| garment_type | ~85-95% | Silhouettes are visually distinct |
| pattern | ~80-90% | Directly observable in the image |
| season | ~75-85% | Inferred from weight, layering, fabric |
| occasion | ~70-80% | Subjective, depends on cultural context |
| style | ~65-75% | Categories overlap significantly |
| color_palette | ~60-75% | Color naming varies (navy vs dark blue) |
| material | ~50-65% | Requires tactile info not available in photos |

---

## Simplifying Assumptions

- **Single-user** — no auth. Production would add OAuth and per-user libraries.
- **Local file storage** — images on disk. Production would use S3/GCS.
- **No pagination UI** — backend supports it, frontend loads all. Fine for <1000 images.
- **No image preprocessing** — sent to the model as-is. Production would resize/optimize.
- **Location is user-supplied** — the AI does not infer location from the image.

## Documentation

Detailed docs for each part of the codebase:

- **[Backend](docs/backend.md)** — API routes, database schema, classification pipeline, provider system, logging
- **[Frontend](docs/frontend.md)** — React components, hooks, API client, build process
- **[Evaluation](docs/evaluation.md)** — running the eval pipeline, scoring methods, interpreting results
- **[Testing](docs/testing.md)** — test structure, fixtures, what's covered
- **[Docker](docs/docker.md)** — container architecture, volumes, environment variables, common operations

## Future Work

1. User authentication with OAuth
2. Image similarity search via CLIP embeddings
3. Batch upload with progress tracking
4. Collection boards / mood boards
5. PDF lookbook export from filtered collections
6. WebSocket push instead of polling
7. Cloud deployment (AWS/GCP) with S3 storage
