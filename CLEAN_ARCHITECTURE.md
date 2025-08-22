# 🏗️ FIAP Vehicles API - Clean Architecture Implementada

## 📊 **REESTRUTURAÇÃO COMPLETA CONFORME CRÍTICAS**

O projeto foi **completamente reestruturado** para seguir a **Clean Architecture** de forma rigorosa, conforme as orientações do Prof. Robert Santos.

---

## 🎯 **NOVA ESTRUTURA - CLEAN ARCHITECTURE**

```
src/
├── entities/                 # 🔴 CAMADA MAIS PURA
│   ├── vehicle.py           # Entity Vehicle com validações puras
│   └── sale.py              # Entity Sale com validações de CPF
│
├── use_cases/               # 🟡 REGRAS DE NEGÓCIO
│   ├── vehicle_use_cases.py # Use Cases de veículos
│   └── sale_use_cases.py    # Use Cases de vendas
│
├── controllers/             # 🟢 ORQUESTRAÇÃO CLEAN
│   ├── vehicle_controller.py # Controller Clean (não Web)
│   └── sale_controller.py   # Controller Clean (não Web)
│
├── gateways/               # 🔵 TRADUTORES
│   ├── vehicle_gateway.py  # Gateway Entity ↔ Repository
│   └── sale_gateway.py     # Gateway Entity ↔ Repository
│
├── presenters/             # 🟣 FORMATAÇÃO DE SAÍDA
│   ├── vehicle_presenter.py # Formatação para API/JSON
│   └── sale_presenter.py   # Formatação para API/JSON
│
└── external/               # ⚫ CAMADA EXTERNA
    ├── database/           # Implementações de Repository
    │   ├── models.py       # SQLAlchemy Models
    │   ├── vehicle_repository.py
    │   └── sale_repository.py
    └── web/                # Controllers Web (FastAPI)
        ├── schemas.py      # Pydantic Schemas
        ├── vehicle_routes.py
        └── sale_routes.py
```

---

## 🔥 **IMPLEMENTAÇÃO RIGOROSA - CLEAN ARCHITECTURE**

### 🔴 **1. ENTITIES (Camada mais pura)**

**Localização**: `src/entities/`

**Responsabilidades**:
- ✅ Apenas regras de negócio **PURAS**
- ✅ Validações sem dependências externas
- ✅ Algoritmo de validação de CPF
- ✅ Validações de ano, preço, marca, modelo
- ✅ Lógica de status (available/sold)

**Exemplo** (`vehicle.py`):
```python
class Vehicle:
    def _validate_cpf(self, cpf: str) -> str:
        # Validação PURA do algoritmo do CPF
        if not self._validate_cpf_algorithm(cpf):
            raise ValueError("CPF inválido")
    
    def mark_as_sold(self) -> None:
        # Regra de negócio PURA
        if not self.is_available():
            raise ValueError("Veículo já foi vendido")
```

### 🟡 **2. USE CASES (Regras de negócio com mundo externo)**

**Localização**: `src/use_cases/`

**Responsabilidades**:
- ✅ Orquestra Entities + Gateways
- ✅ Regras de negócio que envolvem persistência
- ✅ Validações de existência (veículo existe?)
- ✅ Regras de venda (veículo disponível?)

**Exemplo** (`sale_use_cases.py`):
```python
class CreateSaleUseCase:
    def execute(self, vehicle_id: int, customer_cpf: str, amount: Decimal) -> Sale:
        # Verifica se veículo existe e está disponível
        vehicle = self._vehicle_gateway.find_vehicle_by_id(vehicle_id)
        if not vehicle.is_available():
            raise ValueError("Veículo não está disponível")
        
        # Cria Entity (validações automáticas)
        sale = Sale(vehicle_id, customer_cpf, amount)
        
        # Marca veículo como vendido
        vehicle.mark_as_sold()
```

### 🟢 **3. CONTROLLERS (Clean Architecture - NÃO Web)**

**Localização**: `src/controllers/`

**Responsabilidades**:
- ✅ **Recebe repositório** da Controller Web
- ✅ **Instancia Gateway** com repositório injetado
- ✅ **Instancia Use Cases** com Gateway injetado
- ✅ **Orquestra fluxo**: UseCase → Presenter
- ✅ **Retorna dados formatados** para Controller Web

**Exemplo** (`vehicle_controller.py`):
```python
class VehicleController:
    def __init__(self, repository: VehicleRepositoryInterface):
        # Injeta repositório no Gateway (SOLID - DIP)
        self._gateway = VehicleGateway(repository)
        
        # Injeta Gateway nos Use Cases
        self._create_use_case = CreateVehicleUseCase(self._gateway)
    
    def create_vehicle(self, brand: str, model: str, ...) -> Dict[str, Any]:
        # Executa Use Case
        vehicle = self._create_use_case.execute(...)
        
        # Formata resposta via Presenter
        return VehiclePresenter.to_create_response(vehicle)
```

### 🔵 **4. GATEWAYS (Tradutores Entity ↔ Repository)**

**Localização**: `src/gateways/`

**Responsabilidades**:
- ✅ **Traduz Entity → DTO** para repositório
- ✅ **Traduz DTO → Entity** do repositório
- ✅ **Abstrai repositório** para o mundo interno
- ✅ **Converte tipos** (Decimal ↔ float, Enum ↔ string)

**Exemplo** (`vehicle_gateway.py`):
```python
class VehicleGateway:
    def save_vehicle(self, vehicle: Vehicle) -> Vehicle:
        # Converte Entity para DTO (mundo externo)
        vehicle_data = self._entity_to_dict(vehicle)
        
        # Salva no repositório externo
        saved_data = self._repository.save(vehicle_data)
        
        # Converte dados salvos de volta para Entity
        return self._dict_to_entity(saved_data)
```

### 🟣 **5. PRESENTERS (Formatação para mundo externo)**

**Localização**: `src/presenters/`

**Responsabilidades**:
- ✅ **Converte Entity → JSON** para API
- ✅ **Formata respostas** de sucesso/erro
- ✅ **Mascaramento** de dados sensíveis (CPF)
- ✅ **Formatação brasileira** de valores

**Exemplo** (`sale_presenter.py`):
```python
class SalePresenter:
    @staticmethod
    def to_public_dict(sale: Sale) -> Dict[str, Any]:
        return {
            'id': sale.id,
            'customer_cpf': SalePresenter._mask_cpf(sale.customer_cpf),  # 123.***.**9-00
            'amount': float(sale.amount)
        }
```

### ⚫ **6. EXTERNAL (Camada externa - Frameworks)**

**Localização**: `src/external/`

**Responsabilidades**:
- ✅ **Implementações concretas** de Repository (SQLAlchemy)
- ✅ **Controllers Web** (FastAPI)
- ✅ **Schemas de validação** (Pydantic)
- ✅ **Pode usar frameworks** livremente

**Exemplo** (`vehicle_routes.py`):
```python
def get_vehicle_controller(session: Session = Depends(get_db_session)) -> VehicleController:
    # Instancia repositório concreto (SQLAlchemy)
    repository = SQLAlchemyVehicleRepository(session)
    
    # Injeta no Controller da Clean Architecture
    return VehicleController(repository)

@router.post("/")
async def create_vehicle(
    vehicle_data: VehicleCreate,
    controller: VehicleController = Depends(get_vehicle_controller)
):
    # Controller Web injeta repositório no Controller Clean
    result = controller.create_vehicle(...)
```

---

## 🎯 **FLUXO COMPLETO - INVERSÃO DE DEPENDÊNCIAS**

### 📥 **Criação de Veículo**:
```
1. FastAPI (Web Controller) recebe requisição
2. Pydantic valida dados de entrada
3. Web Controller instancia SQLAlchemy Repository
4. Web Controller injeta Repository no Clean Controller
5. Clean Controller injeta Repository no Gateway
6. Clean Controller injeta Gateway no Use Case
7. Use Case cria Entity (validações puras)
8. Use Case salva via Gateway
9. Gateway traduz Entity → DTO → Repository
10. Repository persiste no banco (SQLAlchemy)
11. Gateway traduz DTO → Entity
12. Clean Controller formata via Presenter
13. Web Controller retorna JSON (FastAPI)
```

### 🔄 **Webhook de Pagamento**:
```
1. FastAPI recebe webhook
2. Web Controller injeta repositórios no Clean Controller
3. Clean Controller usa ProcessPaymentWebhookUseCase
4. Use Case busca Sale via Gateway
5. Entity aplica regra de negócio (approve_payment)
6. Gateway persiste alteração
7. Presenter formata resposta idempotente
8. FastAPI retorna 200 (sempre)
```

---

## ✅ **PRINCÍPIOS SOLID APLICADOS**

### 🎯 **S** - Single Responsibility Principle
- ✅ **Entity**: Apenas regras de negócio puras
- ✅ **Use Case**: Apenas uma operação de negócio
- ✅ **Gateway**: Apenas tradução Entity ↔ Repository
- ✅ **Presenter**: Apenas formatação de saída
- ✅ **Controller**: Apenas orquestração

### 🎯 **O** - Open/Closed Principle  
- ✅ **Interfaces** para Repository (abertas para extensão)
- ✅ **Gateways** isolam implementações (fechadas para modificação)

### 🎯 **L** - Liskov Substitution Principle
- ✅ **Qualquer implementação** de Repository pode substituir
- ✅ **SQLAlchemy**, **MongoDB**, **Memory** - todas funcionam

### 🎯 **I** - Interface Segregation Principle
- ✅ **VehicleRepositoryInterface** - apenas métodos de veículo
- ✅ **SaleRepositoryInterface** - apenas métodos de venda

### 🎯 **D** - Dependency Inversion Principle
- ✅ **Use Cases dependem de abstrações** (Gateways)
- ✅ **Controllers injetam dependências** (Repository → Gateway → UseCase)
- ✅ **Camadas internas não conhecem externas**

---

## 🚀 **EXECUÇÃO**

```bash
# 1. Ativar ambiente virtual
source venv/bin/activate

# 2. Executar aplicação
python main.py

# 3. Acessar documentação
http://localhost:8001/docs
```

### 📋 **Endpoints Disponíveis**

#### 🚗 **Veículos**
- `POST /vehicles/` - Criar veículo
- `GET /vehicles/{id}` - Buscar por ID
- `GET /vehicles/` - Listar todos
- `GET /vehicles/status/available` - Disponíveis (ordenados por preço)
- `GET /vehicles/status/sold` - Vendidos (ordenados por preço)
- `PUT /vehicles/{id}` - Atualizar
- `DELETE /vehicles/{id}` - Excluir

#### 💰 **Vendas**
- `POST /sales/` - Criar venda
- `GET /sales/{id}` - Buscar por ID
- `GET /sales/vehicle/{vehicle_id}` - Buscar por veículo
- `GET /sales/` - Listar todas
- `PUT /sales/{id}/payment-status` - Atualizar pagamento
- `POST /sales/payment-webhook` - Webhook (idempotente)

---

## 🏆 **DIFERENÇAS DA IMPLEMENTAÇÃO ANTERIOR**

### ❌ **Antes (Estrutura Simples)**
```
app/
├── domain/models.py     # SQLAlchemy + Entity misturados
├── routers/            # Lógica de negócio nos routers
└── infrastructure/     # Repository simples
```

### ✅ **Agora (Clean Architecture Rigorosa)**
```
src/
├── entities/           # Entities PURAS
├── use_cases/         # Regras de negócio isoladas
├── controllers/       # Controllers Clean (não Web)
├── gateways/          # Tradutores Entity ↔ Repository
├── presenters/        # Formatação para API
└── external/          # Frameworks (FastAPI, SQLAlchemy)
```

---

## 🎓 **ADERÊNCIA ÀS ORIENTAÇÕES DO PROF. ROBERT SANTOS**

### ✅ **Controller Clean Architecture**
- **Separada** da Controller Web ✅
- **Orquestra** fluxo UseCase → Presenter ✅
- **Injeta** repositório no Gateway ✅
- **Injeta** Gateway no UseCase ✅

### ✅ **UseCase**
- **Instancia Entity** ✅
- **Regras de negócio** com mundo externo ✅
- **Gateway injetado** pela Controller ✅
- **Não instancia** Gateway internamente ✅

### ✅ **Entity (Domain)**
- **Mais pura possível** ✅
- **Validações sem dependências** ✅
- **Algoritmo de CPF** implementado ✅
- **Apenas regras de negócio** ✅

### ✅ **Gateway**
- **Tradutor** Entity ↔ Repository ✅
- **Abstrai repositório** ✅
- **Converte DTO ↔ Entity** ✅
- **Repository injetado** ✅

### ✅ **Presenter**
- **Formata saída** para mundo externo ✅
- **Converte Entity → JSON** ✅
- **Máscaras e formatações** ✅
- **Pode gerar PDF, relatórios** ✅

---

**🎯 Agora o projeto segue a Clean Architecture de forma rigorosa e acadêmica!**
