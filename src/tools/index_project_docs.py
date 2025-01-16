import os
from pathlib import Path
from src.services.rag_service import RAGService
from rich.console import Console
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter

console = Console()

def read_file(file_path: str) -> str:
    """Lê o conteúdo de um arquivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        console.print(f"[red]Erro ao ler arquivo {file_path}: {str(e)}[/red]")
        return ""

def split_large_text(text: str, max_tokens: int = 6000) -> List[str]:
    """Divide apenas textos grandes em chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_tokens,
        chunk_overlap=500,
        length_function=len,
        separators=["\n## ", "\n### ", "\n#### ", "\n", " ", ""]
    )
    return text_splitter.split_text(text)

def should_split_file(file_path: str, content: str) -> bool:
    """Determina se um arquivo deve ser dividido em chunks"""
    # Lista de arquivos que devem ser divididos
    large_files = ['instructions.md']
    return any(large_file in file_path for large_file in large_files)

def get_project_files() -> List[Dict]:
    """Coleta todos os arquivos relevantes do projeto"""
    docs = []
    base_path = Path.cwd()  # Diretório atual
    
    # Padrões de arquivos a serem indexados
    patterns = [
        ("docs", "**/*.md"),
        ("instructions", "*.md"),
        ("requirements", "*.txt")
    ]
    
    for section, pattern in patterns:
        section_path = base_path / section
        if section_path.exists():
            for file_path in section_path.rglob(pattern):
                if file_path.is_file():
                    content = read_file(str(file_path))
                    if not content:
                        continue
                        
                    relative_path = str(file_path.relative_to(base_path))
                    
                    # Decide se divide o arquivo em chunks
                    if should_split_file(relative_path, content):
                        chunks = split_large_text(content)
                        for i, chunk in enumerate(chunks):
                            docs.append({
                                "content": chunk,
                                "metadata": {
                                    "path": relative_path,
                                    "type": section,
                                    "section": file_path.parent.name,
                                    "filename": file_path.name,
                                    "chunk": i + 1,
                                    "total_chunks": len(chunks)
                                }
                            })
                    else:
                        # Mantém o arquivo como um único documento
                        docs.append({
                            "content": content,
                            "metadata": {
                                "path": relative_path,
                                "type": section,
                                "section": file_path.parent.name,
                                "filename": file_path.name
                            }
                        })
    
    return docs

def index_project_docs():
    rag = RAGService()
    docs = get_project_files()
    
    console.print(f"\n[bold blue]🔍 Encontrados {len(docs)} documentos/chunks para indexar[/bold blue]")
    
    for doc in docs:
        chunk_info = f" (chunk {doc['metadata']['chunk']}/{doc['metadata']['total_chunks']})" if 'chunk' in doc['metadata'] else ""
        console.print(f"\n[bold green]Indexando {doc['metadata']['path']}{chunk_info}...[/bold green]")
        success = rag.index_document(
            text=doc['content'],
            metadata=doc['metadata']
        )
        if success:
            console.print("✅ Documento indexado com sucesso!")
        else:
            console.print("❌ Erro ao indexar documento")

if __name__ == "__main__":
    console.print("[bold blue]🚀 Iniciando indexação dos documentos do projeto...[/bold blue]")
    index_project_docs() 