# Deal Knowledge Base (POC)

End-to-end proof-of-concept for Ansarada's **deal graph knowledge base** — a
Streamlit demo app backed by an embedded [LadybugDB](https://docs.ladybugdb.com/)
graph store and AWS Bedrock (Claude) for natural-language querying.

## What it demonstrates

- **Chat Assistant** — ask natural-language questions, answered by an LLM
  grounded in facts retrieved from the deal graph.
- **Graph Explorer** — interactive visualization of deals, documents,
  entities, clauses, and their relationships.
- **Risk Analysis** — surfaced risk flags by category/severity across deals.
- **Cross-Document Intelligence** — shared entities and reference links
  between documents across a deal.
- **Tabular Review** — reviewable table of clauses and their linked risk flags.

## Stack

- **Python 3.12** managed with **Poetry**
- **LadybugDB** — embedded, Cypher-queryable graph database (local files;
  swap to S3-backed storage later)
- **Streamlit** — multi-page UI (chat, graph viz, tables, charts)
- **AWS Bedrock** (Anthropic Claude) — LLM reasoning over graph context
- **streamlit-agraph / plotly** — graph and chart visualizations

## Getting started

```bash
poetry install

# Requires AWS credentials with Bedrock access, e.g.:
aws sso login --profile <your-profile>
export AWS_PROFILE=<your-profile>

poetry run streamlit run src/deal_kb/app/Home.py
```

The graph database is created automatically on first run at
`data/graph/deal_graph.lbdb` and seeded with mock deal data.

## Configuration

Environment variables (prefix `DKB_`), optionally set via a `.env` file:

| Variable               | Default                                      | Description                     |
|------------------------|-----------------------------------------------|----------------------------------|
| `DKB_AWS_REGION`       | `ap-southeast-2`                              | AWS region for Bedrock           |
| `DKB_BEDROCK_MODEL_ID` | `anthropic.claude-3-5-sonnet-20241022-v2:0`   | Bedrock model ID                 |
| `DKB_GRAPH_DB_PATH`    | `data/graph/deal_graph.lbdb`                  | LadybugDB database file path     |
