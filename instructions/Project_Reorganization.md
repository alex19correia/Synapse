# Synapse Project Reorganization Guide

## 1. New Project Structure Overview
```bash
C:/projects/synapse/           # Root directory
├── apps/                      # Application code
│   ├── web/                  # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/         # Next.js 14 app router
│   │   │   ├── components/  # React components
│   │   │   ├── lib/        # Frontend utilities
│   │   │   └── styles/     # CSS and styling
│   │   ├── public/         # Static assets
│   │   ├── package.json
│   │   └── next.config.js
│   │
│   └── api/                 # FastAPI backend
│       ├── src/
│       │   ├── core/       # Core business logic
│       │   ├── routes/     # API endpoints
│       │   ├── services/   # Business services
│       │   └── main.py     # FastAPI entry point
│       ├── tests/
│       └── requirements.txt
│
├── packages/                 # Shared packages
│   ├── core/               # Core business logic
│   │   ├── src/
│   │   │   ├── llm/       # LLM integration
│   │   │   ├── rag/       # RAG system
│   │   │   └── memory/    # Memory system
│   │   └── package.json
│   └── utils/             # Shared utilities
│
├── docs/                    # Documentation
│   ├── api/               # API documentation
│   ├── architecture/      # System architecture
│   └── development/       # Development guides
│
└── infrastructure/          # Infrastructure code
    └── docker/
        ├── api/
        │   └── Dockerfile
        └── web/
            └── Dockerfile
```

## 2. Setup Steps

### 2.1 Create Base Directory Structure
```bash
# Create project root
cd C:/projects
mkdir synapse
cd synapse

# Create main directories
mkdir -p apps/{web,api}/src
mkdir -p packages/{core,utils}/src
mkdir -p docs/{api,architecture,development}
mkdir -p infrastructure/docker/{api,web}
```

### 2.2 Initialize Git
```bash
git init
```

### 2.3 Create Essential Configuration Files

#### apps/api/requirements.txt
```txt
fastapi==0.104.0
uvicorn==0.24.0
pydantic==2.4.2
python-dotenv==1.0.0
```

#### apps/api/src/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Synapse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 2.4 Docker Setup

#### infrastructure/docker/docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: 
      context: ../../apps/api
      dockerfile: ../../infrastructure/docker/api/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/synapse
    depends_on:
      - db
      - redis

  web:
    build:
      context: ../../apps/web
      dockerfile: ../../infrastructure/docker/web/Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000

  db:
    image: postgres:14
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: synapse

  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

### 3. Migration Commands

```bash
# 1. Clone existing repository to temporary location
git clone https://github.com/alex19correia/synapse.git old-synapse

# 2. Move frontend files
mv old-synapse/src/app/* apps/web/src/app/
mv old-synapse/src/components/* apps/web/src/components/

# 3. Move backend files
mv old-synapse/src/api/* apps/api/src/
mv old-synapse/src/core/* packages/core/src/

# 4. Move documentation
mv old-synapse/docs/* docs/

# 5. Move configuration files
mv old-synapse/docker-compose.yml infrastructure/docker/
mv old-synapse/.env.example .env.example
```

### 4. Development Setup

```bash
# Install dependencies
npm install

# Setup Python virtual environment
cd apps/api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start development servers
# Terminal 1 (Frontend)
cd apps/web
npm run dev

# Terminal 2 (Backend)
cd apps/api
uvicorn src.main:app --reload
```

## 5. Next Steps

1. **Update Documentation**
   - Update README.md with new structure
   - Update development guides
   - Update deployment documentation

2. **Setup CI/CD**
   - Configure GitHub Actions
   - Setup deployment pipelines
   - Configure monitoring

3. **Development Workflow**
   - Setup ESLint and Prettier
   - Configure pre-commit hooks
   - Setup testing framework

4. **Monitoring Setup**
   - Configure Grafana dashboards
   - Setup Prometheus metrics
   - Configure logging

Remember to keep the original code safe until the migration is complete and tested. 