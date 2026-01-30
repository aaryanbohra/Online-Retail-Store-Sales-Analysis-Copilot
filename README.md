# Analytics Copilot
<a href="https://online-retail-store-sales-analysis.vercel.app/">
  <img width="1311" height="579" alt="image" src="https://github.com/user-attachments/assets/97c420c7-5683-424d-b14f-354ccbe35ea7" />                                               </a>

An intelligent analytics dashboard powered by Claude AI that transforms raw sales data into actionable business insights. Ask natural language questions about your sales data and get instant SQL queries with AI-generated insights.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-000000?logo=vercel&logoColor=white)](https://online-retail-store-sales-analysis.vercel.app/)
![Next.js](https://img.shields.io/badge/Next.js-16.1-black?logo=next.js)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript&logoColor=white)
![Claude AI](https://img.shields.io/badge/Claude-Sonnet%204-9B59B6)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase)
![License](https://img.shields.io/badge/License-MIT-green)

**[Try the Live Demo](https://online-retail-store-sales-analysis.vercel.app/)** - Deployed on Vercel

## Features

- **AI-Powered SQL Generation** - Ask questions in natural language, Claude generates optimized SQL queries
- **Interactive Dashboard** - Real-time KPIs, revenue trends, customer analytics, and product performance
- **Natural Language Insights** - Automatic business intelligence generation from query results
- **Cost-Controlled API Usage** - Daily spending limits on Claude API calls ($1/day default)
- **Serverless Deployment** - Optimized for Vercel with Supabase connection pooler
- **Advanced Analytics** - Customer segmentation, price tier analysis, temporal trends
- **Responsive Design** - Works seamlessly on desktop and mobile

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16, React 19, TypeScript, TanStack Query |
| **Backend** | Next.js API Routes, Node.js |
| **Database** | Supabase (PostgreSQL) with connection pooler |
| **AI** | Claude Sonnet 4 (Anthropic API) |
| **Deployment** | Vercel (serverless) |
| **Analytics** | Custom SQL generation & execution |

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Supabase account (PostgreSQL database)
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
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   POSTGRES_URL=postgresql://user:password@db.region.supabase.co:5432/postgres
   DATABASE_URL=postgresql://user:password@db.region.supabase.co:5432/postgres
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) in your browser.

## Dashboard Features

### KPIs
- Total Revenue
- Total Orders
- Total Customers
- Average Order Value
- Countries Served

### Analytics
- **Revenue Trends** - Monthly revenue visualization
- **Customer Insights** - Segmentation, frequency analysis, repeat rates
- **Product Performance** - Top products by revenue and quantity
- **Price Distribution** - Revenue breakdown by price tier
- **Temporal Analysis** - Revenue patterns by day of week and hour

### Copilot
Ask questions like:
- "What's my top revenue product?"
- "Which countries generate the most revenue?"
- "Show me customer lifetime value distribution"
- "What's the average order value by country?"

Claude AI generates optimized SQL queries and business insights automatically.

## API Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard` | GET | Get KPIs and chart data with optional filtering |
| `/api/dashboard/filters` | GET | Get available years and countries |
| `/api/dataset` | GET | Get paginated raw transaction data |
| `/api/copilot` | POST | Generate SQL and insights from natural language |
| `/api/execute-query` | POST | Execute validated custom SQL queries |

## Deployment

### Deploy to Vercel

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your repository
   - Select framework: Next.js

3. **Add environment variables** in Vercel Settings:
   - `DATABASE_URL`: Use Supabase connection pooler endpoint
   - `ANTHROPIC_API_KEY`: Your Claude API key

4. **Deploy**
   - Vercel will automatically build and deploy
   - Auto-redeploys on git push to main branch

### Supabase Connection Pooler

**For Vercel (serverless):**
```
postgres://user:password@aws-region.pooler.supabase.com:6543/database?options=reference%3Dreference_id&sslmode=require
```

**For local development:**
```
postgresql://user:password@db.region.supabase.co:5432/database
```

## Project Structure

```
├── app/
│   ├── api/
│   │   ├── dashboard/          # Dashboard KPIs & charts
│   │   │   └── filters/        # Available filter options
│   │   ├── dataset/            # Raw data endpoint
│   │   ├── copilot/            # AI copilot endpoint
│   │   └── execute-query/      # Query execution endpoint
│   ├── page.tsx                # Home page
│   ├── layout.tsx              # Root layout
│   └── globals.css             # Global styles
├── lib/
│   ├── claude.ts               # Claude API client
│   ├── postgres.ts             # Database client
│   ├── cost-tracker.ts         # API cost tracking
│   ├── sql-validator.ts        # SQL validation
│   └── constants.ts            # System prompts
├── components/
│   ├── dashboard/              # Dashboard components
│   ├── copilot/                # Copilot UI components
│   └── ui/                     # Reusable UI components
├── tests/                      # Test suite (116 tests)
└── README.md
```

## Cost Control

Built-in cost tracking prevents overspending on Claude API:

- **Daily Limit**: $1 USD (configurable)
- **Tracking**: Per-request token counting and cost calculation
- **Reset**: Automatically resets at midnight UTC
- **Pricing**: Claude Sonnet 4 ($3/M input tokens, $15/M output tokens)

Modify the daily limit in `lib/cost-tracker.ts`:
```typescript
const DAILY_LIMIT = 1.0; // Change to your preferred limit
```

## Database Schema

The app expects these tables in Supabase PostgreSQL:

### orders
```sql
- invoice_id (string)
- customer_id (string)
- invoice_date (timestamp)
- country (string)
```

### order_items
```sql
- invoice_id (string)
- description (string)
- quantity (integer)
- unit_price (decimal)
- revenue (decimal)
- stock_code (string)
```

### customers
```sql
- customer_id (string)
- country (string)
```

## Development

### Run Tests
```bash
npm test
```

All 116 tests cover:
- API routes
- SQL validation
- Chart selectors
- Query execution

### Build for Production
```bash
npm run build
```

### Format Code
```bash
npm run lint
```

## Features in Detail

### AI-Powered Analytics
- Natural language to SQL translation
- Query optimization and validation
- Automatic insight generation from results
- Cost tracking and budget enforcement

### Interactive Filters
- Filter by year and country
- Real-time data updates
- Mobile-responsive UI

### Real-Time Data
- Instant KPI calculations
- Dynamic chart updates
- Paginated data browsing

## Troubleshooting

### Connection Issues

**Timeout on Vercel**
- ✅ Ensure `DATABASE_URL` uses the connection pooler endpoint
- ✅ Check Supabase network restrictions allow Vercel IPs
- ✅ Verify credentials are correct

**Connection Refused Locally**
- ✅ Check `.env` file has correct credentials
- ✅ Verify Supabase project is running
- ✅ Test with `psql` command directly

### API Issues

**Cost Limit Reached**
- ✅ Check `.cost-tracking.json` file for daily usage
- ✅ Limit resets daily at midnight UTC
- ✅ Increase `DAILY_LIMIT` in `lib/cost-tracker.ts`

**Slow Dashboard Queries**
- ✅ Add database indexes on `invoice_date`, `country`, `customer_id`
- ✅ Check Supabase query performance dashboard
- ✅ Consider query optimization

**Invalid SQL Generated**
- ✅ Check SQL validator in `lib/sql-validator.ts`
- ✅ Review system prompts in `lib/constants.ts`
- ✅ Test queries in Supabase SQL editor

## Performance Metrics

- **Dashboard Load**: < 2 seconds
- **API Response**: 200-500ms average
- **Query Generation**: < 1 second
- **Cold Start (Vercel)**: 1-3 seconds

## Environment Setup

### Supabase Setup
1. Create new project
2. Load sample data (Online Retail dataset)
3. Create tables: `orders`, `order_items`, `customers`
4. Get connection string from project settings

### Anthropic API Setup
1. Sign up at [anthropic.com](https://console.anthropic.com)
2. Create API key
3. Set monthly spending limit if desired

### Vercel Setup
1. Connect GitHub repository
2. Set environment variables
3. Deploy with one click

## Testing

```bash
# Run all tests
npm test

# Run specific test file
npm test -- tests/api-routes.test.ts

# Watch mode
npm test -- --watch
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

---

**Built with ❤️ using Next.js, Claude AI, and Supabase**
