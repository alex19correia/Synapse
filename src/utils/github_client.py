from typing import Dict, Optional, List
from pydantic import BaseModel
import aiohttp
import asyncio
from ..utils.logger import get_logger
from ..utils.cache import RedisCache
from .resilience import resilience

logger = get_logger(__name__)

class GitHubRepo(BaseModel):
    org: str
    repo: str
    
    @classmethod
    def from_url(cls, url: str) -> "GitHubRepo":
        """Extrai org/repo de uma URL do GitHub"""
        import re
        pattern = r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$"
        if match := re.search(pattern, url):
            return cls(org=match.group(1), repo=match.group(2))
        raise ValueError(f"URL inválida do GitHub: {url}")

class GitHubClient:
    def __init__(self, token: str, cache_ttl: int = 3600):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.cache = RedisCache(namespace="github", ttl=cache_ttl)
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    @resilience.with_resilience("github_api")
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Faz requisição à API do GitHub com proteções"""
        cache_key = f"{method}:{endpoint}"
        
        # Tenta cache primeiro
        if method == "GET" and (cached := await self.cache.get(cache_key)):
            logger.debug(f"Cache hit for {cache_key}")
            return cached

        # Verifica rate limit
        if self.rate_limit_remaining == 0:
            wait_time = self.rate_limit_reset - asyncio.get_event_loop().time()
            if wait_time > 0:
                logger.warning(f"Rate limit atingido. Aguardando {wait_time}s")
                await asyncio.sleep(wait_time)

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=self.headers, **kwargs) as response:
                # Atualiza rate limit
                self.rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 60))
                self.rate_limit_reset = float(response.headers.get("X-RateLimit-Reset", 0))
                
                response.raise_for_status()
                data = await response.json()

                # Cache se for GET
                if method == "GET":
                    await self.cache.set(cache_key, data)
                
                return data

    async def get_repo_structure(self, repo_url: str) -> List[Dict]:
        """Obtém estrutura completa do repositório"""
        repo = GitHubRepo.from_url(repo_url)
        try:
            data = await self._make_request(
                "GET", 
                f"/repos/{repo.org}/{repo.repo}/git/trees/main",
                params={"recursive": "1"}
            )
            return self._format_repo_structure(data["tree"])
        except Exception as e:
            logger.error(f"Erro ao obter estrutura do repo: {e}")
            raise

    async def get_file_content(self, repo_url: str, file_path: str) -> str:
        """Obtém conteúdo de um arquivo específico"""
        repo = GitHubRepo.from_url(repo_url)
        try:
            data = await self._make_request(
                "GET",
                f"/repos/{repo.org}/{repo.repo}/contents/{file_path}"
            )
            import base64
            return base64.b64decode(data["content"]).decode()
        except Exception as e:
            logger.error(f"Erro ao obter conteúdo do arquivo: {e}")
            raise

    def _format_repo_structure(self, tree: List[Dict]) -> List[str]:
        """Formata estrutura do repositório de forma amigável"""
        excluded = ['.git/', 'node_modules/', '__pycache__/']
        structure = []
        
        for item in tree:
            if not any(ex in item["path"] for ex in excluded):
                prefix = "📁" if item["type"] == "tree" else "📄"
                structure.append(f"{prefix} {item['path']}")
                
        return structure 

    async def get_pull_request(self, repo_url: str, pr_number: int) -> Dict:
        """Obtém detalhes de um Pull Request específico"""
        repo = GitHubRepo.from_url(repo_url)
        try:
            data = await self._make_request(
                "GET",
                f"/repos/{repo.org}/{repo.repo}/pulls/{pr_number}"
            )
            return {
                "title": data["title"],
                "state": data["state"],
                "body": data["body"],
                "user": data["user"]["login"],
                "created_at": data["created_at"],
                "updated_at": data["updated_at"],
                "commits": data["commits"],
                "changed_files": data["changed_files"]
            }
        except Exception as e:
            logger.error(f"Erro ao obter PR #{pr_number}: {e}")
            raise

    async def get_issue(self, repo_url: str, issue_number: int) -> Dict:
        """Obtém detalhes de uma Issue específica"""
        repo = GitHubRepo.from_url(repo_url)
        try:
            data = await self._make_request(
                "GET",
                f"/repos/{repo.org}/{repo.repo}/issues/{issue_number}"
            )
            return {
                "title": data["title"],
                "state": data["state"],
                "body": data["body"],
                "user": data["user"]["login"],
                "created_at": data["created_at"],
                "updated_at": data["updated_at"],
                "comments": data["comments"]
            }
        except Exception as e:
            logger.error(f"Erro ao obter Issue #{issue_number}: {e}")
            raise

    async def get_branch_info(self, repo_url: str, branch: str) -> Dict:
        """Obtém informações sobre uma branch específica"""
        repo = GitHubRepo.from_url(repo_url)
        try:
            data = await self._make_request(
                "GET",
                f"/repos/{repo.org}/{repo.repo}/branches/{branch}"
            )
            return {
                "name": data["name"],
                "commit": {
                    "sha": data["commit"]["sha"],
                    "url": data["commit"]["url"]
                },
                "protected": data.get("protected", False)
            }
        except Exception as e:
            logger.error(f"Erro ao obter info da branch {branch}: {e}")
            raise 

    async def get_commit(self, repo_url: str, commit_sha: str) -> Dict:
        """Obtém detalhes de um commit específico"""
        repo = GitHubRepo.from_url(repo_url)
        try:
            data = await self._make_request(
                "GET",
                f"/repos/{repo.org}/{repo.repo}/commits/{commit_sha}"
            )
            return {
                "sha": data["sha"],
                "author": data["commit"]["author"]["name"],
                "message": data["commit"]["message"],
                "date": data["commit"]["author"]["date"],
                "stats": data["stats"],
                "files": [
                    {
                        "filename": f["filename"],
                        "status": f["status"],
                        "additions": f["additions"],
                        "deletions": f["deletions"]
                    }
                    for f in data["files"]
                ]
            }
        except Exception as e:
            logger.error(f"Erro ao obter commit {commit_sha}: {e}")
            raise

    async def get_releases(self, repo_url: str, limit: int = 5) -> List[Dict]:
        """Obtém releases mais recentes"""
        repo = GitHubRepo.from_url(repo_url)
        try:
            data = await self._make_request(
                "GET",
                f"/repos/{repo.org}/{repo.repo}/releases",
                params={"per_page": limit}
            )
            return [
                {
                    "tag": release["tag_name"],
                    "name": release["name"],
                    "body": release["body"],
                    "created_at": release["created_at"],
                    "draft": release["draft"],
                    "prerelease": release["prerelease"]
                }
                for release in data
            ]
        except Exception as e:
            logger.error(f"Erro ao obter releases: {e}")
            raise

    async def get_contributors(self, repo_url: str, limit: int = 10) -> List[Dict]:
        """Obtém principais contribuidores"""
        repo = GitHubRepo.from_url(repo_url)
        try:
            data = await self._make_request(
                "GET",
                f"/repos/{repo.org}/{repo.repo}/contributors",
                params={"per_page": limit}
            )
            return [
                {
                    "login": user["login"],
                    "contributions": user["contributions"],
                    "type": user["type"]
                }
                for user in data
            ]
        except Exception as e:
            logger.error(f"Erro ao obter contribuidores: {e}")
            raise 