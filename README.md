# 🤖 Kimi Agent

A fullstack AI agent powered by **Kimi API (Moonshot AI)** with web search, memory, file reading, and REST API support.

## ✨ Features

- 🔍 **Web Search** — Agent can search the web in real-time
- 🧠 **Conversation Memory** — Persistent multi-turn chat history per session
- 📄 **File/Document Reader** — Upload and analyze PDF, TXT, DOCX files
- 🚀 **REST API** — FastAPI backend with OpenAPI docs
- 🖥️ **TypeScript Client** — Typed frontend SDK + simple chat UI

## 🗂️ Project Structure

```
kimi-agent/
├── backend/                  # Python FastAPI backend
│   ├── main.py               # App entry point
│   ├── agent/
│   │   ├── kimi_agent.py     # Core agent logic
│   │   ├── tools/
│   │   │   ├── web_search.py # DuckDuckGo web search tool
│   │   │   └── file_reader.py# File parsing tool
│   │   └── memory/
│   │       └── conversation_memory.py # In-memory + file persistence
│   ├── models/
│   │   └── schemas.py        # Pydantic request/response models
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # TypeScript frontend
│   ├── src/
│   │   ├── api/client.ts     # Typed API client
│   │   ├── types/index.ts    # Shared TypeScript types
│   │   └── index.ts          # CLI chat entry point
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Kimi API Key → [platform.moonshot.cn](https://platform.moonshot.cn)
- (Optional) SerpAPI Key for web search

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your API keys

uvicorn main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env

# Run CLI chat
npm run chat

# Build
npm run build
```

### Docker (All-in-one)

```bash
docker-compose up --build
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send message to agent |
| `POST` | `/chat/upload` | Upload file for analysis |
| `GET` | `/sessions/{id}/history` | Get conversation history |
| `DELETE` | `/sessions/{id}` | Clear session memory |
| `GET` | `/health` | Health check |

## 📦 Environment Variables

### Backend (`.env`)
```env
KIMI_API_KEY=your_kimi_api_key
KIMI_MODEL=moonshot-v1-8k         # moonshot-v1-8k / moonshot-v1-32k / moonshot-v1-128k
SERPAPI_KEY=your_serpapi_key       # Optional, for web search
MEMORY_BACKEND=file                # file | redis
MEMORY_DIR=./data/memory
```

### Frontend (`.env`)
```env
API_BASE_URL=http://localhost:8000
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | Kimi (Moonshot AI) via OpenAI-compatible API |
| Backend | Python, FastAPI, LangChain |
| Memory | In-memory + JSON file persistence |
| Search | DuckDuckGo (free) / SerpAPI |
| File parsing | PyMuPDF (PDF), python-docx, plain text |
| Frontend | TypeScript, Axios |
| Containerization | Docker, Docker Compose |

## 📝 License

MIT
