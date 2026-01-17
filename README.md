# Analytics Copilot

An AI-powered business intelligence tool that lets you query your sales data using natural language. Built with Streamlit and Claude AI.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://online-retail-store-sales-analysis-copilot.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)
![License](https://img.shields.io/badge/License-MIT-green)

**[Try the Live Demo](https://online-retail-store-sales-analysis-copilot.streamlit.app/)**

## Overview

Analytics Copilot transforms natural language questions into SQL queries, executes them against your database, and provides visualizations along with AI-generated insights. Simply ask questions like:

- "What was total revenue in 2011?"
- "Show monthly revenue trend"
- "Top 10 products by revenue"
- "Which country has the highest sales?"

## Dataset

This project uses the **Online Retail II** dataset from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii).

### About the Data

- **Source**: UK-based non-store online retail company
- **Period**: December 2009 to December 2011
- **Records**: 1,067,371 transactions
- **Business**: Gift-ware retailer (B2B wholesalers)

### Schema

| Table | Columns |
|-------|---------|
| `customers` | customer_id, country |
| `orders` | invoice_id, invoice_date, customer_id, country |
| `order_items` | order_item_id, invoice_id, stock_code, description, quantity, unit_price, revenue |

### Original Variables

| Variable | Description |
|----------|-------------|
| InvoiceNo | 6-digit invoice number (prefix 'C' = cancellation) |
| StockCode | 5-digit product code |
| Description | Product name |
| Quantity | Quantity per transaction |
| InvoiceDate | Transaction date and time |
| UnitPrice | Price per unit (GBP) |
| CustomerID | 5-digit customer identifier |
| Country | Customer's country |

## Features

- **Natural Language Queries**: Ask questions in plain English
- **Auto-generated SQL**: Claude AI converts questions to valid SQLite queries
- **Smart Visualizations**: Automatic chart selection (line, bar, KPI, table)
- **AI Insights**: Brief analysis of query results
- **Query History**: Track your recent queries
- **CSV Export**: Download results for further analysis

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Sales Analysis"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   MODEL=claude-3-haiku-20240307
   ```

5. **Prepare the database**

   Download the dataset from UCI and place the CSV files in the project folder, then run:
   ```bash
   python setup_database.py
   ```

## Usage

Start the application:
```bash
streamlit run Home.py
```

The app will open in your browser at `http://localhost:8501`.

Navigate using the sidebar:
- **Home**: Overview and getting started
- **Copilot**: AI-powered natural language queries
- **Dashboard**: Interactive analytics dashboard
- **Dataset**: Browse the original dataset

## Project Structure

```
Sales Analysis/
├── Home.py                # Main entry point (multi-page app)
├── pages/
│   ├── 1_Copilot.py       # AI Copilot page
│   ├── 2_Dashboard.py     # Analytics dashboard page
│   └── 3_Dataset.py       # Original dataset viewer
├── config.py              # Configuration and prompts
├── setup_database.py      # Database initialization script
├── analytics.db           # SQLite database
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in repo)
└── utils/
    ├── llm_client.py      # Anthropic API wrapper
    ├── sql_validator.py   # SQL safety validation
    └── chart_selector.py  # Visualization logic
```

## Configuration

Key settings in `config.py`:

| Setting | Description |
|---------|-------------|
| `MODEL` | Claude model to use (default: claude-3-haiku) |
| `MAX_TOKENS` | Maximum response tokens |
| `DEFAULT_LIMIT` | Default row limit for queries |
| `MAX_ROWS_FOR_CHART` | Threshold for table vs chart display |

## SQL Safety

The application includes built-in safety features:
- Blocks destructive keywords (DROP, DELETE, UPDATE, etc.)
- Prevents multiple SQL statements
- Disallows SQL comments
- Auto-applies row limits to unbounded queries

## Acknowledgments

- Dataset: [UCI Machine Learning Repository - Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- AI: [Anthropic Claude](https://www.anthropic.com/)
- UI: [Streamlit](https://streamlit.io/)

## License

MIT License
