#!/bin/bash

# Verifica se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
  echo "❌ Docker não está rodando"
  exit 1
fi

# Verifica status dos containers
services=("qdrant" "redis")
for service in "${services[@]}"; do
  status=$(docker inspect -f '{{.State.Status}}' $service 2>/dev/null)
  
  if [ "$status" != "running" ]; then
    echo "❌ Serviço $service não está rodando"
    exit 1
  fi
done

echo "✅ Todos os serviços estão rodando corretamente" 