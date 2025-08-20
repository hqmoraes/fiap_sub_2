# 🚀 ROTEIRO DE IMPLEMENTAÇÃO - FIAP Vehicles API

## Guia Passo a Passo para Avaliadores

Este documento fornece instruções detalhadas para implementar e executar a solução completa da API de Revenda de Veículos.

---

## 📋 **PRÉ-REQUISITOS**

### Ambiente de Desenvolvimento
- **SO**: Linux (Ubuntu 20.04+ recomendado) ou macOS
- **Git**: Para clonar o repositório
- **Docker**: Para containerização
- **Kubernetes**: Para orquestração (k3s recomendado)

### Instalação dos Pré-requisitos (Ubuntu/Debian)

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Git
sudo apt install -y git

# Instalar Docker
sudo apt install -y docker.io docker-compose-v2
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Instalar k3s (Kubernetes)
curl -sfL https://get.k3s.io | sh -
sudo chmod 644 /etc/rancher/k3s/k3s.yaml

# Instalar Python e pip
sudo apt install -y python3 python3-pip python3-venv

# Reiniciar sessão para aplicar grupo docker
newgrp docker
```

---

## 🗂️ **1. CLONAGEM E CONFIGURAÇÃO INICIAL**

```bash
# Clonar repositório
git clone <URL_DO_REPOSITORIO>
cd FIAP_Sub_2

# Verificar estrutura do projeto
ls -la

# Criar arquivo de ambiente
cp .env.example .env

# Verificar conteúdo do .env (opcional: ajustar configurações)
cat .env
```

**Estrutura esperada:**
```
FIAP_Sub_2/
├── app/                    # Código da aplicação
├── k8s/                    # Manifests Kubernetes
├── docker-compose.yml      # Configuração Docker Compose
├── Dockerfile             # Imagem da aplicação
├── requirements.txt       # Dependências Python
├── .env.example           # Template de configuração
└── README.md              # Documentação
```

---

## 🐳 **2. EXECUÇÃO LOCAL COM DOCKER COMPOSE**

### Teste Rápido (Recomendado para Avaliação)

```bash
# Build e execução em um comando
docker compose up --build

# OU em background
docker compose up --build -d
```

### Verificação do Funcionamento

```bash
# Verificar containers rodando
docker compose ps

# Testar health check
curl http://localhost:8000/health
# Resposta esperada: {"status":"ok"}

# Acessar documentação Swagger
curl http://localhost:8000/docs
# OU abrir no navegador: http://localhost:8000/docs

# Verificar logs (se necessário)
docker compose logs api
docker compose logs db
```

### Testes Funcionais da API

```bash
# 1. Health Check
curl http://localhost:8000/health

# 2. Listar veículos (inicialmente vazio)
curl http://localhost:8000/vehicles

# 3. Criar um veículo
curl -X POST http://localhost:8000/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2023,
    "color": "Branco", 
    "price": 85000.00
  }'

# 4. Listar veículos novamente
curl http://localhost:8000/vehicles?status=AVAILABLE

# 5. Webhook de pagamento (exemplo)
curl -X POST http://localhost:8000/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "paymentCode": "PAY123",
    "status": "PAID"
  }'
```

---

## ☸️ **3. DEPLOY NO KUBERNETES**

### Preparação do Ambiente Kubernetes

```bash
# Verificar se k3s está funcionando
kubectl cluster-info
kubectl get nodes

# Verificar se Docker está acessível
docker ps
```

### Build e Importação da Imagem

```bash
# Build da imagem Docker
docker compose build

# Para k3s: importar imagem local
docker save fiap_sub_2-api:latest | sudo k3s ctr images import -

# Verificar imagem importada
sudo k3s ctr images list | grep fiap
```

### Deploy da Aplicação

```bash
# Aplicar manifests na ordem correta
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mysql-secret.yaml  
kubectl apply -f k8s/mysql-statefulset.yaml
kubectl apply -f k8s/api.yaml

# Para acesso externo (escolha UMA das opções):
kubectl apply -f k8s/api-nodeport.yaml  # Porta 30080
# OU
kubectl apply -f k8s/ingress.yaml       # Porta 80
```

### Verificação do Deploy

```bash
# Verificar todos os recursos
kubectl get all -n fiap-vehicles

# Verificar pods específicos
kubectl get pods -n fiap-vehicles

# Verificar logs da aplicação
kubectl logs deployment/api -n fiap-vehicles

# Verificar serviços
kubectl get services,ingress -n fiap-vehicles
```

### Teste Funcional no Kubernetes

```bash
# Teste interno (dentro do cluster)
kubectl run test-pod --image=curlimages/curl --rm -it --restart=Never -n fiap-vehicles -- curl http://api/health

# Teste externo (substituir IP pelo seu)
curl http://192.168.1.112/health           # Via Ingress
curl http://192.168.1.112:30080/health     # Via NodePort
```

---

## 🧪 **4. VALIDAÇÃO COMPLETA DOS ENTREGÁVEIS**

### Checklist de Verificação

- [ ] **Repositório GitHub**: Código fonte completo
- [ ] **README.md**: Documentação detalhada
- [ ] **Docker Compose**: `docker compose up` funciona
- [ ] **Kubernetes**: Deploy com 2+ réplicas
- [ ] **API Funcionando**: Endpoints respondem
- [ ] **Swagger**: Documentação acessível
- [ ] **Clean Architecture**: Estrutura de pastas organizada
- [ ] **Banco de Dados**: MySQL persistente

### Testes de Aceitação

```bash
# 1. Teste de Health Check
curl http://localhost:8000/health
# Esperado: {"status":"ok"}

# 2. Teste de Documentação
curl -I http://localhost:8000/docs
# Esperado: HTTP/1.1 200 OK

# 3. Teste de CRUD de Veículos
# (Ver seção de testes funcionais acima)

# 4. Teste de Kubernetes
kubectl get pods -n fiap-vehicles
# Esperado: 2+ pods da API em Running, 1 pod MySQL em Running

# 5. Teste de Acesso Externo
curl http://<SEU_IP>/health
# Esperado: {"status":"ok"}
```

---

## 🔧 **5. TROUBLESHOOTING**

### Problemas Comuns e Soluções

#### Docker não funciona sem sudo
```bash
sudo usermod -aG docker $USER
newgrp docker
```

#### Pods em CrashLoopBackOff
```bash
kubectl logs deployment/api -n fiap-vehicles
kubectl describe pod <pod-name> -n fiap-vehicles
```

#### Erro de conexão com MySQL
```bash
# Verificar se MySQL está rodando
kubectl get pods -n fiap-vehicles
kubectl logs statefulset/mysql -n fiap-vehicles
```

#### Acesso externo não funciona
```bash
# Verificar serviços
kubectl get services,ingress -n fiap-vehicles

# Verificar IP do nó
kubectl get nodes -o wide
```

#### Imagem não encontrada no Kubernetes
```bash
# Re-importar imagem
docker save fiap_sub_2-api:latest | sudo k3s ctr images import -

# Verificar imagem
sudo k3s ctr images list | grep fiap
```

---

## 📊 **6. EVIDÊNCIAS DOS ENTREGÁVEIS**

### Capturas de Tela Recomendadas

1. **Swagger UI**: http://localhost:8000/docs
2. **Pods Kubernetes**: `kubectl get pods -n fiap-vehicles`
3. **Teste de API**: Resposta do health check
4. **Estrutura do Código**: Árvore de diretórios
5. **Docker Compose**: `docker compose ps`

### Logs de Evidência

```bash
# Salvar evidências em arquivos
kubectl get all -n fiap-vehicles > evidencias-kubernetes.txt
docker compose ps > evidencias-docker.txt
curl http://localhost:8000/health > evidencias-api.txt
tree app/ > evidencias-arquitetura.txt
```

---

## ⏱️ **7. TEMPO ESTIMADO DE EXECUÇÃO**

| Etapa | Tempo Estimado | Descrição |
|-------|----------------|-----------|
| Pré-requisitos | 10-15 min | Instalação de ferramentas |
| Clone e Setup | 2-3 min | Download do código |
| Docker Compose | 5-10 min | Build e execução local |
| Kubernetes Deploy | 5-10 min | Deploy no cluster |
| Testes e Validação | 5-10 min | Verificação final |
| **TOTAL** | **27-48 min** | Implementação completa |

---

## 📞 **8. SUPORTE**

### Informações de Contato
- **Documentação**: README.md do projeto
- **Issues**: GitHub Issues do repositório
- **API Reference**: http://localhost:8000/docs

### Versões Testadas
- **Ubuntu**: 20.04+ / 24.04
- **Docker**: 20.10+
- **Kubernetes**: k3s v1.28+
- **Python**: 3.12+

---

**🎯 Seguindo este roteiro, a solução completa deve estar funcionando em menos de 1 hora!**
