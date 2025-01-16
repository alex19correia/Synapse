from src.services.rag_service import RAGService
from rich.console import Console
from typing import List, Dict

console = Console()

# Documentos de exemplo sobre o Synapse
documents = [
    {
        "content": """
        O Synapse utiliza um sistema de memória avançado que inclui:
        1. Memória de curto prazo para o contexto imediato da conversa
        2. Memória de longo prazo para informações importantes sobre o usuário
        3. Memória episódica para experiências e interações passadas
        """,
        "metadata": {
            "type": "documentation",
            "section": "memory",
            "topic": "architecture"
        }
    },
    {
        "content": """
        Principais comandos do Synapse:
        - /help: Mostra todos os comandos disponíveis
        - /context: Mostra o contexto atual da conversa
        - /clear: Limpa o histórico da conversa atual
        - /save: Salva uma informação importante
        """,
        "metadata": {
            "type": "documentation",
            "section": "commands",
            "topic": "usage"
        }
    },
    {
        "content": """
        O Synapse prioriza a privacidade do usuário:
        - Dados são criptografados
        - Informações sensíveis não são compartilhadas
        - Usuário tem controle total sobre seus dados
        - Opção de deletar histórico a qualquer momento
        """,
        "metadata": {
            "type": "documentation",
            "section": "privacy",
            "topic": "security"
        }
    }
]

def index_documents():
    rag = RAGService()
    
    for doc in documents:
        console.print(f"\n[bold blue]Indexando documento sobre {doc['metadata']['section']}...[/bold blue]")
        success = rag.index_document(
            text=doc['content'],
            metadata=doc['metadata']
        )
        if success:
            console.print(f"✅ Documento indexado com sucesso!")
        else:
            console.print(f"❌ Erro ao indexar documento")

if __name__ == "__main__":
    console.print("[bold green]🔍 Indexando documentos no Synapse...[/bold green]")
    index_documents() 