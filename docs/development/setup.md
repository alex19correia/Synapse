# Development Environment Setup 🛠️

## Visão Geral
O ambiente de desenvolvimento do Synapse é projetado para ser consistente, reproduzível e fácil de configurar.

## Setup Inicial

### 1. Pré-requisitos
```python
requirements = {
    "system": {
        "os": ["macOS", "Linux", "WSL2"],
        "memory": "≥ 16GB RAM",
        "storage": "≥ 50GB free"
    },
    "tools": {
        "python": "≥ 3.10",
        "docker": "latest",
        "git": "latest",
        "poetry": "latest"
    }
}
```

### 2. Instalação

#### 2.1 Core Tools
```bash
# macOS (usando Homebrew)
brew install python@3.10
brew install docker
brew install git
curl -sSL https://install.python-poetry.org | python3 -

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3.10 python3.10-venv
sudo apt install docker.io
sudo apt install git
curl -sSL https://install.python-poetry.org | python3 -
```

#### 2.2 Project Setup
```python
setup_steps = {
    "repo": [
        "git clone https://github.com/user/synapse.git",
        "cd synapse"
    ],
    "env": [
        "poetry install",
        "poetry shell",
        "cp .env.example .env"
    ],
    "docker": [
        "docker-compose up -d",
        "docker-compose ps"
    ]
}
```

### 3. Configuração do IDE

#### 3.1 VSCode Settings
```json
{
    "editor.formatOnSave": true,
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.testing.pytestEnabled": true,
    "python.analysis.typeCheckingMode": "basic"
}
```

#### 3.2 Extensions
```python
vscode_extensions = {
    "essential": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-azuretools.vscode-docker"
    ],
    "recommended": [
        "eamodio.gitlens",
        "yzhang.markdown-all-in-one",
        "gruntfuggly.todo-tree"
    ]
}
```

### 4. Development Tools

#### 4.1 Code Quality
```python
code_quality = {
    "linting": {
        "flake8": {
            "max-line-length": 88,
            "extend-ignore": ["E203"]
        },
        "mypy": {
            "strict": True,
            "ignore_missing_imports": True
        }
    },
    "formatting": {
        "black": {
            "line-length": 88,
            "target-version": ["py310"]
        },
        "isort": {
            "profile": "black",
            "multi_line_output": 3
        }
    }
}
```

### 5. Local Services

#### 5.1 Docker Compose
```yaml
services:
  database:
    image: supabase/postgres
    ports: ["5432:5432"]
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      
  redis:
    image: redis:alpine
    ports: ["6379:6379"]
    
  langfuse:
    image: langfuse/langfuse
    ports: ["3000:3000"]
```

### 6. Development Workflow

#### 6.1 Git Flow
```python
git_workflow = {
    "branches": {
        "main": "Produção",
        "develop": "Desenvolvimento",
        "feature/*": "Novas features",
        "bugfix/*": "Correções"
    },
    "commits": {
        "style": "Conventional Commits",
        "prefixes": [
            "feat:", "fix:", "docs:",
            "style:", "refactor:", "test:"
        ]
    }
}
```

### 7. Debug Configuration

#### 7.1 VSCode Launch
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--port",
                "8000"
            ],
            "jinja": true
        }
    ]
}
```

### 8. Ambiente Virtual

#### 8.1 Poetry Config
```toml
[tool.poetry]
name = "synapse"
version = "1.0.0"
description = "Personal AI Assistant"

[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.104.0"
langchain = "^0.0.330"
supabase = "^1.0.3"

[tool.poetry.dev-dependencies]
pytest = "^7.4.0"
black = "^23.9.1"
flake8 = "^6.1.0"
```

### 9. Próximos Passos
1. Setup inicial do ambiente
2. Configurar IDE
3. Instalar dependências
4. Testar serviços locais
5. Configurar git hooks

## Referências
- [Poetry Documentation](https://python-poetry.org/docs/)
- [FastAPI Development](https://fastapi.tiangolo.com/tutorial/)
- [Supabase Local Development](https://supabase.com/docs/guides/local-development) 