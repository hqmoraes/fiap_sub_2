# FIAP Vehicles – API de Revenda de Veículos

API REST para plataforma de revenda de veículos automotores desenvolvida com FastAPI, seguindo princípios de Clean Architecture e SOLID.

## 🚀 Funcionalidades

- **CRUD de Veículos**: Cadastro, edição e consulta de veículos
- **Sistema de Vendas**: Processamento e registro de vendas de veículos
- **Webhook de Pagamentos**: Endpoint para receber notificações de status de pagamento
- **Listagens Ordenadas**: Veículos disponíveis e vendidos ordenados por preço
- **Documentação OpenAPI**: Interface Swagger automática em `/docs`
- **Health Check**: Endpoint de verificação de saúde em `/health`

## 🛠️ Stack Tecnológica

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.x, PyMySQL
- **Banco de Dados**: MySQL 8.x
- **Containerização**: Docker, Docker Compose
- **Orquestração**: Kubernetes (k3s)
- **Arquitetura**: Clean Architecture + SOLID

## 📋 Pré-requisitos

### Para execução local:
- Python 3.12+
- Docker e Docker Compose
- Git

### Para deploy Kubernetes:
- Cluster Kubernetes (testado com k3s)
- kubectl configurado

## 🏃‍♂️ Execução Local

### 1. Clone e Configure
```bash
git clone <repository-url>
cd FIAP_Sub_2
cp .env.example .env
```

### 2. Docker Compose (Recomendado)
```bash
# Build e execução
docker compose up --build

# Execução em background
docker compose up -d
```

### 3. Ambiente Python Local (Alternativo)
```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar banco (MySQL deve estar rodando)
export DB_HOST=localhost
python -m app.init_db

# Executar aplicação
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Acesso
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## ☸️ Deploy Kubernetes

### 1. Preparar Imagem
```bash
# Build da imagem
docker compose build

# Para k3s: importar imagem local
docker save fiap_sub_2-api:latest | sudo k3s ctr images import -
```

### 2. Aplicar Manifests
```bash
# Aplicar na ordem
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mysql-secret.yaml
kubectl apply -f k8s/mysql-statefulset.yaml
kubectl apply -f k8s/api.yaml

# Para acesso externo (escolha uma opção):
kubectl apply -f k8s/api-nodeport.yaml  # Acesso via porta 30080
kubectl apply -f k8s/ingress.yaml       # Acesso via porta 80
```

### 3. Verificar Deploy
```bash
# Status dos recursos
kubectl get all -n fiap-vehicles

# Logs da aplicação
kubectl logs deployment/api -n fiap-vehicles

# Teste funcional
kubectl run test-pod --image=curlimages/curl --rm -it --restart=Never -n fiap-vehicles -- curl http://api/health
```

### 4. Acesso Externo
Após aplicar os manifests de exposição, a aplicação estará disponível em:

- **Via NodePort**: http://192.168.1.112:30080
- **Via Ingress**: http://192.168.1.112 (porta 80)
- **Documentação**: http://192.168.1.112/docs ou http://192.168.1.112:30080/docs
- **Health Check**: http://192.168.1.112/health ou http://192.168.1.112:30080/health

## 🧪 Testes

### Testes Funcionais da API
```bash
# Health Check
curl http://localhost:8000/health

# Documentação Swagger
curl http://localhost:8000/docs

# Listar veículos disponíveis
curl http://localhost:8000/vehicles?status=AVAILABLE

# Criar veículo (exemplo)
curl -X POST http://localhost:8000/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2023,
    "color": "Branco",
    "price": 85000.00
  }'
```

### Testes Unitários
```bash
# Executar com pytest
source venv/bin/activate
pytest

# Com coverage
pytest --cov=app
```

## 📚 Documentação da API

A documentação completa da API está disponível via Swagger UI:
- **Local**: http://localhost:8000/docs
- **Kubernetes**: http://localhost:8080/docs (via port-forward)

### Principais Endpoints:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check |
| GET | `/vehicles` | Listar veículos (com filtros) |
| POST | `/vehicles` | Cadastrar veículo |
| PUT | `/vehicles/{id}` | Editar veículo |
| POST | `/vehicles/{id}/sell` | Vender veículo |
| POST | `/payments/webhook` | Webhook de pagamento |

## 🏗️ Arquitetura

```
app/
├── config.py              # Configurações
├── main.py                # Aplicação FastAPI
├── init_db.py             # Inicialização do BD
├── domain/                # Camada de Domínio
│   ├── models.py          # Entidades SQLAlchemy
│   └── schemas.py         # Schemas Pydantic
├── infrastructure/        # Camada de Infraestrutura
│   └── db.py             # Configuração do banco
└── routers/              # Camada de Interface
    ├── vehicles.py       # Endpoints de veículos
    └── payments.py       # Endpoints de pagamentos
```

### Princípios Aplicados:
- **Clean Architecture**: Separação clara de responsabilidades
- **SOLID**: Princípios de orientação a objetos
- **DDD**: Modelagem orientada ao domínio
- **Dependency Injection**: Inversão de dependências

## 🔧 Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `APP_NAME` | Nome da aplicação | `fiap-vehicles` |
| `APP_ENV` | Ambiente | `local` |
| `LOG_LEVEL` | Nível de log | `INFO` |
| `API_PORT` | Porta da API | `8000` |
| `DB_HOST` | Host do MySQL | `localhost` |
| `DB_PORT` | Porta do MySQL | `3306` |
| `DB_NAME` | Nome do banco | `fiap_vehicles` |
| `DB_USER` | Usuário do banco | `fiap` |
| `DB_PASSWORD` | Senha do banco | `fiap` |

### Configuração Kubernetes

**Secrets necessários** (em produção, usar valores seguros):
- `DB_USER`: Usuário do MySQL
- `DB_PASSWORD`: Senha do MySQL  
- `WEBHOOK_SECRET`: Segredo do webhook

## 🐳 Containers

### Dockerfile
- Imagem base: `python:3.12-slim`
- Multi-stage build para otimização
- Dependências de sistema para MySQL
- Usuário não-root para segurança

### Docker Compose
- **Serviços**: API + MySQL
- **Volumes**: Persistência de dados
- **Health checks**: Verificação de saúde
- **Redes**: Isolamento de containers

## 📦 Manifests Kubernetes

| Arquivo | Descrição |
|---------|-----------|
| `namespace.yaml` | Namespace `fiap-vehicles` |
| `mysql-secret.yaml` | Secrets do MySQL |
| `mysql-statefulset.yaml` | StatefulSet + Service MySQL |
| `api.yaml` | ConfigMap, Secret, Deployment e Service da API |

### Recursos Configurados:
- **Replicas**: 2 para alta disponibilidade
- **Probes**: Liveness e readiness
- **Resources**: Requests e limits definidos
- **Storage**: PVC para persistência MySQL

## 🔒 Segurança

- **Secrets**: Variáveis sensíveis em Kubernetes Secrets
- **CORS**: Configurado para domínios permitidos
- **Validação**: Sanitização de inputs via Pydantic
- **Logging**: Logs estruturados (sem exposição de dados sensíveis)
- **Container**: Usuário não-root

## 🔄 CI/CD

Preparado para GitHub Actions com:
- Build e push para Docker Hub
- Deploy automático no Kubernetes
- Testes automatizados

**Secrets necessários no GitHub**:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `KUBE_CONFIG`

## 📋 Checklist de Produção

- [ ] Configurar DNS e Ingress
- [ ] Implementar monitoramento (Prometheus/Grafana)
- [ ] Configurar backups automatizados
- [ ] Implementar rate limiting
- [ ] Configurar SSL/TLS
- [ ] Implementar cache (Redis)
- [ ] Configurar alertas
- [ ] Documentar procedimentos operacionais

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

Para dúvidas ou suporte:
- Documentação: http://localhost:8000/docs
- Issues: GitHub Issues
- Email: [seu-email@exemplo.com]

---

**FIAP Tech Challenge - Fase 2**  
*Plataforma de Revenda de Veículos - API REST*
