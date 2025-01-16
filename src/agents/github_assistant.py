from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from .base_agent import BaseAgent
from ..utils.github_client import GitHubClient
from ..config.settings import get_settings
from ..utils.nlp_extractor import GitHubQueryExtractor
from ..utils.code_analyzer import CodeAnalyzer
from ..utils.repo_reporter import RepoReporter

class GitHubAssistant(BaseAgent):
    name: str = "GitHub Assistant"
    description: str = "Especialista em análise e gestão de repositórios GitHub"
    version: str = "1.0.0"
    keywords: List[str] = [
        "github", "git", "repo", "commit", "pull request", 
        "issue", "branch", "merge", "fork", "clone"
    ]
    github_client: Optional[GitHubClient] = None
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow"
    )
    
    def __init__(self):
        super().__init__()
        settings = get_settings()
        self.github_client = GitHubClient(settings.github_token)
    
    async def can_handle(self, query: str, context: Dict) -> float:
        """Calcula score de confiança para queries relacionadas ao GitHub"""
        query_lower = query.lower()
        keyword_matches = sum(1 for kw in self.keywords if kw in query_lower)
        return min(1.0, keyword_matches * 0.2)  # 0.2 por keyword, max 1.0
    
    async def process_query(self, query: str, context: Dict) -> Dict:
        """Processa queries relacionadas ao GitHub"""
        try:
            # Extrai URL do GitHub da query
            import re
            urls = re.findall(r'https?://github\.com/[^\s]+', query)
            if not urls:
                return {
                    "type": "error",
                    "content": "Nenhuma URL do GitHub encontrada na query"
                }
            
            repo_url = urls[0]
            response = await self._process_github_query(repo_url, query)
            
            return {
                "type": "ai",
                "content": f"[Using {repo_url}]\n\n{response}",
                "data": {
                    "source": "github_assistant",
                    "confidence": await self.can_handle(query, context)
                }
            }
        except Exception as e:
            return {
                "type": "error",
                "content": f"Erro ao processar query GitHub: {str(e)}",
                "data": {"error_type": type(e).__name__}
            }

    async def _process_github_query(self, repo_url: str, query: str) -> str:
        """Processa diferentes tipos de queries GitHub"""
        # Adiciona análise de código e relatórios
        if "analisar" in query.lower() or "análise" in query.lower():
            if "código" in query.lower() or "file" in query.lower():
                return await self._analyze_code(repo_url, query)
            else:
                return await self._generate_report(repo_url)
                
        entities = GitHubQueryExtractor.extract_entities(query)
        
        # Processa baseado nas entidades encontradas
        for entity in entities:
            if entity.type == "file_path":
                content = await self.github_client.get_file_content(repo_url, entity.value)
                return f"Conteúdo do arquivo {entity.value}:\n\n```\n{content}\n```"
                
            elif entity.type == "pr_number":
                pr_data = await self.github_client.get_pull_request(repo_url, int(entity.value))
                return f"Pull Request #{entity.value}:\n" + \
                       f"Título: {pr_data['title']}\n" + \
                       f"Estado: {pr_data['state']}\n" + \
                       f"Autor: {pr_data['user']}\n" + \
                       f"Arquivos alterados: {pr_data['changed_files']}\n\n" + \
                       f"Descrição:\n{pr_data['body']}"
                
            elif entity.type == "issue_number":
                issue_data = await self.github_client.get_issue(repo_url, int(entity.value))
                return f"Issue #{entity.value}:\n" + \
                       f"Título: {issue_data['title']}\n" + \
                       f"Estado: {issue_data['state']}\n" + \
                       f"Autor: {issue_data['user']}\n" + \
                       f"Comentários: {issue_data['comments']}\n\n" + \
                       f"Descrição:\n{issue_data['body']}"
                
            elif entity.type == "branch":
                branch_data = await self.github_client.get_branch_info(repo_url, entity.value)
                return f"Branch {entity.value}:\n" + \
                       f"Último commit: {branch_data['commit']['sha'][:7]}\n" + \
                       f"Protegida: {'Sim' if branch_data['protected'] else 'Não'}"

        # Default: retorna estrutura do repo
        structure = await self.github_client.get_repo_structure(repo_url)
        return "Estrutura do repositório:\n\n" + "\n".join(structure) 

    async def _analyze_code(self, repo_url: str, query: str) -> str:
        """Analisa código específico ou geral do repositório"""
        file_path = GitHubQueryExtractor.get_file_path(query)
        
        if file_path:
            content = await self.github_client.get_file_content(repo_url, file_path)
            metrics = await CodeAnalyzer.analyze_file(content, file_path)
            
            return (
                f"Análise do arquivo {file_path}:\n\n"
                f"📊 Métricas:\n"
                f"- Linhas totais: {metrics.lines_total}\n"
                f"- Linhas de código: {metrics.lines_code}\n"
                f"- Complexidade: {metrics.complexity:.2f}\n"
                f"- Funções: {metrics.functions}\n"
                f"- Classes: {metrics.classes}\n\n"
                f"🔍 Problemas de Segurança:\n" +
                "\n".join(f"- L{issue['line']}: {issue['description']}" 
                         for issue in metrics.security_issues)
            )
        
        return "Por favor, especifique um arquivo para análise."

    async def _generate_report(self, repo_url: str) -> str:
        """Gera relatório completo do repositório"""
        reporter = RepoReporter(self.github_client)
        report = await reporter.generate_report(repo_url)
        
        return (
            f"📊 Relatório do Repositório\n\n"
            f"Atividade (últimos 30 dias):\n"
            f"- Commits: {report.activity.commits}\n"
            f"- Pull Requests: {report.activity.pull_requests}\n"
            f"- Issues: {report.activity.issues}\n"
            f"- Contribuidores: {report.activity.contributors}\n"
            f"- Última atualização: {report.activity.last_updated}\n\n"
            f"Qualidade do Código:\n"
            f"- Arquivos analisados: {report.quality.files_analyzed}\n"
            f"- Total de linhas: {report.quality.total_lines}\n"
            f"- Complexidade média: {report.quality.avg_complexity:.2f}\n"
            f"- Problemas de segurança: {len(report.quality.security_issues)}\n"
            f"- Top dependências: {', '.join(report.quality.top_dependencies)}\n"
        ) 