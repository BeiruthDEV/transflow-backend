<p align="center">
  <img src="assets/logo-vassouras.png" alt="Universidade de Vassouras" width="400"/>
</p>

<h3 align="center">
  Universidade de Vassouras  
</h3>

---

### 📚 Curso: **Engenharia de Software** 
### 🖥️ Disciplina: **Banco de Dados Não Relacionais** 
### 👨‍🎓 Autor: **Matheus Beiruth**

---


# 🚖 TransFlow API

![CI](https://github.com/BeiruthDEV/transflow-backend/actions/workflows/ci.yml/badge.svg)

> Backend de alta performance para gestão de corridas urbanas com processamento assíncrono, arquitetura de microsserviços e Frontend Enterprise.

Este projeto simula um ecossistema completo de mobilidade urbana (semelhante a Uber/99), onde a alta concorrência de transações e a consistência de dados são tratadas utilizando mensageria (RabbitMQ), cache distribuído (Redis) e persistência NoSQL (MongoDB).

---

## 🖥️ Interface do Usuário (Frontend SPA)

O sistema conta com um **Dashboard Enterprise** desenvolvido com HTML5, TailwindCSS e JavaScript Puro, operando como uma Single Page Application (SPA) para monitoramento em tempo real.

### 1. Painel de Controle (Visão Geral)
Monitoramento de KPIs, solicitação de corridas e feed de transações em tempo real via WebSocket/Polling.
![Dashboard](assets/front1.png)

### 2. Gestão de Frota (Motoristas)
Algoritmo no Frontend processa os dados brutos da API para gerar métricas de desempenho individual dos motoristas.
![Motoristas](assets/front2.png)

### 3. Analytics Financeiro (Relatórios)
Análise de distribuição de pagamentos e cálculo de Ticket Médio da operação.
![Relatórios](assets/front3.png)

---

## 🔌 Backend & API (FastAPI)

A API foi construída focando em performance e documentação automática (OpenAPI 3.1).

### Documentação Interativa (Swagger UI)
Todos os endpoints são documentados e testáveis via navegador.
![Swagger Lista](assets/backend_post.png)

### Modelagem de Dados (Schemas Pydantic)
Validação rigorosa de tipos de dados na entrada (Request) e saída (Response) para garantir integridade.
![Schema JSON](assets/post.png)

---

## 🧪 Qualidade de Código (QA)

O projeto possui uma suíte de testes automatizada utilizando `pytest` e `TestContainers` (mocks), garantindo que a lógica de negócios funcione isoladamente da infraestrutura.

### Execução dos Testes
![Testes Pytest](assets/pytest.png)

---

## 🚀 Tecnologias Utilizadas

* **Linguagem:** Python 3.11
* **Web Framework:** FastAPI (Alta performance)
* **Mensageria:** RabbitMQ + FastStream (Processamento Assíncrono)
* **Banco de Dados:** MongoDB (Persistência de Corridas)
* **Cache & Sessão:** Redis (Gestão de Saldo Atômica)
* **Infraestrutura:** Docker & Docker Compose
* **Frontend:** Nginx Server (SPA)

---

## Arquitetura
 
![Arquitetura do TransFlow](assets/arquitetura.png)
 
1. A API recebe a corrida e salva o registro no MongoDB.
2. Em vez de atualizar o saldo na hora, a API publica um evento no RabbitMQ e já responde ao cliente.
3. Um worker separado consome o evento.
4. O worker soma o valor ao saldo do motorista no Redis com uma operação atômica.
## Decisões técnicas
 
- **Mensageria (RabbitMQ) em vez de atualizar o saldo direto na API:** a API responde rápido e não depende do cálculo do saldo. Se o worker cair, os eventos ficam na fila e são processados quando ele voltar.
- **Operação atômica no Redis:** duas corridas do mesmo motorista podem chegar ao mesmo tempo. Ler o saldo, somar e gravar em passos separados poderia perder uma das somas (race condition). A operação atômica do Redis faz a soma de uma vez só.
- **MongoDB para as corridas:** cada corrida é um documento com passageiro, motorista, trajeto e pagamento. O formato de documento encaixa naturalmente nesse dado.
- **Redis para o saldo:** o saldo é consultado com frequência e precisa de leitura rápida, que é o ponto forte de um banco em memória.
- **Testes com mocks:** os testes da API substituem MongoDB, RabbitMQ e Redis por mocks, então rodam em segundos e no CI sem precisar subir a infraestrutura.

---

## 📂 Estrutura do Projeto

```bash
transflow-backend/
├── assets/                  # Evidências (Prints)
│   ├── backend_post.png
│   ├── post.png
│   ├── front1.png
│   ├── front2.png
│   ├── front3.png
│   └── pytest.png
├── frontend/                # Aplicação Web (SPA)
│   ├── Dockerfile           # Configuração Nginx
│   ├── index.html           # Estrutura HTML
│   ├── script.js            # Lógica (API + Gráficos)
│   └── styles.css           # Estilos e Animações
├── src/                     # Código Fonte Backend
│   ├── database/            # Camada de Persistência
│   │   ├── mongo_client.py  # Driver Motor (MongoDB)
│   │   └── redis_client.py  # Driver Redis (Cache)
│   ├── models/              # Camada de Dados
│   │   └── corrida_model.py # Schemas Pydantic (Validação)              # Schemas Pydantic
│   ├── config.py            # Configurações Gerais
│   ├── consumer.py          # Worker RabbitMQ
│   ├── main.py              # API Server
│   └── producer.py          # Publicador de Eventos
├── tests/                   # Testes Automatizados
│   └── test_api.py
├── .env                     # Variáveis de Ambiente
├── docker-compose.yml       # Orquestração de Containers
├── Dockerfile               # Imagem do Backend
├── README.md                # Documentação Oficial
└── requirements.txt         # Dependências Python
```

## 🛠️ Como Executar

### Pré-requisitos
* Docker e Docker Compose instalados.

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/BeiruthDEV/transflow-backend.git](https://github.com/BeiruthDEV/transflow-backend.git)
    cd transflow-backend
    ```

2.  **Suba o ambiente:**
    ```bash
    docker-compose up --build
    ```

3.  **Acesse:**
    * **Dashboard:** [http://localhost](http://localhost)
    * **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Rodando os Testes

Para validar a aplicação dentro do container:

```bash
docker-compose exec app python -m pytest -v
