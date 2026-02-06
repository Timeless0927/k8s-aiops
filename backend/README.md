# K8s AIOps Agent - Backend

The intelligent core of the K8s AIOps platform. Built with Python, FastAPI, and LangGraph, it orchestrates autonomous troubleshooting, manages state, and interacts with the Kubernetes cluster.

## 🛠️ Architecture

- **Framework**: FastAPI (Async Web Server)
- **AI Engine**: LangGraph (ReAct Agent loop) + LangChain
- **Memory**:
  - **Short-term**: `Beads` (Checkpointer for conversation state)
  - **Long-term**: `ChromaDB` (Vector store for historical insights)
- **Communication**: WebSocket (`/ws/{client_id}`) for real-time streaming
- **Task Queue**: Internal background tasks for alert processing

## 🔌 Plugin System

The backend uses a modular plugin architecture located in `app/plugins/`.
Built-in plugins include:
- **K8sPlugin**: Executes `kubectl` commands (read-only by default).
- **PrometheusPlugin**: Queries metrics via PromQL.
- **LokiPlugin**: Queries logs via LogQL.
- **KnowledgePlugin**: RAG interface for saving/retrieving insights.
- **K8sGPTPlugin**: Integrates `k8sgpt` CLI for deep scanning.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A running Kubernetes cluster (kubeconfig configured)
- OpenAI API Key (or compatible)

### Installation

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   Copy the example env file and configure your credentials:
   ```bash
   cp ../.env.example ../.env
   # Edit .env and set OPENAI_API_KEY, KUBECONFIG_PATH, etc.
   ```

### Running the Server

Start the development server with hot-reload:

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 --env-file ../.env
```

The API will be available at `http://localhost:8000`.

### API Documentation

Once running, visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🧪 Testing

Run the alert simulation to verify the agent's autonomous capabilities:

```bash
python test_alert.py
```

This script sends a mock alert to the webhook endpoint, triggering an investigation session.
