# Online Retail Sales Analysis Copilot

An intelligent analytics dashboard powered by Claude AI that transforms raw sales data into actionable business insights. Ask natural language questions about your sales data and get instant SQL queries with AI-generated insights.

## Features

- **AI-Powered SQL Generation** - Ask questions in natural language, Claude generates optimized SQL queries
- **Interactive Dashboard** - Real-time KPIs, revenue trends, customer analytics, and product performance
- **Natural Language Insights** - Automatic business intelligence generation from query results
- **Cost-Controlled API Usage** - Daily spending limits on Claude API calls
- **Serverless Deployment** - Optimized for Vercel with Supabase connection pooler

## Tech Stack

- **Frontend**: Next.js 16, React, TanStack Query
- **Backend**: Next.js API Routes
- **Database**: Supabase (PostgreSQL)
- **AI**: Claude API (Sonnet 4)
- **Deployment**: Vercel

## Getting Started

### Prerequisites

- Node.js 18+
- Supabase account
- Anthropic API key (for Claude)
- Vercel account (optional, for deployment)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo>
   cd "Sales Analysis"
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key
   POSTGRES_URL=postgresql://user:password@host:port/database
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude API key from Anthropic | Yes |
| `DATABASE_URL` | PostgreSQL connection string (for Vercel) | Yes |
| `POSTGRES_URL` | PostgreSQL connection string (for local) | Yes |

## Key Features Explained

### Dashboard
- **KPIs**: Total revenue, orders, customers, AOV, countries
- **Revenue Trends**: Monthly revenue visualization
- **Customer Analytics**: Segmentation, frequency, repeat rates
- **Product Performance**: Top products by revenue and quantity
- **Price Tiers**: Revenue distribution by price range

### Copilot
- Write natural language questions about your sales data
- Claude generates optimized SQL queries
- View results in a clean table format
- Get AI-generated business insights automatically

### Cost Control
- Daily spending limit: $1 USD (configurable)
- Automatic cost tracking per request
- Resets daily at midnight UTC
- Claude Sonnet 4 pricing: $3 per 1M input tokens, $15 per 1M output tokens

## API Routes

- `GET /api/dashboard` - Get KPIs and chart data
- `GET /api/dashboard/filters` - Get available years and countries
- `GET /api/dataset` - Get paginated raw data
- `POST /api/copilot` - Generate SQL and insights from natural language

## Deployment

### Deploy to Vercel

1. Push to GitHub
2. Connect repository to Vercel
3. Add environment variables:
   - `DATABASE_URL`: Use Supabase connection pooler for serverless
   - `ANTHROPIC_API_KEY`: Your Claude API key
4. Deploy

The app will automatically redeploy on git push to main branch.

### Supabase Connection Pooler

For Vercel (serverless), use the connection pooler:
```
postgres://user:password@aws-region.pooler.supabase.com:6543/database?options=reference%3Dreference_id&sslmode=require
```

For local development, use the direct connection:
```
postgresql://user:password@db.region.supabase.co:5432/database
```

## Project Structure

```
├── app/
│   ├── api/                 # API routes
│   │   ├── dashboard/       # Dashboard data
│   │   ├── copilot/         # AI copilot
│   │   └── execute-query/   # Custom query execution
│   ├── page.tsx            # Home page
│   └── layout.tsx          # Root layout
├── lib/
│   ├── claude.ts           # Claude API client
│   ├── postgres.ts         # Database client
│   ├── cost-tracker.ts     # API cost tracking
│   └── sql-validator.ts    # SQL query validation
├── components/             # React components
└── tests/                  # Test suite
```

## Cost Tracking

The app includes built-in cost tracking for Claude API usage:

- Located in `lib/cost-tracker.ts`
- Tracks daily spending with $1/day default limit
- Automatically resets at midnight UTC
- Logs all API costs to console

To modify the daily limit, edit `DAILY_LIMIT` in `lib/cost-tracker.ts`.

## Development

### Run Tests
```bash
npm test
```

### Build for Production
```bash
npm run build
```

### Format Code
```bash
npm run lint
```

## Database Schema

The app expects these tables in Supabase:
- `orders` - Invoice data with dates and customers
- `order_items` - Line items with product details and revenue
- `customers` - Customer information with countries

## Troubleshooting

**Connection Timeout on Vercel**
- Ensure `DATABASE_URL` uses the connection pooler endpoint
- Check that Supabase network restrictions allow Vercel IPs

**Cost Limit Reached**
- Check `.cost-tracking.json` file for daily usage
- Limit resets daily at midnight UTC
- Contact Anthropic to increase API quota

**Slow Dashboard Queries**
- Consider adding database indexes on frequently filtered columns
- Check Supabase query performance in monitoring dashboard

## License

MIT
