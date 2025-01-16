# Guia de Contribuição

## Como Contribuir

### 1. Preparação do Ambiente

1. Fork o repositório
2. Clone o seu fork
3. Configure o ambiente de desenvolvimento

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
pip install -r requirements/dev.txt
```

### 2. Desenvolvimento

1. Crie uma branch para sua feature/correção
```bash
git checkout -b feature/nome-da-feature
```

2. Siga as convenções de código:
- Use type hints
- Documente funções e classes
- Siga PEP 8
- Adicione testes

3. Execute os testes localmente
```bash
pytest
```

### 3. Commit

Siga a convenção para mensagens de commit:

- feat: nova funcionalidade
- fix: correção de bug
- docs: documentação
- style: formatação
- refactor: refatoração
- test: testes
- chore: manutenção

### 4. Pull Request

1. Push para seu fork
2. Crie um Pull Request
3. Descreva as mudanças
4. Aguarde review

## Estrutura do Projeto

```
synapse/
├── docs/
├── llm_docs/
├── src/
│   ├── api/
│   ├── config/
│   ├── models/
│   ├── services/
│   └── utils/
└── tests/
```

## Convenções de Código

### Python
- Use type hints
- Docstrings no estilo Google
- Nomes em inglês
- Testes para novas funcionalidades

### Git
- Branches: feature/, fix/, docs/
- Commits descritivos
- Rebase antes do PR

## Testes

- Testes unitários em `tests/unit/`
- Testes de integração em `tests/integration/`
- Mínimo de 80% de cobertura
