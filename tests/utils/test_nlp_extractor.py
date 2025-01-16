import pytest
from src.utils.nlp_extractor import GitHubQueryExtractor, GitHubEntity

def test_extract_file_path():
    """Testa extração de caminhos de arquivo"""
    queries = [
        ("Mostre o arquivo main.py", "main.py"),
        ("Abra o conteúdo de src/utils/helper.js", "src/utils/helper.js"),
        ("Leia o arquivo 'config.json'", "config.json"),
        ("O que tem no arquivo test/unit/test_app.py?", "test/unit/test_app.py"),
    ]
    
    for query, expected in queries:
        entities = GitHubQueryExtractor.extract_entities(query)
        file_entities = [e for e in entities if e.type == "file_path"]
        assert len(file_entities) > 0
        assert file_entities[0].value == expected

def test_extract_pr_number():
    """Testa extração de números de PR"""
    queries = [
        ("Mostre o PR #123", "123"),
        ("Qual o status do pull request 456?", "456"),
        ("Abra a pull request #789", "789"),
    ]
    
    for query, expected in queries:
        entities = GitHubQueryExtractor.extract_entities(query)
        pr_entities = [e for e in entities if e.type == "pr_number"]
        assert len(pr_entities) > 0
        assert pr_entities[0].value == expected

def test_extract_branch():
    """Testa extração de nomes de branch"""
    queries = [
        ("Mostre a branch main", "main"),
        ("O que tem na branch feature/login?", "feature/login"),
        ("Status do branch 'develop'", "develop"),
    ]
    
    for query, expected in queries:
        entities = GitHubQueryExtractor.extract_entities(query)
        branch_entities = [e for e in entities if e.type == "branch"]
        assert len(branch_entities) > 0
        assert branch_entities[0].value == expected

def test_multiple_entities():
    """Testa extração de múltiplas entidades"""
    query = "No PR #123 da branch feature/login, mostre o arquivo src/main.py"
    entities = GitHubQueryExtractor.extract_entities(query)
    
    # Verifica tipos únicos de entidades
    entity_types = {entity.type for entity in entities}
    assert entity_types == {"pr_number", "branch", "file_path"}
    
    # Verifica valores específicos
    values = {(entity.type, entity.value) for entity in entities}
    assert ("pr_number", "123") in values
    assert ("branch", "feature/login") in values
    assert ("file_path", "src/main.py") in values 