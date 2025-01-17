from typing import Dict, List, Optional
import ast
import re
from pydantic import BaseModel
from collections import defaultdict
from ..utils.logger import get_logger

logger = get_logger(__name__)

class CodeMetrics(BaseModel):
    """Métricas de análise de código"""
    lines_total: int = 0
    lines_code: int = 0
    lines_comment: int = 0
    complexity: float = 0.0
    functions: int = 0
    classes: int = 0
    imports: List[str] = []
    dependencies: List[str] = []
    security_issues: List[Dict] = []

class SecurityIssue(BaseModel):
    """Representa um problema de segurança encontrado"""
    type: str
    severity: str
    line: int
    description: str
    suggestion: str

class CodeAnalyzer:
    """Analisador de código com foco em métricas e segurança"""
    
    SECURITY_PATTERNS = {
        "hardcoded_secret": (
            r"(?i)(password|secret|token|key|api_key|apikey)\s*=\s*['\"'][^'\"]+['\"']",
            "alta",
            "Possível secret hardcoded encontrado"
        ),
        "sql_injection": (
            r"(?i)execute\([f'].*?\b(where|select|insert|update|delete)\b",
            "alta",
            "Possível SQL injection vulnerability"
        ),
        "debug_code": (
            r"(?i)print\(|console\.log\(|debugger|todo:",
            "baixa",
            "Código de debug encontrado"
        )
    }

    @classmethod
    async def analyze_file(cls, content: str, file_path: str) -> CodeMetrics:
        """Analisa conteúdo de um arquivo"""
        metrics = CodeMetrics()
        
        try:
            # Análise básica de linhas
            lines = content.splitlines()
            metrics.lines_total = len(lines)
            metrics.lines_comment = sum(1 for line in lines if line.strip().startswith('#'))
            metrics.lines_code = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))

            # Análise AST para Python
            if file_path.endswith('.py'):
                metrics = await cls._analyze_python(content, metrics)
            elif file_path.endswith('.js'):
                metrics = await cls._analyze_javascript(content, metrics)

            # Análise de segurança
            metrics.security_issues = await cls._check_security(content, lines)

            return metrics
        except Exception as e:
            logger.error(f"Erro ao analisar {file_path}: {e}")
            return metrics

    @classmethod
    async def _analyze_python(cls, content: str, metrics: CodeMetrics) -> CodeMetrics:
        """Análise específica para Python"""
        try:
            tree = ast.parse(content)
            
            # Contagem de funções e classes
            metrics.functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            metrics.classes = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            
            # Análise de imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(n.name for n in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)
            
            metrics.imports = imports
            metrics.dependencies = list(set(imp.split('.')[0] for imp in imports if imp))
            
            # Cálculo de complexidade
            metrics.complexity = cls._calculate_complexity(tree)
            
            return metrics
        except Exception as e:
            logger.error(f"Erro na análise Python: {e}")
            return metrics

    @classmethod
    async def _check_security(cls, content: str, lines: List[str]) -> List[Dict]:
        """Verifica problemas de segurança no código"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            for issue_type, (pattern, severity, description) in cls.SECURITY_PATTERNS.items():
                if re.search(pattern, line):
                    issues.append(SecurityIssue(
                        type=issue_type,
                        severity=severity,
                        line=line_num,
                        description=description,
                        suggestion=cls._get_security_suggestion(issue_type)
                    ).dict())
        
        return issues

    @staticmethod
    def _calculate_complexity(tree: ast.AST) -> float:
        """Calcula complexidade ciclomática"""
        complexity = 1  # Base complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Assert,
                               ast.Try, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    @staticmethod
    def _get_security_suggestion(issue_type: str) -> str:
        """Retorna sugestão para resolver problema de segurança"""
        suggestions = {
            "hardcoded_secret": "Use variáveis de ambiente ou gestão segura de secrets",
            "sql_injection": "Use prepared statements ou ORM",
            "debug_code": "Remova código de debug antes do deploy"
        }
        return suggestions.get(issue_type, "Revise o código com foco em segurança") 