# DataForge Commerce

Projeto de engenharia de dados para gerar, validar, carregar e analisar dados sintéticos de um e-commerce.

## Objetivo

Construir uma pipeline reprodutível que transforma dados brutos de clientes, produtos e pedidos em estruturas prontas para análise no PostgreSQL.

## Fluxo de funcionamento

```text
                         src/generate_raw_data.py
                                     |
                                     v
                         data/raw/*.csv
                                     |
                                     v
                       src/validate_raw_data.py
                                     |
                       dados brutos aprovados
                                     |
                                     v
                   Docker Compose + PostgreSQL
                                     |
                                     v
                     sql/01_create_tables.sql
                                     |
                                     v
                       src/load_raw_data.py
                                     |
                                     v
                    src/validate_loaded_data.py
                    reconcilia CSVs e PostgreSQL
                                     |
                                     v
               sql/03_create_analytics_layer.sql
                                     |
                                     v
                         schema analytics
          +------------------+-------------------+
          |                  |                   |
          v                  v                   v
monthly_category_revenue  product_sales    customer_sales
```

Todas as etapas são orquestradas por `src/run_pipeline.py`. A execução é registrada no terminal e em `logs/pipeline.log`.

## Tecnologias

- Python 3.12
- Pandas
- SQLAlchemy e Psycopg
- PostgreSQL 16
- Docker e Docker Compose
- Pytest
- GitHub Actions

## Estrutura do projeto

```text
dataforge-commerce/
├── data/raw/                  # Arquivos CSV gerados
├── logs/                      # Logs locais da pipeline, ignorados pelo Git
├── sql/
│   ├── 01_create_tables.sql   # Estrutura das tabelas operacionais
│   ├── 02_analytics_queries.sql
│   └── 03_create_analytics_layer.sql
├── src/
│   ├── database.py            # Conexão reutilizável com PostgreSQL
│   ├── generate_raw_data.py
│   ├── validate_raw_data.py
│   ├── load_raw_data.py
│   ├── validate_loaded_data.py
│   └── run_pipeline.py        # Orquestrador principal
├── tests/
│   └── test_validations.py
├── .github/workflows/tests.yaml
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Pré-requisitos

- Python 3.12 ou compatível
- Docker Desktop em execução
- Git

## Configuração local

Crie e ative o ambiente virtual. Antes de instalar dependências, confirme que o terminal mostra `(.venv)`.

No Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto. Ele é local e não deve ser versionado:

```text
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_PORT=
```

## Executando a pipeline

Com a venv ativa e o Docker Desktop aberto, execute:

```bash
python src/run_pipeline.py
```

A pipeline executa, nesta ordem:

1. Gera os CSVs sintéticos em `data/raw/`.
2. Valida estrutura, valores nulos, duplicidades, datas, valores numéricos e chaves estrangeiras.
3. Inicia o PostgreSQL com Docker Compose.
4. Cria as tabelas necessárias, caso ainda não existam.
5. Limpa e recarrega os dados no banco.
6. Reconcilia a quantidade de linhas dos CSVs com as tabelas do PostgreSQL.
7. Cria ou atualiza as views do schema `analytics`.

## Validações de dados

As regras incluem:

- colunas obrigatórias;
- ausência de valores nulos;
- unicidade de IDs e e-mails;
- formato de datas;
- preços numéricos e positivos;
- quantidades positivas e inteiras;
- categorias e status permitidos;
- integridade referencial entre pedidos, clientes e produtos;
- reconciliação de contagens após a carga.

## Camada analítica

O schema `analytics` contém views reutilizáveis para relatórios e dashboards:

- `analytics.monthly_category_revenue`: faturamento mensal por categoria;
- `analytics.product_sales`: unidades vendidas, pedidos e faturamento por produto;
- `analytics.customer_sales`: pedidos concluídos e faturamento por cliente.

Exemplo de consulta:

```sql
SELECT *
FROM analytics.product_sales
ORDER BY revenue DESC
LIMIT 10;
```

## Testes

Execute os testes unitários com a venv ativa:

```bash
python -m pytest -v
```

Os testes cobrem as funções de validação de colunas, nulos, duplicidades, datas, números positivos, inteiros e chaves estrangeiras.

## Integração contínua

O workflow `.github/workflows/tests.yaml` executa a suíte de testes automaticamente no GitHub Actions a cada `push` ou pull request para a branch `main`.

## Segurança

- Não versione `.env`, `logs/`, `.vscode/` ou arquivos SQL de testes locais.
- Nunca inclua senhas nas consultas, no README ou em commits.
- Use o arquivo `.env` apenas no ambiente local.
