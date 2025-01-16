#!/usr/bin/env python3
"""
Script para setup do ambiente de desenvolvimento.
Instala todas as dependências necessárias e configura o ambiente.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict

class ProjectSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.python_deps = [
            "pytest",
            "pytest-cov",
            "requests",
            "pyyaml",
            "flake8",
            "black",
            "mypy"
        ]
        self.node_deps = {
            "dependencies": [
                "@clerk/nextjs",
                "next",
                "react",
                "react-dom",
                "tailwindcss"
            ],
            "devDependencies": [
                "@playwright/test",
                "@types/node",
                "@types/react",
                "typescript",
                "eslint"
            ]
        }

    def setup_all(self) -> bool:
        """
        Executa todo o processo de setup e retorna True se sucesso.
        """
        print("🚀 Iniciando setup do projeto...")
        
        try:
            # Verificar requisitos
            self.check_requirements()
            
            # Setup Python
            self.setup_python()
            
            # Setup Node.js
            self.setup_node()
            
            # Setup Docker
            self.setup_docker()
            
            # Setup Git hooks
            self.setup_git_hooks()
            
            print("\n✅ Setup concluído com sucesso!")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro durante setup: {e}")
            return False

    def check_requirements(self):
        """
        Verifica se os requisitos básicos estão instalados.
        """
        print("\n🔍 Verificando requisitos...")
        
        requirements = {
            "python": "python --version",
            "node": "node --version",
            "npm": "npm --version",
            "docker": "docker --version",
            "git": "git --version"
        }
        
        for req, cmd in requirements.items():
            try:
                subprocess.run(
                    cmd.split(),
                    check=True,
                    capture_output=True
                )
                print(f"✅ {req} instalado")
            except:
                raise RuntimeError(f"{req} não encontrado")

    def setup_python(self):
        """
        Configura o ambiente Python.
        """
        print("\n🐍 Configurando ambiente Python...")
        
        # Criar e ativar venv
        if not (self.project_root / "venv").exists():
            subprocess.run(
                ["python", "-m", "venv", "venv"],
                cwd=self.project_root,
                check=True
            )
        
        # Instalar dependências
        pip_cmd = str(self.project_root / "venv" / "Scripts" / "pip")
        subprocess.run(
            [pip_cmd, "install", "-U", "pip"],
            check=True
        )
        
        for dep in self.python_deps:
            print(f"Instalando {dep}...")
            subprocess.run(
                [pip_cmd, "install", dep],
                check=True
            )

    def setup_node(self):
        """
        Configura o ambiente Node.js.
        """
        print("\n📦 Configurando ambiente Node.js...")
        
        # Verificar se package.json existe
        if not (self.project_root / "package.json").exists():
            subprocess.run(
                ["npm", "init", "-y"],
                cwd=self.project_root,
                check=True
            )
        
        # Instalar dependências
        for dep in self.node_deps["dependencies"]:
            print(f"Instalando {dep}...")
            subprocess.run(
                ["npm", "install", dep],
                cwd=self.project_root,
                check=True
            )
        
        for dep in self.node_deps["devDependencies"]:
            print(f"Instalando {dep}...")
            subprocess.run(
                ["npm", "install", "-D", dep],
                cwd=self.project_root,
                check=True
            )
        
        # Instalar browsers para Playwright
        subprocess.run(
            ["npx", "playwright", "install"],
            cwd=self.project_root,
            check=True
        )

    def setup_docker(self):
        """
        Configura o ambiente Docker.
        """
        print("\n🐳 Configurando Docker...")
        
        # Verificar se docker-compose.yml existe
        if not (self.project_root / "docker-compose.yml").exists():
            self.create_docker_compose()
        
        # Iniciar serviços
        subprocess.run(
            ["docker", "compose", "pull"],
            cwd=self.project_root,
            check=True
        )

    def setup_git_hooks(self):
        """
        Configura hooks do Git.
        """
        print("\n🔨 Configurando Git hooks...")
        
        hooks_dir = self.project_root / ".git" / "hooks"
        
        # Pre-commit hook
        with open(hooks_dir / "pre-commit", "w") as f:
            f.write("""#!/bin/sh
# Rodar linters
echo "🔍 Executando linters..."
python -m black . --check || exit 1
python -m flake8 . || exit 1
python -m mypy . || exit 1

# Rodar testes unitários
echo "🧪 Executando testes unitários..."
python -m pytest tests/unit || exit 1
""")
        
        # Tornar executável
        os.chmod(hooks_dir / "pre-commit", 0o755)

    def create_docker_compose(self):
        """
        Cria arquivo docker-compose.yml.
        """
        content = """version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: synapse
      POSTGRES_PASSWORD: synapse
      POSTGRES_DB: synapse
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
"""
        
        with open(self.project_root / "docker-compose.yml", "w") as f:
            f.write(content)

def main():
    setup = ProjectSetup()
    success = setup.setup_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 