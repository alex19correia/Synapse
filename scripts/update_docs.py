#!/usr/bin/env python3
"""
Script para atualização automática da documentação.
Gera índices, valida links e formata documentos.
"""

import os
import re
import sys
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

class DocumentationUpdater:
    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.updated_files: Set[str] = set()

    def update_all(self) -> bool:
        """
        Executa todas as atualizações e retorna True se sucesso.
        """
        print("🔄 Iniciando atualização da documentação...")
        
        try:
            # Backup
            self.create_backup()
            
            # Atualizar estrutura
            self.update_structure()
            
            # Atualizar índices
            self.update_indexes()
            
            # Atualizar referências
            self.update_references()
            
            # Formatar documentos
            self.format_documents()
            
            # Validar alterações
            self.validate_changes()
            
            print("\n✅ Documentação atualizada com sucesso!")
            return True
            
        except Exception as e:
            print(f"\n❌ Erro durante atualização: {e}")
            self.restore_backup()
            return False

    def create_backup(self):
        """
        Cria backup da documentação.
        """
        print("\n💾 Criando backup...")
        
        backup_dir = self.docs_dir.parent / f"docs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copytree(self.docs_dir, backup_dir)

    def restore_backup(self):
        """
        Restaura backup em caso de erro.
        """
        print("\n⚠️ Restaurando backup...")
        
        backups = sorted(self.docs_dir.parent.glob("docs_backup_*"))
        if backups:
            latest_backup = backups[-1]
            shutil.rmtree(self.docs_dir)
            shutil.copytree(latest_backup, self.docs_dir)
            print(f"✅ Backup restaurado: {latest_backup}")

    def update_structure(self):
        """
        Atualiza a estrutura de diretórios.
        """
        print("\n📁 Atualizando estrutura...")
        
        required_dirs = {
            "architecture": "Documentação de arquitetura",
            "runbooks": "Procedimentos operacionais",
            "api": "Documentação da API",
            "development": "Guias de desenvolvimento"
        }
        
        for dir_name, description in required_dirs.items():
            dir_path = self.docs_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            
            readme_path = dir_path / "README.md"
            if not readme_path.exists():
                self.create_readme(readme_path, dir_name, description)

    def update_indexes(self):
        """
        Atualiza os índices da documentação.
        """
        print("\n📑 Atualizando índices...")
        
        # Índice principal
        self.create_main_index()
        
        # Índices de subdiretórios
        for dir_path in self.docs_dir.iterdir():
            if dir_path.is_dir() and not dir_path.name.startswith("."):
                self.create_directory_index(dir_path)

    def update_references(self):
        """
        Atualiza referências entre documentos.
        """
        print("\n🔗 Atualizando referências...")
        
        # Mapear todos os arquivos
        files_map = {
            f.relative_to(self.docs_dir).as_posix(): f
            for f in self.docs_dir.rglob("*.md")
        }
        
        # Atualizar referências em cada arquivo
        for file_path in files_map.values():
            content = file_path.read_text(encoding="utf-8")
            updated_content = self.update_file_references(content, files_map)
            if content != updated_content:
                file_path.write_text(updated_content, encoding="utf-8")
                self.updated_files.add(str(file_path))

    def format_documents(self):
        """
        Formata os documentos Markdown.
        """
        print("\n✨ Formatando documentos...")
        
        for md_file in self.docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            formatted_content = self.format_markdown(content)
            if content != formatted_content:
                md_file.write_text(formatted_content, encoding="utf-8")
                self.updated_files.add(str(md_file))

    def validate_changes(self):
        """
        Valida as alterações feitas.
        """
        print("\n🔍 Validando alterações...")
        
        # Executar script de validação
        import validate_docs
        validator = validate_docs.DocumentationValidator()
        if not validator.validate_all():
            raise RuntimeError("Validação falhou após alterações")

    def create_readme(self, path: Path, dir_name: str, description: str):
        """
        Cria arquivo README.md para um diretório.
        """
        content = f"""# {dir_name.title()} 📚

## Visão Geral
{description}

## Documentos
<!-- Lista de documentos será gerada automaticamente -->

## Convenções
- Usar Markdown para todos os documentos
- Incluir exemplos práticos
- Manter referências atualizadas

## Manutenção
- Revisar mensalmente
- Atualizar exemplos
- Validar links

## Referências
- [Documentação Principal](../README.md)
"""
        path.write_text(content, encoding="utf-8")
        self.updated_files.add(str(path))

    def create_main_index(self):
        """
        Cria/atualiza o índice principal.
        """
        content = """# Documentação 📚

## Visão Geral
Documentação completa do projeto, incluindo arquitetura, procedimentos e guias.

## Seções

### Core
- [Arquitetura](architecture/README.md) - Design e decisões técnicas
- [API](api/README.md) - Documentação da API
- [Desenvolvimento](development/README.md) - Guias e padrões

### Operacional
- [Runbooks](runbooks/README.md) - Procedimentos operacionais
- [Troubleshooting](runbooks/troubleshooting-guide.md) - Resolução de problemas
- [DR](runbooks/disaster-recovery.md) - Recuperação de desastres

## Manutenção
Este repositório é mantido automaticamente por scripts que:
- Validam links e referências
- Atualizam índices
- Formatam documentos
- Geram backups

## Contribuição
1. Clone o repositório
2. Crie uma branch
3. Faça suas alterações
4. Execute `python scripts/validate_docs.py`
5. Submeta um PR
"""
        
        index_path = self.docs_dir / "README.md"
        index_path.write_text(content, encoding="utf-8")
        self.updated_files.add(str(index_path))

    def create_directory_index(self, dir_path: Path):
        """
        Cria/atualiza o índice de um diretório.
        """
        files = []
        for f in dir_path.rglob("*.md"):
            if f.name != "README.md":
                rel_path = f.relative_to(dir_path)
                title = self.get_document_title(f)
                files.append(f"- [{title}]({rel_path}) - {self.get_document_description(f)}")
        
        if files:
            readme_path = dir_path / "README.md"
            content = readme_path.read_text(encoding="utf-8")
            
            # Atualizar seção de documentos
            docs_section = "\n".join(["## Documentos", *sorted(files)])
            content = re.sub(
                r"## Documentos.*?(?=##|$)",
                docs_section + "\n\n",
                content,
                flags=re.DOTALL
            )
            
            readme_path.write_text(content, encoding="utf-8")
            self.updated_files.add(str(readme_path))

    def update_file_references(self, content: str, files_map: Dict[str, Path]) -> str:
        """
        Atualiza referências em um arquivo.
        """
        def replace_link(match):
            text, link = match.groups()
            if not link.startswith(("http", "#")):
                # Converter para path relativo
                link_path = Path(link)
                if str(link_path) in files_map:
                    return f"[{text}]({link_path.as_posix()})"
            return match.group(0)
        
        return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, content)

    def format_markdown(self, content: str) -> str:
        """
        Formata um documento Markdown.
        """
        # Garantir uma linha em branco após títulos
        content = re.sub(r"(^#.*)\n([^#\n])", r"\1\n\n\2", content, flags=re.MULTILINE)
        
        # Remover espaços em branco no final das linhas
        content = re.sub(r"[ \t]+$", "", content, flags=re.MULTILINE)
        
        # Garantir uma única linha em branco entre seções
        content = re.sub(r"\n{3,}", "\n\n", content)
        
        # Garantir newline no final do arquivo
        if not content.endswith("\n"):
            content += "\n"
        
        return content

    def get_document_title(self, file_path: Path) -> str:
        """
        Extrai o título de um documento Markdown.
        """
        content = file_path.read_text(encoding="utf-8")
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return match.group(1) if match else file_path.stem.replace("-", " ").title()

    def get_document_description(self, file_path: Path) -> str:
        """
        Extrai a descrição de um documento Markdown.
        """
        content = file_path.read_text(encoding="utf-8")
        
        # Tentar extrair do frontmatter
        frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if frontmatter_match:
            try:
                frontmatter = yaml.safe_load(frontmatter_match.group(1))
                if "description" in frontmatter:
                    return frontmatter["description"]
            except yaml.YAMLError:
                pass
        
        # Tentar extrair do primeiro parágrafo após o título
        match = re.search(r"^#.*?\n+([^#\n].*?)(?=\n\n|\n#|$)", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return "Sem descrição"

def main():
    updater = DocumentationUpdater()
    success = updater.update_all()
    
    if success and updater.updated_files:
        print("\n📝 Arquivos atualizados:")
        for file in sorted(updater.updated_files):
            print(f"  - {file}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 