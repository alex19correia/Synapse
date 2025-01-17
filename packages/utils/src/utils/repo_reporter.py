from typing import Dict, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from .github_client import GitHubClient
from .code_analyzer import CodeAnalyzer
from ..utils.logger import get_logger

logger = get_logger(__name__)

class RepoActivity(BaseModel):
    """Atividade do repositório"""
    commits: int = 0
    pull_requests: int = 0
    issues: int = 0
    contributors: int = 0
    last_updated: datetime | None = None

class CodeQuality(BaseModel):
    """Qualidade do código"""
    files_analyzed: int = 0
    total_lines: int = 0
    avg_complexity: float = 0.0
    security_issues: List[Dict] = []
    top_dependencies: List[str] = []

class RepoReport(BaseModel):
    """Relatório completo do repositório"""
    activity: RepoActivity
    quality: CodeQuality
    generated_at: datetime = datetime.now()

class RepoReporter:
    """Gerador de relatórios de repositório"""
    
    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client
        self.analyzer = CodeAnalyzer()

    async def generate_report(self, repo_url: str, days: int = 30) -> RepoReport:
        """Gera relatório completo do repositório"""
        try:
            # Inicializa relatório
            activity = await self._analyze_activity(repo_url, days)
            quality = await self._analyze_quality(repo_url)
            
            return RepoReport(
                activity=activity,
                quality=quality
            )
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            raise

    async def _analyze_activity(self, repo_url: str, days: int) -> RepoActivity:
        """Analisa atividade recente do repositório"""
        since = datetime.now() - timedelta(days=days)
        
        # Obtém dados de atividade
        commits = await self.github_client.get_commits(repo_url, since=since)
        prs = await self.github_client.get_pull_requests(repo_url, state="all", since=since)
        issues = await self.github_client.get_issues(repo_url, state="all", since=since)
        contributors = await self.github_client.get_contributors(repo_url)
        
        return RepoActivity(
            commits=len(commits),
            pull_requests=len(prs),
            issues=len(issues),
            contributors=len(contributors),
            last_updated=max(c["date"] for c in commits) if commits else None
        )

    async def _analyze_quality(self, repo_url: str) -> CodeQuality:
        """Analisa qualidade do código"""
        structure = await self.github_client.get_repo_structure(repo_url)
        
        # Analisa apenas arquivos relevantes
        code_files = [f for f in structure if f.endswith(('.py', '.js', '.ts', '.jsx', '.tsx'))]
        
        metrics_total = CodeQuality()
        all_dependencies = []
        
        for file_path in code_files:
            content = await self.github_client.get_file_content(repo_url, file_path)
            metrics = await CodeAnalyzer.analyze_file(content, file_path)
            
            metrics_total.files_analyzed += 1
            metrics_total.total_lines += metrics.lines_total
            metrics_total.avg_complexity += metrics.complexity
            metrics_total.security_issues.extend(metrics.security_issues)
            all_dependencies.extend(metrics.dependencies)
        
        if metrics_total.files_analyzed > 0:
            metrics_total.avg_complexity /= metrics_total.files_analyzed
        
        # Top dependências
        from collections import Counter
        deps_count = Counter(all_dependencies)
        metrics_total.top_dependencies = [dep for dep, _ in deps_count.most_common(10)]
        
        return metrics_total 