#!/bin/bash

# FIAP Vehicles - Script de Setup Automático
# Executa toda a configuração necessária automaticamente

set -e  # Para em caso de erro

echo "🚀 FIAP Vehicles - Setup Automático"
echo "====================================="

# Verificar pré-requisitos
echo "📋 Verificando pré-requisitos..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale o Docker primeiro."
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl não encontrado. Por favor, instale o Kubernetes primeiro."
    exit 1
fi

echo "✅ Pré-requisitos atendidos"

# Configurar ambiente
echo "🔧 Configurando ambiente..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Arquivo .env criado"
else
    echo "✅ Arquivo .env já existe"
fi

# Build da aplicação
echo "🐳 Fazendo build da aplicação..."
docker compose build
echo "✅ Build concluído"

# Executar localmente
echo "🏃 Executando aplicação localmente..."
docker compose up -d
echo "✅ Aplicação rodando localmente"

# Aguardar aplicação subir
echo "⏳ Aguardando aplicação inicializar..."
sleep 15

# Testar aplicação local
echo "🧪 Testando aplicação local..."
if curl -sf http://localhost:8000/health > /dev/null; then
    echo "✅ Aplicação local funcionando"
else
    echo "❌ Erro na aplicação local"
    docker compose logs api
    exit 1
fi

# Importar imagem para k3s (se disponível)
if command -v k3s &> /dev/null; then
    echo "📦 Importando imagem para k3s..."
    docker save fiap_sub_2-api:latest | sudo k3s ctr images import -
    echo "✅ Imagem importada para k3s"
    
    # Deploy no Kubernetes
    echo "☸️ Fazendo deploy no Kubernetes..."
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/mysql-secret.yaml
    kubectl apply -f k8s/mysql-statefulset.yaml
    kubectl apply -f k8s/api.yaml
    kubectl apply -f k8s/api-nodeport.yaml
    kubectl apply -f k8s/ingress.yaml
    echo "✅ Deploy no Kubernetes concluído"
    
    # Aguardar pods subirem
    echo "⏳ Aguardando pods iniciarem..."
    kubectl wait --for=condition=ready pod -l app=api -n fiap-vehicles --timeout=300s
    
    # Obter IP do nó
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
    
    echo "🧪 Testando aplicação no Kubernetes..."
    if curl -sf http://$NODE_IP:30080/health > /dev/null; then
        echo "✅ Aplicação no Kubernetes funcionando"
    else
        echo "⚠️  Aplicação no Kubernetes pode não estar acessível externamente"
    fi
    
    echo ""
    echo "🎉 SETUP CONCLUÍDO COM SUCESSO!"
    echo "==============================="
    echo ""
    echo "📡 URLs de Acesso:"
    echo "   Local: http://localhost:8000"
    echo "   Kubernetes: http://$NODE_IP:30080"
    echo "   Documentação: /docs (em qualquer URL acima)"
    echo ""
    echo "🔍 Comandos úteis:"
    echo "   docker compose ps                    # Status local"
    echo "   kubectl get pods -n fiap-vehicles    # Status Kubernetes"
    echo "   curl http://localhost:8000/health    # Teste local"
    echo "   curl http://$NODE_IP:30080/health    # Teste Kubernetes"
    echo ""
else
    echo "⚠️  k3s não encontrado - pulando deploy Kubernetes"
    echo ""
    echo "🎉 SETUP LOCAL CONCLUÍDO!"
    echo "========================="
    echo ""
    echo "📡 URLs de Acesso:"
    echo "   Local: http://localhost:8000"
    echo "   Documentação: http://localhost:8000/docs"
    echo ""
fi

echo "📚 Para mais informações, consulte:"
echo "   README.md - Documentação completa"
echo "   ROTEIRO_IMPLEMENTACAO.md - Guia passo a passo"
echo "   EVIDENCIAS_ENTREGAVEIS.md - Comprovação dos critérios"
