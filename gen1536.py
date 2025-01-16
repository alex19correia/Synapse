import random

# Gerar 1536 valores entre 0 e 1
values = [round(random.random(), 4) for _ in range(1536)]

# Formatar para SQL
sql_values = ', '.join(map(str, values))
sql_query = f"""
INSERT INTO document_embeddings (content, embedding, metadata)
VALUES (
  'Exemplo de conteúdo',
  ARRAY[{sql_values}]::vector(1536),
  '{{"source": "manual", "type": "example"}}'
);
"""

print(sql_query)