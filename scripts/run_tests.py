#!/usr/bin/env python3
"""
Script para execução automatizada de testes.
Executa testes unitários, integração, E2E e validação de documentação.
"""

import os
import sys
import time
import subprocess
from typing import List, Dict
from pathlib import Path
from datetime import datetime

class TestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results: Dict[str, Dict] = {}
        self.start_time = time.time()

    def run_all(self) -> bool:
        """
        Executa todos os tipos de teste e retorna True se todos passarem.
        """
        print("🚀 Iniciando suite de testes...")
        
        # Testes unitários
        self.run_unit_tests()
        
        # Testes de integração
        self.run_integration_tests()
        
        # Testes E2E
        self.run_e2e_tests()
        
        # Validação de documentação
        self.run_doc_validation()
        
        # Exibir resultados
        self.print_results()
        
        return all(result["success"] for result in self.results.values())

    def run_unit_tests(self):
        """
        Executa testes unitários com pytest.
        """
        print("\n🔬 Executando testes unitários...")
        
        result = self._run_command([
            "pytest",
            "tests",
            "--ignore=tests/e2e",
            "--ignore=tests/integration",
            "-v",
            "--cov=src",
            "--cov-report=term-missing"
        ])
        
        self.results["unit"] = {
            "success": result.returncode == 0,
            "output": result.stdout.decode(),
            "duration": time.time() - self.start_time
        }

    def run_integration_tests(self):
        """
        Executa testes de integração.
        """
        print("\n🔄 Executando testes de integração...")
        
        # Garantir que serviços necessários estão rodando
        self._ensure_services()
        
        result = self._run_command([
            "pytest",
            "tests/integration",
            "-v",
            "--cov=src",
            "--cov-append"
        ])
        
        self.results["integration"] = {
            "success": result.returncode == 0,
            "output": result.stdout.decode(),
            "duration": time.time() - self.start_time
        }

    def run_e2e_tests(self):
        """
        Executa testes E2E com Playwright.
        """
        print("\n🌐 Executando testes E2E...")
        
        # Garantir que a aplicação está rodando
        self._ensure_app_running()
        
        result = self._run_command([
            "playwright",
            "test",
            "--config=playwright.config.ts"
        ])
        
        self.results["e2e"] = {
            "success": result.returncode == 0,
            "output": result.stdout.decode(),
            "duration": time.time() - self.start_time
        }

    def run_doc_validation(self):
        """
        Executa validação da documentação.
        """
        print("\n📚 Validando documentação...")
        
        result = self._run_command([
            "python",
            "scripts/validate_docs.py"
        ])
        
        self.results["docs"] = {
            "success": result.returncode == 0,
            "output": result.stdout.decode(),
            "duration": time.time() - self.start_time
        }

    def _ensure_services(self):
        """
        Garante que serviços necessários estão rodando.
        """
        services = {
            "postgres": "docker compose up -d postgres",
            "redis": "docker compose up -d redis"
        }
        
        for service, command in services.items():
            print(f"Verificando {service}...")
            if not self._is_service_running(service):
                print(f"Iniciando {service}...")
                subprocess.run(command.split(), check=True)

    def _ensure_app_running(self):
        """
        Garante que a aplicação está rodando para testes E2E.
        """
        if not self._is_port_open(8000):
            print("Iniciando aplicação...")
            subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self._wait_for_port(8000)

    def _is_service_running(self, service: str) -> bool:
        """
        Verifica se um serviço Docker está rodando.
        """
        result = subprocess.run(
            ["docker", "compose", "ps", service, "--quiet"],
            capture_output=True
        )
        return bool(result.stdout)

    def _is_port_open(self, port: int) -> bool:
        """
        Verifica se uma porta está aberta.
        """
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0

    def _wait_for_port(self, port: int, timeout: int = 30):
        """
        Espera até que uma porta esteja disponível.
        """
        start = time.time()
        while time.time() - start < timeout:
            if self._is_port_open(port):
                return
            time.sleep(1)
        raise TimeoutError(f"Porta {port} não ficou disponível em {timeout}s")

    def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """
        Executa um comando e retorna o resultado.
        """
        return subprocess.run(
            command,
            cwd=self.project_root,
            capture_output=True
        )

    def print_results(self):
        """
        Exibe um resumo dos resultados dos testes.
        """
        total_time = time.time() - self.start_time
        
        print("\n📊 Resultados dos Testes")
        print("=" * 50)
        
        all_passed = True
        for test_type, result in self.results.items():
            status = "✅" if result["success"] else "❌"
            print(f"\n{status} {test_type.title()}")
            print(f"  Duração: {result['duration']:.2f}s")
            if not result["success"]:
                all_passed = False
                print("\n  Saída:")
                print("  " + "\n  ".join(result["output"].split("\n")))
        
        print("\n" + "=" * 50)
        print(f"Tempo total: {total_time:.2f}s")
        print(f"Status: {'✅ Todos passaram' if all_passed else '❌ Falhas encontradas'}")

    def generate_report(self):
        """
        Gera um relatório HTML com os resultados.
        """
        report_dir = self.project_root / "test-reports"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"test_report_{timestamp}.html"
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("""
            <html>
            <head>
                <title>Relatório de Testes</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .success { color: green; }
                    .failure { color: red; }
                    pre { background: #f5f5f5; padding: 10px; }
                </style>
            </head>
            <body>
            """)
            
            f.write(f"<h1>Relatório de Testes - {timestamp}</h1>")
            
            for test_type, result in self.results.items():
                status_class = "success" if result["success"] else "failure"
                f.write(f"""
                <h2 class="{status_class}">{test_type.title()}</h2>
                <p>Duração: {result['duration']:.2f}s</p>
                <pre>{result['output']}</pre>
                """)
            
            f.write("</body></html>")
        
        print(f"\n📝 Relatório gerado: {report_file}")

def main():
    runner = TestRunner()
    success = runner.run_all()
    runner.generate_report()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 