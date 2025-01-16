#!/usr/bin/env python3
"""
Script principal para manutenção do projeto.
Executa todos os scripts de manutenção em sequência.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class ProjectMaintainer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = Path(__file__).parent
        self.results: Dict[str, Dict] = {}
        self.start_time = time.time()

    def run_all(self) -> bool:
        """
        Executa todos os scripts de manutenção e retorna True se sucesso.
        """
        print("🚀 Iniciando manutenção do projeto...")
        
        try:
            # Setup
            self.run_script("setup.py", "Setup do ambiente")
            
            # Testes
            self.run_script("run_tests.py", "Execução de testes")
            
            # Documentação
            self.run_script("update_docs.py", "Atualização da documentação")
            self.run_script("validate_docs.py", "Validação da documentação")
            
            # Exibir resultados
            self.print_results()
            
            # Gerar relatório
            self.generate_report()
            
            return all(result["success"] for result in self.results.values())
            
        except Exception as e:
            print(f"\n❌ Erro durante manutenção: {e}")
            return False

    def run_script(self, script_name: str, description: str):
        """
        Executa um script Python e registra o resultado.
        """
        print(f"\n🔄 {description}...")
        
        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            print(f"❌ Script não encontrado: {script_name}")
            return
        
        start = time.time()
        result = subprocess.run(
            ["python", str(script_path)],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        duration = time.time() - start
        
        self.results[script_name] = {
            "description": description,
            "success": result.returncode == 0,
            "output": result.stdout + result.stderr,
            "duration": duration
        }

    def print_results(self):
        """
        Exibe um resumo dos resultados.
        """
        total_time = time.time() - self.start_time
        
        print("\n📊 Resultados da Manutenção")
        print("=" * 50)
        
        all_passed = True
        for script, result in self.results.items():
            status = "✅" if result["success"] else "❌"
            print(f"\n{status} {result['description']}")
            print(f"  Script: {script}")
            print(f"  Duração: {result['duration']:.2f}s")
            if not result["success"]:
                all_passed = False
                print("\n  Saída:")
                print("  " + "\n  ".join(result["output"].split("\n")))
        
        print("\n" + "=" * 50)
        print(f"Tempo total: {total_time:.2f}s")
        print(f"Status: {'✅ Tudo OK' if all_passed else '❌ Falhas encontradas'}")

    def generate_report(self):
        """
        Gera um relatório HTML com os resultados.
        """
        report_dir = self.project_root / "maintenance-reports"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"maintenance_report_{timestamp}.html"
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("""
            <html>
            <head>
                <title>Relatório de Manutenção</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .success { color: green; }
                    .failure { color: red; }
                    pre { background: #f5f5f5; padding: 10px; }
                    .summary { margin: 20px 0; padding: 10px; background: #eee; }
                </style>
            </head>
            <body>
            """)
            
            f.write(f"<h1>Relatório de Manutenção - {timestamp}</h1>")
            
            # Sumário
            total_time = time.time() - self.start_time
            all_passed = all(r["success"] for r in self.results.values())
            f.write(f"""
            <div class="summary">
                <h2>Sumário</h2>
                <p>Status: <span class="{'success' if all_passed else 'failure'}">
                    {'✅ Tudo OK' if all_passed else '❌ Falhas encontradas'}
                </span></p>
                <p>Tempo total: {total_time:.2f}s</p>
                <p>Scripts executados: {len(self.results)}</p>
            </div>
            """)
            
            # Resultados detalhados
            f.write("<h2>Resultados Detalhados</h2>")
            for script, result in self.results.items():
                status_class = "success" if result["success"] else "failure"
                f.write(f"""
                <div class="{status_class}">
                    <h3>{result['description']}</h3>
                    <p>Script: {script}</p>
                    <p>Duração: {result['duration']:.2f}s</p>
                    <pre>{result['output']}</pre>
                </div>
                """)
            
            f.write("</body></html>")
        
        print(f"\n📝 Relatório gerado: {report_file}")

def main():
    maintainer = ProjectMaintainer()
    success = maintainer.run_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 