## Arquitetura proposta

```mermaid
flowchart LR
  subgraph Client
    UI[Frontend Web]
  end

  subgraph Cluster[Kubernetes 192.168.1.112]
    subgraph NS[Namespace: fiap-vehicles]
      API[FastAPI Deployment x2]
      SVC_API[Service API (ClusterIP:80->8000)]
      CFG[ConfigMap api-config]
      SCRT[Secret api-secret]

      DB[(PVC)]
      MYSQL[(MySQL StatefulSet)]
      SVC_DB[Service MySQL (Headless)]
    end
  end

  UI -->|HTTP/Ingress*| SVC_API --> API
  API -->|SQL (3306)| SVC_DB --> MYSQL --> DB

  classDef res fill:#f5f5f5,stroke:#888,stroke-width:1px
  class CFG,SCRT,DB,SVC_DB,SVC_API res
```

Notas:
- Ingress opcional (quando expor publicamente). No mínimo, Service interno.
- MySQL via StatefulSet com PVC para persistência.
- Segredos via Secret; configs via ConfigMap.
- API com readiness/liveness probes e réplicas >= 2.
