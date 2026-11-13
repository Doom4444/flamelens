# 🔥 FlameLens
### Intelligent Discovery & Analysis of Microgravity Combustion Research

<p align="center">
  <strong>NASA Space Apps Challenge 2026</strong><br>
  Challenge: Flame in Freefall
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Challenge-NASA%20Space%20Apps-0B3D91?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-In%20Development-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-FastAPI-009688?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-3178C6?style=for-the-badge" />
</p>

---

## 🚀 Overview

**FlameLens** is an AI-powered scientific discovery and analysis platform designed to help researchers, engineers, and space enthusiasts explore and understand NASA's microgravity combustion research.

Combustion experiments conducted in microgravity provide valuable insights into flame behavior, fire dynamics, and spacecraft fire safety. However, navigating scientific investigations, datasets, and experimental results can be challenging.

FlameLens aims to bridge this gap by combining scientific data processing, numerical analysis, interactive visualization, and Retrieval-Augmented Generation (RAG) into one unified platform.

Our goal is to transform complex scientific information into accessible, searchable, comparable, and understandable knowledge.

## 🎯 Project Objectives

- Centralize and organize relevant NASA combustion research information.
- Simplify discovery of scientific investigations and associated datasets.
- Enable comparisons between compatible experimental parameters and results.
- Visualize experimental measurements and trends.
- Provide a conversational AI assistant grounded in scientific sources.
- Support evidence-based insights relevant to fire safety in space exploration.

## ✨ Planned Features

### 1. 🔎 Scientific Investigation Explorer
- Browse NASA PSI investigations.
- Search and filter scientific records.
- Explore research objectives, methodologies, and findings.
- Discover associated datasets and available files.

### 2. 📊 Experimental Data Analysis
- Extract and process available numerical datasets.
- Identify scientific parameters and measurement units.
- Normalize compatible measurements.
- Generate statistical summaries.
- Analyze experimental time-series data where available.

### 3. ⚖️ Investigation Comparison
- Compare selected investigations and datasets.
- Identify compatible experimental parameters.
- Visualize numerical differences and trends.
- Highlight missing information and scientific limitations.

### 4. 🤖 AI Scientific Assistant
- Ask natural-language questions about combustion research.
- Retrieve relevant information from NASA PSI records.
- Maintain conversational context.
- Explain scientific findings with source references.
- Invoke analytical tools to support numerical comparisons.

### 5. 📈 Interactive Visualization
- Explore experimental measurements.
- Compare scientific parameters through interactive charts.
- Visualize trends and statistical summaries.
- Present results with scientific context and provenance.

---

## 🧠 System Architecture

FlameLens follows a **Modular Monolith Architecture** to simplify development, integration, and deployment.

```text
                    USER / RESEARCHER
                           |
                           v
                  REACT FRONTEND
                           |
                        REST API
                           |
                           v
                    FASTAPI BACKEND
                           |
         +-----------------+-----------------+
         |                 |                 |
         v                 v                 v
    DATA PIPELINE     SCIENTIFIC ENGINE    AI ENGINE
         |                 |                 |
         v                 v                 v
     NASA PSI          PANDAS / NUMPY      LLM PROVIDERS
     EXTRACTION        SCIPY / PLOTLY      EMBEDDINGS
         |                 |                 |
         +-----------------+-----------------+
                           |
                           v
                  POSTGRESQL + PGVECTOR
                           |
              +------------+------------+
              |                         |
              v                         v
        SCIENTIFIC DATA             RAG STORAGE
```

### Core Components

| Component | Responsibility |
|---|---|
| Frontend | User interface, exploration, comparison, visualization |
| Backend API | Application endpoints and service orchestration |
| Data Pipeline | NASA PSI discovery, extraction, processing, ingestion |
| Scientific Engine | Parameter mapping, unit conversion, validation, analysis |
| AI Engine | LLM integration, RAG, semantic retrieval, tool calling |
| Database | Scientific metadata, measurements, embeddings, conversations |

---

## 🛠️ Technology Stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- Plotly.js
- TanStack Query

### Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Alembic

### Data Engineering & Scientific Computing
- Pandas
- NumPy
- SciPy
- PyArrow
- CSV / Parquet

### Database & Retrieval
- PostgreSQL
- pgvector
- JSONB

### Artificial Intelligence
- Gemini API (initial hosted candidate)
- Ollama (local inference option)
- Groq (optional provider)
- BAAI/bge-small-en-v1.5 (initial embedding candidate)
- Retrieval-Augmented Generation (RAG)

### Development & Deployment
- Git / GitHub
- Docker
- Docker Compose
- Vercel
- Render
- Supabase

---

## 🛰️ Data Source

Our primary scientific data source is:

**NASA Physical Sciences Informatics (PSI)**

- [NASA PSI Repository — Combustion Science](https://psi.nasa.gov/physci/repo/search?q=combustion)
- [NASA PSI Repository](https://psi.nasa.gov/physci/repo)

The data pipeline is designed to discover investigations, datasets, files, and available scientific metadata before selecting experimental data for processing.

### Data Processing Strategy

1. Discover available investigations.
2. Inventory associated datasets and files.
3. Extract metadata and file information.
4. Select relevant files for downloading.
5. Parse and validate available measurements.
6. Map scientific parameters and normalize units.
7. Store structured metadata and analytical outputs.
8. Make validated information available to the dashboard and AI assistant.

**Scientific integrity:** Original measurements, units, source references, and processing information must be preserved. Comparisons are performed only after compatibility checks.

---

## 📁 Project Structure

```text
flamelens/
│
├── docs/
│   ├── architecture.md
│   ├── database-schema.md
│   ├── api-contracts.md
│   ├── data-dictionary.md
│   ├── ingestion-strategy.md
│   └── deployment-guide.md
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── hooks/
│       ├── types/
│       └── utils/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── data_pipeline/
│   │   ├── scientific/
│   │   ├── ai/
│   │   └── utils/
│   │
│   ├── migrations/
│   └── tests/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── metadata/
│   └── samples/
│
├── scripts/
│
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

---

## 🗄️ Database Overview

The database is designed around the following entities:

| Entity | Purpose |
|---|---|
| `research_areas` | Scientific research classifications |
| `investigations` | NASA PSI investigation records |
| `investigation_relationships` | Relationships between investigations |
| `datasets` | Dataset collections |
| `data_files` | Individual PSI data files |
| `parameter_definitions` | Canonical scientific parameters |
| `file_parameters` | Original-to-canonical parameter mappings |
| `measurement_series` | Extracted numerical measurements |
| `measurement_summaries` | Statistical summaries |
| `analysis_runs` | Scientific analysis executions |
| `analysis_results` | Analysis outputs |
| `documents` | Scientific text sources |
| `document_chunks` | RAG document chunks and embeddings |
| `conversations` | Chatbot sessions |
| `messages` | Conversation messages |
| `ingestion_runs` | Data pipeline executions |
| `ingestion_logs` | Pipeline execution logs |

For the detailed entity relationships and field definitions, see:

[`docs/database-schema.md`](docs/database-schema.md)

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.11+
- Node.js and npm
- Git
- Docker Desktop
- PostgreSQL (if running without Docker)

### 1. Clone the Repository

```bash
git clone https://github.com/Doom4444/flamelens.git
cd flamelens
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Update `.env` with the required database and AI provider credentials.

Never commit real API keys or credentials.

### 3. Backend Setup

```bash
cd backend

python -m venv .venv
```

Activate the environment:

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

API documentation:

```text
http://localhost:8000/docs
```

### 4. Frontend Setup

Open another terminal:

```bash
cd frontend

npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

### 5. Local Docker Deployment

Once Docker configuration is implemented:

```bash
docker compose up --build
```

This will provide the local deployment environment using the same application architecture as the cloud deployment.

---

## 🌿 Git Workflow

The project uses feature branches for parallel development.

| Branch | Owner | Responsibility |
|---|---|---|
| `main` | Team | Stable integrated application |
| `adham-backend` | Adham | Database, backend architecture, scientific engine |
| `mariam-backend` | Mariam | FastAPI endpoints and backend integration |
| `toka-dataflow` | Toka | NASA PSI data engineering pipeline |
| `Mariam-AI` | Mariam | LLM integration and conversational AI |
| `Mira-AI` | Mira | Embeddings, semantic search, and RAG |

### Development Workflow

```text
Developer Branch
       |
       v
   Commit Changes
       |
       v
  Push to GitHub
       |
       v
 Create Pull Request
       |
       v
 Review and Test
       |
       v
 Merge into main
```

### Basic Commands

Switch to your assigned branch:

```bash
git switch adham-backend
```

Pull the latest changes:

```bash
git pull origin adham-backend
```

Commit your changes:

```bash
git add .
git commit -m "feat: implement database models"
```

Push:

```bash
git push origin adham-backend
```

Create a Pull Request to merge your branch into `main`.

**Important:** Always work on your assigned branch. Avoid direct commits to `main`.

---

## 👥 Team

| Member | Role |
|---|---|
| Adham | Backend Architecture, Data Analysis & Scientific Engine |
| Mariam | Backend Development & API Integration |
| Toka | Data Engineering & NASA PSI Pipeline |
| Mariam | AI Application & LLM Integration |
| Mira | Machine Learning, Embeddings & RAG |

---

## 🔬 Scientific Principles

FlameLens is designed around several scientific data integrity principles:

- Preserve original NASA source information.
- Maintain traceability between results and source files.
- Validate parameter meaning and units before comparison.
- Distinguish measured values from derived results.
- Report missing data and comparison limitations.
- Avoid unsupported scientific conclusions.
- Keep analytical calculations separate from LLM-generated explanations.

---

## 🚧 Development Status

The project architecture and repository structure have been initialized.

| Component | Status |
|---|---|
| Repository initialization | ✅ Completed |
| Architecture design | ✅ Defined |
| Database schema design | ✅ Defined |
| Team branch setup | 🔄 Initialized |
| PSI data inventory | 🔄 In progress |
| Backend implementation | ⏳ Planned |
| Frontend implementation | ⏳ Planned |
| Scientific comparison engine | ⏳ Planned |
| RAG and AI assistant | ⏳ Planned |
| Cloud deployment | ⏳ Planned |
| Local Docker deployment | ⏳ Planned |

---

## 🎯 Final Vision

FlameLens aims to make microgravity combustion research more accessible and actionable by connecting scientific data discovery, numerical analysis, interactive visualization, and AI-assisted understanding.

**From experimental data to scientific insight.**

---

<p align="center">
  Built for NASA Space Apps Challenge 2026 🚀
</p>