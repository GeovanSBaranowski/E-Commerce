# DataForge Commerce

Projeto de engenharia de dados para gerar, validar, carregar e analisar dados sintéticos de um e-commerce.

## Objetivo

Construir uma pipeline reprodutível que transforma dados brutos de clientes, produtos e pedidos em estruturas prontas para análise no PostgreSQL.

## Fluxo de funcionamento

```text
Inicialização ou reconstrução completa (manual)
  gerar data/raw/*.csv
    -> validar clientes, produtos e itens de pedidos
    -> criar tabelas no PostgreSQL
    -> TRUNCATE e recarregar as tabelas
    -> conferir contagens com os CSVs
    -> criar ou atualizar as views analytics

Rotina incremental (Airflow, diária)
  data/incoming/orders_*.csv
    -> validar cada lote e suas referências
    -> inserir itens ainda não existentes
    -> conferir as chaves (order_id, item_number) carregadas
    -> criar ou atualizar as views analytics
```

`src/run_pipeline.py` executa a reconstrução completa e registra sua saída no terminal e em `logs/pipeline.log`. A DAG `dataforge_pipeline` agenda somente a rotina incremental.

## Tecnologias

- Python 3.12
- Pandas
- SQLAlchemy e Psycopg
- PostgreSQL 16
- Docker e Docker Compose
- Apache Airflow
- Pytest
- GitHub Actions

## Estrutura do projeto

```text
dataforge-commerce/
├── data/raw/                  # Arquivos CSV gerados
├── data/incoming/             # Lotes incrementais de pedidos
├── airflow/
│   ├── dags/dataforge_pipeline.py
│   └── docker-compose.yaml
├── logs/                      # Logs locais da pipeline, ignorados pelo Git
├── sql/
│   ├── 01_create_tables.sql   # Estrutura das tabelas operacionais
│   ├── 02_analytics_queries.sql
│   ├── 03_create_analytics_layer.sql
│   └── 04_add_item_number.sql # Migração de bancos criados antes da chave composta
├── src/
│   ├── database.py            # Conexão reutilizável com PostgreSQL
│   ├── generate_raw_data.py
│   ├── validate_raw_data.py
│   ├── load_raw_data.py
│   ├── validate_loaded_data.py
│   ├── run_pipeline.py        # Reconstrução completa, manual
│   ├── validate_incoming_orders.py
│   ├── load_incoming_orders.py
│   ├── validate_incoming_loaded.py
│   └── run_incremental_pipeline.py
├── tests/
│   └── test_validations.py
├── .github/workflows/tests.yaml
├── docker-compose.yml
├── Dockerfile                 # Imagem local usada pelo Airflow
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

## Inicialização ou reconstrução completa

Com a venv ativa e o Docker Desktop aberto, execute na raiz do projeto:

```bash
python src/run_pipeline.py
```

Este comando executa, nesta ordem:

1. Gera os CSVs sintéticos em `data/raw/`.
2. Valida estrutura, valores nulos, duplicidades, datas, valores numéricos e chaves estrangeiras.
3. Inicia o PostgreSQL com Docker Compose.
4. Cria as tabelas necessárias, caso ainda não existam.
5. Executa `TRUNCATE` e recarrega os dados no banco.
6. Reconcilia a quantidade de linhas dos CSVs com as tabelas do PostgreSQL.
7. Cria ou atualiza as views do schema `analytics`.

**Atenção:** essa é uma reconstrução completa. Executá-la depois de uma carga incremental remove os itens recebidos em `data/incoming/` que não estejam também em `data/raw/orders.csv`. Use-a apenas quando quiser reinicializar o banco deliberadamente.

## Carga incremental de pedidos

Coloque novos lotes em `data/incoming/` com nomes no padrão `orders_*.csv`. Cada linha representa um item de pedido, identificado pelo par `(order_id, item_number)`. Os clientes e produtos referenciados precisam existir nos CSVs de `data/raw/` e nas tabelas do banco.

Para processar manualmente todos os lotes encontrados, execute na raiz do projeto, com a venv ativa e o PostgreSQL em execução:

```bash
python src/run_incremental_pipeline.py
```

O script processa os arquivos em ordem de nome: valida o lote, insere os itens e confere se suas chaves foram encontradas no banco. A restrição única `(order_id, item_number)` e `ON CONFLICT DO NOTHING` permitem repetir a carga sem duplicar itens. Essa política **não atualiza** um item já existente caso o conteúdo do CSV mude.

Também é possível processar e verificar um arquivo específico:

```bash
python src/load_incoming_orders.py data/incoming/orders_2026-10-01.csv
python src/validate_incoming_loaded.py data/incoming/orders_2026-10-01.csv
```

A DAG `dataforge_pipeline` executa diariamente a rotina incremental: verifica a conexão com o PostgreSQL, processa os arquivos de `data/incoming/` e atualiza as views. O agendamento depende de o computador, o Docker Desktop e os serviços do Airflow estarem em execução. A DAG não gera os CSVs brutos nem executa `TRUNCATE`.

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
- unicidade do par `(order_id, item_number)` dentro de cada lote;
- reconciliação de contagens após a reconstrução completa;
- verificação das chaves de cada lote após a carga incremental.

A verificação incremental confirma a presença das chaves no banco; ela ainda não compara todos os campos do item com o CSV.

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

Os testes cobrem as funções de validação de colunas, nulos, duplicidades, datas, números positivos, inteiros, chaves estrangeiras e a chave composta dos itens de pedido.

## Integração contínua

O workflow `.github/workflows/tests.yaml` executa a suíte de testes automaticamente no GitHub Actions a cada `push` ou pull request para a branch `main`.

## Segurança

- Não versione `.env`, `logs/`, `.vscode/` ou arquivos SQL de testes locais.
- Nunca inclua senhas nas consultas, no README ou em commits.
- Use o arquivo `.env` apenas no ambiente local.
