# Synapse Assistant

## Prerequisites

Before you begin, ensure you have the following installed:
- Git
- Python (Latest stable)
- Node.js (LTS version)
- Docker Desktop
- VS Code + Cursor
- PowerShell 5.1 or later

## Quick Start (New PC Setup)

1. **Clone the Repository**
   ```powershell
   git clone https://github.com/alex19correia/synapse.git
   cd synapse
   ```

2. **Run Setup Script**
   ```powershell
   # This will install all necessary tools and dependencies
   ./scripts/setup.ps1
   ```

3. **Environment Setup**
   ```powershell
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your values
   code .env
   ```

4. **Start Development Environment**
   ```powershell
   # Start all services with Docker
   docker-compose up -d
   
   # Start development servers
   pnpm dev
   ```

## Project Structure

```
synapse/
├── apps/                      # Application code
│   ├── web/                  # Next.js frontend
│   │   └── src/
│   │       ├── app/         # Next.js 14 app router
│   │       ├── components/  # React components
│   │       └── lib/        # Frontend utilities
│   └── api/                 # FastAPI backend
│       └── src/
│           ├── routes/     # API endpoints
│           └── services/   # Business services
├── packages/                 # Shared packages
│   ├── core/               # Core business logic
│   │   └── src/
│   │       ├── llm/       # LLM integration
│   │       └── rag/       # RAG system
│   └── utils/             # Shared utilities
└── docs/                    # Documentation
```

## Development Workflow

1. **Start Development Environment**
   ```bash
   # Start all services
   pnpm dev
   ```

2. **Access Services**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Supabase: http://localhost:54323

3. **Run Tests**
   ```bash
   # Run all tests
   pnpm test
   
   # Run specific workspace tests
   pnpm --filter @synapse/web test
   pnpm --filter @synapse/api test
   ```

## Common Issues & Solutions

### Docker Issues
1. **Services Won't Start**
   - Ensure Docker Desktop is running
   - Try `docker-compose down -v` then `docker-compose up -d`

### Python Issues
1. **Missing Dependencies**
   ```bash
   # Recreate virtual environment
   rm -rf .venv
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r apps/api/requirements.txt
   ```

### Node.js Issues
1. **Dependency Conflicts**
   ```bash
   # Clean install
   pnpm clean
   pnpm install
   ```

## Contributing

1. Create a new branch
   ```bash
   git checkout -b feature/your-feature
   ```

2. Make your changes following our conventions
   - Use TypeScript strict mode
   - Follow ESLint rules
   - Write tests for new features

3. Submit a pull request
   - Ensure all tests pass
   - Update documentation if needed
   - Request review from team members

## License

This project is private and confidential. All rights reserved.
