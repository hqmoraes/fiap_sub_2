# 🎥 ROTEIRO PARA VÍDEO DE DEMONSTRAÇÃO

## Guia para Gravação do Vídeo Demonstrativo

---

## 📝 **ROTEIRO SUGERIDO (8-10 minutos)**

### **1. Introdução (1 minuto)**
- Apresentação do projeto: "FIAP Vehicles - API de Revenda de Veículos"
- Tecnologias utilizadas: FastAPI, MySQL, Docker, Kubernetes
- Arquitetura: Clean Architecture + SOLID

### **2. Estrutura do Código (1-2 minutos)**
```bash
# Mostrar estrutura do projeto
tree -I 'venv|__pycache__|*.pyc'

# Destacar:
# - Separação em camadas (domain, infrastructure, routers)
# - Arquivos Docker e Kubernetes
# - Documentação completa
```

### **3. Execução Local (2-3 minutos)**
```bash
# Mostrar arquivo de configuração
cat .env.example

# Executar aplicação
docker compose up --build

# Aguardar subir e testar
curl http://localhost:8000/health
```

**Mostrar no navegador:**
- http://localhost:8000/docs (Swagger UI)
- Demonstrar alguns endpoints na interface

### **4. Testes da API (2-3 minutos)**
```bash
# 1. Health Check
curl http://localhost:8000/health

# 2. Criar veículo
curl -X POST http://localhost:8000/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Toyota",
    "model": "Corolla",
    "year": 2023,
    "color": "Branco",
    "price": 85000.00
  }'

# 3. Listar veículos
curl http://localhost:8000/vehicles?status=AVAILABLE

# 4. Vender veículo (usar ID retornado)
curl -X POST http://localhost:8000/vehicles/1/sell \
  -H "Content-Type: application/json" \
  -d '{
    "buyerCpf": "12345678901",
    "saleDate": "2025-08-20",
    "salePrice": 80000.00,
    "paymentCode": "PAY123"
  }'

# 5. Webhook de pagamento
curl -X POST http://localhost:8000/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "paymentCode": "PAY123",
    "status": "PAID"
  }'

# 6. Listar veículos vendidos
curl http://localhost:8000/vehicles?status=SOLD
```

### **5. Deploy Kubernetes (2-3 minutos)**
```bash
# Mostrar manifests
ls -la k8s/

# Aplicar manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mysql-secret.yaml
kubectl apply -f k8s/mysql-statefulset.yaml
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/api-nodeport.yaml
kubectl apply -f k8s/ingress.yaml

# Verificar deploy
kubectl get all -n fiap-vehicles

# Aguardar pods subirem
kubectl get pods -n fiap-vehicles -w
```

### **6. Teste da Aplicação no Kubernetes (1 minuto)**
```bash
# Teste interno
kubectl run test-pod --image=curlimages/curl --rm -it --restart=Never -n fiap-vehicles -- curl http://api/health

# Teste externo
curl http://192.168.1.112/health
curl http://192.168.1.112:30080/health
```

**Mostrar no navegador:**
- http://192.168.1.112/docs (Swagger via Kubernetes)

### **7. Conclusão (30 segundos)**
- Recapitular o que foi demonstrado
- Destacar alta disponibilidade (2 réplicas)
- Mencionar documentação completa no repositório

---

## 🎬 **DICAS PARA GRAVAÇÃO**

### **Preparação**
1. **Limpar ambiente** antes de gravar
2. **Testar todos comandos** previamente
3. **Ter terminal com fonte grande** (legibilidade)
4. **Browser em tela cheia** para Swagger
5. **Preparar dados de teste** (veículo exemplo)

### **Durante a Gravação**
- **Falar pausadamente** explicando cada passo
- **Esperar comandos terminarem** antes de prosseguir
- **Destacar resultados importantes** (status 200, pods Running)
- **Mostrar erros e como resolver** (se houver)

### **Estrutura de Telas**
1. **Editor de código** - estrutura do projeto
2. **Terminal** - comandos e execução
3. **Browser** - Swagger UI e testes
4. **Split screen** quando necessário

---

## 📋 **CHECKLIST PRÉ-GRAVAÇÃO**

### Ambiente Preparado
- [ ] Docker funcionando
- [ ] Kubernetes (k3s) funcionando  
- [ ] Projeto clonado e limpo
- [ ] Terminal com fonte legível
- [ ] Browser configurado
- [ ] Comandos testados

### Aplicação Funcionando
- [ ] `docker compose up` funciona
- [ ] Health check responde
- [ ] Swagger UI acessível
- [ ] Deploy Kubernetes funciona
- [ ] Pods em estado Running
- [ ] Acesso externo funcionando

### Documentação
- [ ] README.md atualizado
- [ ] ROTEIRO_IMPLEMENTACAO.md completo
- [ ] EVIDENCIAS_ENTREGAVEIS.md finalizado
- [ ] Scripts de setup testados

---

## 🎯 **PONTOS IMPORTANTES A DESTACAR**

### **Arquitetura**
- Clean Architecture implementada
- Separação clara de responsabilidades
- Princípios SOLID aplicados

### **Funcionalidades**
- CRUD completo de veículos
- Sistema de vendas integrado
- Webhook idempotente de pagamentos
- Listagens ordenadas e paginadas

### **Infraestrutura**
- Containerização completa
- Deploy em Kubernetes
- Alta disponibilidade (múltiplas réplicas)
- Configuração via ConfigMaps/Secrets

### **Qualidade**
- Documentação OpenAPI automática
- Health checks implementados
- Tratamento de erros adequado
- Código limpo e organizando

---

## 📹 **ESTRUTURA FINAL DO VÍDEO**

```
00:00 - 01:00  Introdução e overview
01:00 - 02:30  Estrutura do código
02:30 - 05:00  Execução local e testes
05:00 - 08:00  Deploy Kubernetes
08:00 - 09:00  Testes finais
09:00 - 10:00  Conclusão
```

**Duração total recomendada: 8-10 minutos**
