from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class GitHubEntity(BaseModel):
    type: str
    value: str
    confidence: float = 0.0
    
    model_config = ConfigDict(
        extra="allow"
    )

class GitHubQueryExtractor:
    @staticmethod
    def extract_entities(query: str) -> List[GitHubEntity]:
        """Extrai entidades relevantes da query"""
        entities = []
        query_lower = query.lower()
        
        # Extrai file paths
        import re
        file_paths = re.findall(r'[\w\-./]+\.[a-zA-Z]+', query)
        for path in file_paths:
            if not path.startswith(('http://', 'https://')):
                entities.append(GitHubEntity(
                    type="file_path",
                    value=path,
                    confidence=0.8
                ))
        
        # Extrai PR numbers (melhorado)
        pr_patterns = [
            r'#(\d+)',                    # #123
            r'pr\s+(\d+)',               # PR 123
            r'pull request\s+(\d+)',     # pull request 123
            r'pull request #(\d+)'       # pull request #123
        ]
        
        for pattern in pr_patterns:
            matches = re.findall(pattern, query_lower)
            for number in matches:
                entities.append(GitHubEntity(
                    type="pr_number",
                    value=number,
                    confidence=0.9
                ))
        
        # Extrai branch names (melhorado)
        branch_patterns = [
            r'branch\s+[\'"]?([a-zA-Z0-9\-_/]+)[\'"]?',     # branch 'name'
            r'branch:\s*([a-zA-Z0-9\-_/]+)',                # branch: name
        ]
        
        for pattern in branch_patterns:
            matches = re.findall(pattern, query_lower)
            for branch in matches:
                entities.append(GitHubEntity(
                    type="branch",
                    value=branch,
                    confidence=0.8
                ))
        
        return entities

    @classmethod
    def get_file_path(cls, query: str) -> Optional[str]:
        """Extrai caminho do arquivo da query"""
        entities = cls.extract_entities(query)
        file_entities = [e for e in entities if e.type == "file_path"]
        return max(file_entities, key=lambda x: x.confidence).value if file_entities else None 