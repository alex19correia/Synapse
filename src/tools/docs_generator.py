from typing import Dict, List
import ast
import inspect
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class DocsGenerator:
    """Gerador de documentação automática."""
    
    def __init__(self, src_path: Path, output_path: Path):
        self.src_path = src_path
        self.output_path = output_path
        self.env = Environment(loader=FileSystemLoader('templates'))
        
    async def generate_docs(self):
        """Gera documentação completa."""
        modules = self._scan_modules()
        
        for module in modules:
            docs = await self._generate_module_docs(module)
            await self._write_docs(module, docs)
            
        await self._generate_index(modules)
    
    async def _generate_module_docs(self, module_path: Path) -> Dict:
        """Gera documentação para um módulo."""
        with open(module_path, 'r') as f:
            module_content = f.read()
            
        module = ast.parse(module_content)
        
        return {
            "classes": self._extract_classes(module),
            "functions": self._extract_functions(module),
            "docstring": ast.get_docstring(module),
            "examples": self._extract_examples(module_content)
        }
    
    def _extract_classes(self, module: ast.Module) -> List[Dict]:
        """Extrai documentação das classes."""
        classes = []
        for node in ast.walk(module):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "methods": self._extract_methods(node)
                })
        return classes 