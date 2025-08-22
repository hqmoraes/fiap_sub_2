# 🚀 FIAP Vehicles API - Funcionamento Completo

## ✅ Status do Projeto: 100% FUNCIONAL

A API está **totalmente funcional** com Clean Architecture rigorosamente implementada.

## 🎯 Como Executar

### 1. Pré-requisitos
```bash
# Python 3.12+ e Docker
python3 --version
docker --version
```

### 2. Configuração do Ambiente
```bash
# 1. Clone/Acesse o diretório
cd /home/hqmoraes/FIAP_Sub_2

# 2. Ative o ambiente virtual
source venv/bin/activate

# 3. Inicie o MySQL via Docker
docker compose up -d db

# 4. Verifique se MySQL está rodando
docker logs fiap_mysql

# 5. Inicie a aplicação
python main.py
```

### 3. Acesso à API
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 Endpoints Testados e Funcionais

### 📋 Health Check
```bash
curl http://localhost:8000/health
# Resposta: {"status":"healthy","message":"FIAP Vehicles API - Clean Architecture"...}
```

### 🚗 Veículos

#### Listar todos os veículos
```bash
curl http://localhost:8000/vehicles/
```

#### Criar veículo
```bash
curl -X POST http://localhost:8000/vehicles/ \
  -H "Content-Type: application/json" \
  -d '{"brand": "Honda", "model": "Civic", "year": 2024, "price": 105000.00, "color": "Azul"}'
```

#### Buscar veículo por ID
```bash
curl http://localhost:8000/vehicles/1
```

#### Veículos disponíveis (ordenados por preço)
```bash
curl http://localhost:8000/vehicles/status/available
```

#### Veículos vendidos (ordenados por preço)
```bash
curl http://localhost:8000/vehicles/status/sold
```

### 💰 Vendas

#### Listar todas as vendas
```bash
curl http://localhost:8000/sales/
```

#### Criar venda (CPF deve ser válido)
```bash
curl -X POST http://localhost:8000/sales/ \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id": 1, "customer_cpf": "11144477735", "amount": 105000.00}'
```

#### Buscar venda por ID
```bash
curl http://localhost:8000/sales/1
```

#### Atualizar status de pagamento
```bash
curl -X PUT http://localhost:8000/sales/1/payment-status \
  -H "Content-Type: application/json" \
  -d '{"payment_status": "approved"}'
```

#### Webhook de pagamento (idempotente)
```bash
curl -X POST http://localhost:8000/sales/payment-webhook \
  -H "Content-Type: application/json" \
  -d '{"sale_id": 1, "status": "approved"}'
```

## 🏗️ Arquitetura Clean implementada

### 📁 Estrutura de Diretórios
```
src/
├── entities/           # 🔴 Camada mais pura - Regras de negócio
│   ├── vehicle.py      # Entity Vehicle com validações
│   └── sale.py         # Entity Sale com validação de CPF
├── use_cases/          # 🟡 Casos de uso - Regras da aplicação
│   ├── vehicle_use_cases.py
│   └── sale_use_cases.py
├── controllers/        # 🟢 Controllers Clean (não web)
│   ├── vehicle_controller.py
│   └── sale_controller.py
├── gateways/           # 🔵 Tradutores Entity ↔ Repository
│   ├── vehicle_gateway.py
│   └── sale_gateway.py
├── presenters/         # 🟣 Formatação de saídas
│   ├── vehicle_presenter.py
│   └── sale_presenter.py
└── external/           # ⚫ Camada externa - Frameworks
    ├── database/       # SQLAlchemy
    └── web/           # FastAPI
```

### 🔄 Fluxo de Dados
```
FastAPI → Web Controller → Clean Controller → Gateway → UseCase → Entity
```

### 🎯 Princípios SOLID Aplicados
- **S**: Single Responsibility - Cada classe tem uma responsabilidade
- **O**: Open/Closed - Extensível via interfaces
- **L**: Liskov Substitution - Implementações intercambiáveis
- **I**: Interface Segregation - Interfaces específicas por domínio
- **D**: Dependency Inversion - Dependências injetadas

## ✅ Funcionalidades Implementadas

### 🚗 Gestão de Veículos
- ✅ CRUD completo (Create, Read, Update, Delete)
- ✅ Validações rigorosas (marca, modelo, ano, preço, cor)
- ✅ Status automático (available/sold)
- ✅ Ordenação por preço
- ✅ Filtros por status

### 💰 Sistema de Vendas
- ✅ Criação de vendas com validação de CPF
- ✅ Algoritmo de validação de CPF implementado
- ✅ Status de pagamento (pending/approved/rejected)
- ✅ Webhook idempotente para pagamentos
- ✅ Atualização automática de status do veículo

### 🛡️ Validações e Segurança
- ✅ CPF mascarado na exibição (111.***.**7-35)
- ✅ Validação algorítmica de CPF
- ✅ Validações de dados de entrada
- ✅ Tratamento de erros robusto

### 📊 API Features
- ✅ Documentação OpenAPI automática
- ✅ CORS configurado
- ✅ Health check endpoint
- ✅ Responses padronizadas
- ✅ Status codes HTTP apropriados

## 🔍 Debug e Troubleshooting

### Endpoints de Debug Disponíveis
```bash
# Testar conexão com banco
curl http://localhost:8000/debug/database

# Recriar tabelas (se necessário)
curl -X POST http://localhost:8000/debug/recreate-tables
```

### Logs
- Aplicação: `debug.log`
- MySQL: `docker logs fiap_mysql`

## 🎉 Resultado Final

### ✅ Projeto 100% Funcional
- ✅ Clean Architecture rigorosamente implementada
- ✅ Todos os endpoints funcionando
- ✅ Banco de dados MySQL conectado
- ✅ Validações implementadas
- ✅ Documentação automática
- ✅ SOLID principles aplicados
- ✅ Testes manuais realizados e aprovados

### 📋 Endpoints Testados
- ✅ Health check
- ✅ CRUD de veículos
- ✅ CRUD de vendas
- ✅ Webhook de pagamentos
- ✅ Filtros e ordenações
- ✅ Documentação OpenAPI

**A API está pronta para produção!** 🚀
