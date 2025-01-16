#!/usr/bin/env python3
"""
Script para validação automática da documentação.
Verifica links, formatação e estrutura dos documentos.
"""

import os
import re
import sys
import yaml
import requests
from pathlib import Path
from typing import Dict, List, Set, Tuple
from concurrent.futures import ThreadPoolExecutor

class DocumentationValidator:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checked_links: Set[str] = set()

    def validate_all(self) -> bool:
        """
        Executa todas as validações e retorna True se não houver erros.
        """
        print("🔍 Iniciando validação da documentação...")
        
        # Validar estrutura
        self.validate_structure()
        
        # Validar formatação
        self.validate_formatting()
        
        # Validar links
        self.validate_links()
        
        # Validar frontmatter
        self.validate_frontmatter()
        
        # Exibir resultados
        self.print_results()
        
        return len(self.errors) == 0

    def validate_structure(self):
        """
        Verifica se a estrutura de diretórios está correta.
        """
        print("\n📁 Verificando estrutura de diretórios...")
        
        required_dirs = [
            "architecture",
            "runbooks",
            "api",
            "development"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.docs_dir / dir_name
            if not dir_path.is_dir():
                self.errors.append(f"Diretório obrigatório ausente: {dir_name}")
            else:
                if not (dir_path / "README.md").exists():
                    self.warnings.append(f"README.md ausente em: {dir_name}")

    def validate_formatting(self):
        """
        Verifica a formatação dos arquivos Markdown.
        """
        print("\n📝 Verificando formatação Markdown...")
        
        for md_file in self.docs_dir.rglob("*.md"):
            relative_path = md_file.relative_to(self.docs_dir)
            content = md_file.read_text(encoding="utf-8")
            
            # Verificar título H1
            if not re.search(r"^# .+", content, re.MULTILINE):
                self.errors.append(f"{relative_path}: Falta título H1")
            
            # Verificar hierarquia de títulos
            headers = re.findall(r"^(#{1,6}) ", content, re.MULTILINE)
            for i in range(len(headers)-1):
                if len(headers[i+1]) - len(headers[i]) > 1:
                    self.warnings.append(
                        f"{relative_path}: Pulo na hierarquia de títulos"
                    )
            
            # Verificar links quebrados internos
            internal_links = re.findall(r"\[([^\]]+)\]\(([^http][^)]+)\)", content)
            for text, link in internal_links:
                if not (md_file.parent / link).exists():
                    self.errors.append(
                        f"{relative_path}: Link quebrado para {link}"
                    )

    def validate_links(self):
        """
        Verifica links externos.
        """
        print("\n🔗 Verificando links externos...")
        
        def check_link(url: str) -> Tuple[str, bool]:
            if url in self.checked_links:
                return url, True
            
            try:
                response = requests.head(url, timeout=5)
                is_valid = response.status_code < 400
                self.checked_links.add(url)
                return url, is_valid
            except:
                return url, False
        
        external_links: Set[str] = set()
        
        # Coletar todos os links externos
        for md_file in self.docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            links = re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", content)
            external_links.update(link for _, link in links)
        
        # Verificar links em paralelo
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(check_link, external_links)
            
            for url, is_valid in results:
                if not is_valid:
                    self.warnings.append(f"Link externo quebrado: {url}")

    def validate_frontmatter(self):
        """
        Verifica o frontmatter YAML dos arquivos.
        """
        print("\n📋 Verificando frontmatter...")
        
        required_fields = {"title", "description", "category"}
        
        for md_file in self.docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            
            # Verificar se tem frontmatter
            frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if frontmatter_match:
                try:
                    frontmatter = yaml.safe_load(frontmatter_match.group(1))
                    missing_fields = required_fields - set(frontmatter.keys())
                    if missing_fields:
                        self.warnings.append(
                            f"{md_file.name}: Campos ausentes no frontmatter: {missing_fields}"
                        )
                except yaml.YAMLError:
                    self.errors.append(f"{md_file.name}: Erro no YAML do frontmatter")

    def print_results(self):
        """
        Exibe os resultados da validação.
        """
        print("\n📊 Resultados da Validação")
        print("=" * 50)
        
        if self.errors:
            print("\n❌ Erros encontrados:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\n⚠️  Avisos:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ Nenhum problema encontrado!")
        
        print(f"\nTotal: {len(self.errors)} erros, {len(self.warnings)} avisos")

def main():
    validator = DocumentationValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 