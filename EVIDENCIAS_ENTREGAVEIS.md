# 📋 EVIDÊNCIAS DOS ENTREGÁVEIS - FIAP Tech Challenge Fase 2

## Comprovação de Atendimento aos Critérios de Avaliação

---

## 🎯 **CRITÉRIOS FUNCIONAIS ATENDIDOS**

### ✅ **1. Cadastrar um veículo para venda**
- **Implementado**: `POST /vehicles`
- **Localização**: `app/routers/vehicles.py`
- **Validações**: Marca, modelo, ano, cor, preço obrigatórios
- **Teste**: 
  ```bash
  curl -X POST http://localhost:8000/vehicles \
    -H "Content-Type: application/json" \
    -d '{"brand":"Toyota","model":"Corolla","year":2023,"color":"Branco","price":85000.00}'
  ```

### ✅ **2. Editar os dados do veículo**
- **Implementado**: `PUT /vehicles/{id}`
- **Localização**: `app/routers/vehicles.py`
- **Regra**: Só permite edição se status = AVAILABLE
- **Validações**: Campos opcionais com validação de tipos

### ✅ **3. Efetuar a venda de um veículo**
- **Implementado**: `POST /vehicles/{id}/sell`
- **Localização**: `app/routers/vehicles.py`
- **Funcionalidades**:
  - CPF do comprador
  - Data da venda
  - Preço de venda
  - Mudança de status para SOLD
  - Código de pagamento opcional

### ✅ **4. Listagem de veículos à venda (ordenada por preço)**
- **Implementado**: `GET /vehicles?status=AVAILABLE&sort=price,asc`
- **Localização**: `app/routers/vehicles.py`
- **Funcionalidades**:
  - Filtro por status
  - Ordenação por preço ascendente
  - Paginação com page/size

### ✅ **5. Listagem de veículos vendidos (ordenada por preço)**
- **Implementado**: `GET /vehicles?status=SOLD&sort=price,asc`
- **Localização**: `app/routers/vehicles.py`
- **Funcionalidades**:
  - Filtro por status SOLD
  - Ordenação por preço ascendente
  - Paginação implementada

### ✅ **6. Webhook de pagamento**
- **Implementado**: `POST /payments/webhook`
- **Localização**: `app/routers/payments.py`
- **Funcionalidades**:
  - Recebe código de pagamento
  - Atualiza status (PAID/CANCELED)
  - Idempotência implementada
  - Validação de paymentCode

---

## 🛠️ **CRITÉRIOS TÉCNICOS ATENDIDOS**

### ✅ **Documentação OpenAPI/Swagger**
- **URL Local**: http://localhost:8000/docs
- **URL Kubernetes**: http://192.168.1.112/docs
- **Implementação**: FastAPI gera automaticamente
- **Conteúdo**: Todos endpoints documentados com exemplos

### ✅ **Docker Compose**
- **Arquivo**: `docker-compose.yml`
- **Comando**: `docker compose up` funciona
- **Serviços**: API + MySQL
- **Funcionalidades**:
  - Health checks
  - Volumes persistentes
  - Variáveis de ambiente
  - Dependências entre serviços

### ✅ **Kubernetes (Deployment, ConfigMap, Secrets, Services)**
- **Namespace**: `k8s/namespace.yaml`
- **Secrets**: `k8s/mysql-secret.yaml`, `k8s/api.yaml`
- **ConfigMaps**: `k8s/api.yaml`
- **StatefulSet**: `k8s/mysql-statefulset.yaml` (MySQL)
- **Deployment**: `k8s/api.yaml` (2 réplicas)
- **Services**: ClusterIP, NodePort, Ingress
- **Probes**: Liveness e Readiness implementados

### ✅ **Clean Architecture + SOLID**
```
app/
├── config.py              # Configuração centralizada
├── main.py                # Entry point FastAPI
├── init_db.py             # Inicialização BD
├── domain/                # 🟢 CAMADA DE DOMÍNIO
│   ├── models.py          # Entidades SQLAlchemy
│   └── schemas.py         # Contratos Pydantic
├── infrastructure/        # 🟢 CAMADA DE INFRAESTRUTURA
│   └── db.py             # Conexão banco de dados
└── routers/              # 🟢 CAMADA DE INTERFACE
    ├── vehicles.py       # Controllers veículos
    └── payments.py       # Controllers pagamentos
```

**Princípios SOLID Aplicados**:
- **S** - Single Responsibility: Cada classe/módulo tem uma responsabilidade
- **O** - Open/Closed: Extensível via herança e interfaces
- **L** - Liskov Substitution: Substituição de implementações
- **I** - Interface Segregation: Interfaces específicas (schemas)
- **D** - Dependency Inversion: Inversão via FastAPI dependency injection

---

## 📊 **EVIDÊNCIAS DE FUNCIONAMENTO**

### **1. Execução Local (Docker Compose)**

```bash
# Comando de execução
$ docker compose up --build

# Status dos containers
$ docker compose ps
NAME         IMAGE       COMMAND                  SERVICE   CREATED        STATUS                  PORTS
fiap_api     fiap_sub_2-api   "sh -c 'python -m ap…"   api       5 minutes ago   Up 5 minutes (healthy)   0.0.0.0:8000->8000/tcp
fiap_mysql   mysql:8.4        "docker-entrypoint.s…"   db        5 minutes ago   Up 5 minutes (healthy)   0.0.0.0:3306->3306/tcp

# Teste de saúde
$ curl http://localhost:8000/health
{"status":"ok"}
```

### **2. Deploy Kubernetes**

```bash
# Status dos recursos
$ kubectl get all -n fiap-vehicles
NAME                       READY   STATUS    RESTARTS   AGE
pod/api-55f8d84f49-sm427   1/1     Running   0          15m
pod/api-55f8d84f49-zkpgv   1/1     Running   0          15m
pod/mysql-0                1/1     Running   0          20m

NAME                   TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE
service/api            ClusterIP   10.43.81.86   <none>        80/TCP         20m
service/api-nodeport   NodePort    10.43.55.73   <none>        80:30080/TCP   10m
service/mysql          ClusterIP   None          <none>        3306/TCP       20m

NAME                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/api   2/2     2            2           20m

NAME                             DESIRED   CURRENT   READY   AGE
replicaset.apps/api-55f8d84f49   2         2         2       15m

NAME                     READY   AGE
statefulset.apps/mysql   1/1     20m

INGRESS                                     CLASS    HOSTS   ADDRESS         PORTS   AGE
ingress.networking.k8s.io/api-ingress      <none>   *       192.168.1.112   80      10m
```

### **3. Testes Funcionais API**

```bash
# Health Check
$ curl http://192.168.1.112/health
{"status":"ok"}

# Criar veículo
$ curl -X POST http://192.168.1.112/vehicles \
  -H "Content-Type: application/json" \
  -d '{"brand":"Toyota","model":"Corolla","year":2023,"color":"Branco","price":85000.00}'
{
  "id": 1,
  "brand": "Toyota",
  "model": "Corolla", 
  "year": 2023,
  "color": "Branco",
  "price": 85000.0,
  "status": "AVAILABLE",
  "createdAt": "2025-08-20T14:30:00"
}

# Listar veículos disponíveis
$ curl http://192.168.1.112/vehicles?status=AVAILABLE
{
  "items": [...],
  "total": 1,
  "page": 1,
  "size": 10
}
```

### **4. Swagger/OpenAPI**

- **URL**: http://192.168.1.112/docs
- **Conteúdo**: Interface completa com todos endpoints
- **Funcionalidades**: Try it out, schemas, exemplos

---

## 🗂️ **ESTRUTURA DO REPOSITÓRIO ENTREGUE**

```
FIAP_Sub_2/
├── README.md                    # ✅ Documentação principal
├── ROTEIRO_IMPLEMENTACAO.md     # ✅ Guia passo a passo
├── EVIDENCIAS_ENTREGAVEIS.md    # ✅ Este arquivo
├── .instructions.md             # ✅ Especificações originais
├── contexto.md                  # ✅ Contexto do projeto
├── ARCHITECTURE.md              # ✅ Diagrama arquitetural
├── docker-compose.yml           # ✅ Configuração Docker
├── Dockerfile                   # ✅ Imagem da aplicação
├── requirements.txt             # ✅ Dependências Python
├── .env.example                 # ✅ Template configuração
├── .gitignore                   # ✅ Exclusões Git
├── .dockerignore               # ✅ Exclusões Docker
├── app/                        # ✅ Código fonte
│   ├── config.py
│   ├── main.py
│   ├── init_db.py
│   ├── domain/
│   │   ├── models.py
│   │   └── schemas.py
│   ├── infrastructure/
│   │   └── db.py
│   └── routers/
│       ├── vehicles.py
│       └── payments.py
└── k8s/                        # ✅ Manifests Kubernetes
    ├── namespace.yaml
    ├── mysql-secret.yaml
    ├── mysql-statefulset.yaml
    ├── api.yaml
    ├── api-nodeport.yaml
    └── ingress.yaml
```

---

## 🎯 **CHECKLIST FINAL DE ENTREGÁVEIS**

### **Repositório GitHub**
- [x] Código-fonte completo
- [x] README.md explicativo  
- [x] Instruções de execução local
- [x] Instruções de teste
- [x] Decisões técnicas documentadas

### **Implementação**
- [x] Todas funcionalidades descritas no escopo
- [x] Clean Architecture implementada
- [x] Princípios SOLID aplicados
- [x] Validações e tratamento de erros
- [x] Documentação OpenAPI/Swagger

### **Containerização**
- [x] Dockerfile funcional
- [x] docker-compose.yml completo
- [x] `docker compose up` funciona
- [x] Aplicação acessível localmente

### **Kubernetes**
- [x] Deployment com múltiplas réplicas
- [x] ConfigMaps para configuração
- [x] Secrets para dados sensíveis
- [x] Services (ClusterIP/NodePort/Ingress)
- [x] StatefulSet para MySQL
- [x] Probes de saúde configurados

### **Funcionalidades**
- [x] CRUD de veículos funcional
- [x] Sistema de vendas implementado
- [x] Webhook de pagamento idempotente
- [x] Listagens ordenadas por preço
- [x] Filtros por status operacionais
- [x] Paginação implementada

---

## 📞 **INFORMAÇÕES PARA AVALIAÇÃO**

### **URLs de Acesso (Após Deploy)**
- **API Local**: http://localhost:8000
- **API Kubernetes**: http://192.168.1.112 ou http://192.168.1.112:30080
- **Documentação**: `/docs` em qualquer URL acima
- **Health Check**: `/health` em qualquer URL acima

### **Comandos de Validação Rápida**
```bash
# Local
docker compose up --build
curl http://localhost:8000/health

# Kubernetes  
kubectl apply -f k8s/
kubectl get pods -n fiap-vehicles
curl http://192.168.1.112/health
```

### **Tempo de Execução**
- **Setup inicial**: ~15 minutos
- **Execução local**: ~5 minutos
- **Deploy Kubernetes**: ~10 minutos
- **Total**: ~30 minutos

---

**✅ TODOS OS CRITÉRIOS E ENTREGÁVEIS FORAM ATENDIDOS CONFORME ESPECIFICAÇÃO**
