from pathlib import Path
from typing import Set

# Configurações de ignorar
IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".next", "build", "dist",
    "cypress", ".github", ".vscode", "coverage", "migrations"
}

IGNORE_FILES = {
    ".env", ".DS_Store", "*.pyc", "*.log", "*.lock", 
    "package-lock.json", "yarn.lock"
}

# Emojis por tipo
DIR_EMOJIS = {
    "config": "⚙️",
    "docs": "📚",
    "src": "🔧",
    "tests": "🧪",
    "api": "🌐",
    "components": "🧩",
    "hooks": "🎣",
    "utils": "🛠️",
    "services": "🔌",
    "core": "⚛️"
}

FILE_EMOJIS = {
    ".py": "🐍",
    ".ts": "📘",
    ".tsx": "⚛️",
    ".md": "📝",
    ".json": "📋",
    ".yml": "⚙️",
    ".yaml": "⚙️"
}

def get_emoji(path: Path) -> str:
    """Retorna o emoji apropriado para o caminho."""
    if path.is_file():
        return FILE_EMOJIS.get(path.suffix.lower(), "📄")
    return DIR_EMOJIS.get(path.name.lower(), "📁")

def generate_tree(
    start_path: str = ".",
    ignore_dirs: Set[str] = IGNORE_DIRS,
    ignore_files: Set[str] = IGNORE_FILES,
    indent: str = "│   "
) -> str:
    """Gera a árvore de diretórios."""
    output = []
    start_path = Path(start_path)

    def should_ignore(path: Path) -> bool:
        """Verifica se deve ignorar o caminho."""
        from fnmatch import fnmatch
        return (
            path.name.startswith(".") or
            (path.is_dir() and path.name in ignore_dirs) or
            (path.is_file() and any(fnmatch(path.name, p) for p in ignore_files))
        )

    def add_directory(directory: Path, prefix: str = "") -> None:
        """Adiciona um diretório à árvore."""
        if should_ignore(directory):
            return

        if directory != start_path:
            emoji = get_emoji(directory)
            output.append(f"{prefix}├── {emoji} {directory.name}/")

        # Lista e ordena diretórios e arquivos
        items = sorted(directory.iterdir())
        dirs = [x for x in items if x.is_dir() and not should_ignore(x)]
        files = [x for x in items if x.is_file() and not should_ignore(x)]

        # Processa diretórios
        for i, d in enumerate(dirs):
            is_last_dir = (i == len(dirs) - 1) and not files
            new_prefix = prefix + ("    " if is_last_dir else "│   ")
            add_directory(d, new_prefix)

        # Processa arquivos
        for i, f in enumerate(files):
            is_last = i == len(files) - 1
            marker = "└── " if is_last else "├── "
            emoji = get_emoji(f)
            output.append(f"{prefix}{marker}{emoji} {f.name}")

    # Inicia a geração
    output.append(f"🚀 {start_path.name}/")
    add_directory(start_path)
    return "\n".join(output)

if __name__ == "__main__":
    try:
        tree = generate_tree()
        print(tree)
        
        with open("project_structure.txt", "w", encoding="utf-8") as f:
            f.write(tree)
    except Exception as e:
        print(f"Erro ao gerar árvore: {e}") 