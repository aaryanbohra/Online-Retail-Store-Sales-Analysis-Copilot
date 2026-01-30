import { NextResponse } from 'next/server';
import { sql } from '@/lib/postgres';

function isValidFilter(values: string[]): boolean {
  return values.length > 0 && values[0] !== '' && values[0] !== 'all';
}

function buildWhereClause(years: string[], countries: string[]): { whereClause: string; values: string[] } {
  const conditions: string[] = [];
  const values: string[] = [];
  let paramCount = 1;

  if (isValidFilter(years)) {
    const placeholders = years.map(() => `$${paramCount++}`).join(',');
    conditions.push(`TO_CHAR(o.invoice_date, 'YYYY') IN (${placeholders})`);
    values.push(...years);
  }

  if (isValidFilter(countries)) {
    const placeholders = countries.map(() => `$${paramCount++}`).join(',');
    conditions.push(`o.country IN (${placeholders})`);
    values.push(...countries);
  }

  const whereClause = conditions.length > 0 ? 'WHERE ' + conditions.join(' AND ') : '';
  return { whereClause, values };
}

export async function GET(request: Request): Promise<Response> {
  try {
    const { searchParams } = new URL(request.url);
    const years = searchParams.get('year')?.split(',') || [];
    const countries = searchParams.get('country')?.split(',') || [];

    const { whereClause, values } = buildWhereClause(years, countries);

    // 1. KPIs
    const kpiQuery = `
            SELECT 
                SUM(oi.revenue) as total_revenue,
                COUNT(DISTINCT o.invoice_id) as total_orders,
                COUNT(DISTINCT o.customer_id) as total_customers,
                SUM(oi.revenue) / NULLIF(COUNT(DISTINCT o.invoice_id), 0) as avg_order_value,
                COUNT(DISTINCT o.country) as total_countries
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            ${whereClause}
        `;

    // 2. Revenue Trend (Monthly)
    const trendQuery = `
            SELECT 
                TO_CHAR(o.invoice_date, 'YYYY-MM') as month,
                SUM(oi.revenue) as revenue
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            ${whereClause}
            GROUP BY month
            ORDER BY month
        `;

    // 3. Revenue by Day of Week
    const dayQuery = `
            SELECT 
                TO_CHAR(o.invoice_date, 'Day') as day_name,
                EXTRACT(DOW FROM o.invoice_date) as day_index,
                SUM(oi.revenue) as revenue
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            ${whereClause}
            GROUP BY day_name, day_index
            ORDER BY day_index
        `;

    // 4. Revenue by Hour
    const hourQuery = `
            SELECT 
                EXTRACT(HOUR FROM o.invoice_date) as hour,
                SUM(oi.revenue) as revenue
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            ${whereClause}
            GROUP BY hour
            ORDER BY hour
        `;

    // 5. Top Countries
    const countryQuery = `
            SELECT 
                o.country,
                SUM(oi.revenue) as revenue,
                COUNT(DISTINCT o.invoice_id) as orders,
                COUNT(DISTINCT o.customer_id) as customers
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            ${whereClause}
            GROUP BY o.country
            ORDER BY revenue DESC
            LIMIT 10
        `;

    // 6. Top Products (Revenue & Qty)
    const productQuery = `
            SELECT 
                oi.description,
                SUM(oi.revenue) as revenue,
                SUM(oi.quantity) as quantity
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            ${whereClause}
            GROUP BY oi.description
            ORDER BY revenue DESC
            LIMIT 20
        `;

    // 7. Price Tiers
    const priceTierQuery = `
            WITH price_data AS (
                SELECT
                    revenue,
                    quantity,
                    CASE
                        WHEN unit_price < 1 THEN 'Under £1'
                        WHEN unit_price < 2 THEN '£1-2'
                        WHEN unit_price < 5 THEN '£2-5'
                        WHEN unit_price < 10 THEN '£5-10'
                        WHEN unit_price < 25 THEN '£10-25'
                        ELSE '£25+'
                    END as tier
                FROM order_items oi
                JOIN orders o ON oi.invoice_id = o.invoice_id
                ${whereClause ? whereClause + ' AND unit_price > 0' : 'WHERE unit_price > 0'}
            )
            SELECT 
                tier,
                SUM(revenue) as revenue,
                SUM(quantity) as units_sold,
                COUNT(*) as product_count
            FROM price_data
            GROUP BY tier
            ORDER BY tier
        `;

    // 8. Top Customers
    const customerQuery = `
            SELECT
                o.customer_id,
                SUM(oi.revenue) as revenue,
                COUNT(DISTINCT o.invoice_id) as orders
            FROM order_items oi
            JOIN orders o ON oi.invoice_id = o.invoice_id
            ${whereClause ? whereClause + ' AND o.customer_id IS NOT NULL' : 'WHERE o.customer_id IS NOT NULL'}
            GROUP BY o.customer_id
            ORDER BY revenue DESC
            LIMIT 10
        `;

    // 9. Customer Segments & Frequency
    const customerFrequencyQuery = `
            WITH customer_stats AS (
                SELECT
                    o.customer_id,
                    COUNT(DISTINCT o.invoice_id) as order_count,
                    SUM(oi.revenue) as total_revenue
                FROM order_items oi
                JOIN orders o ON oi.invoice_id = o.invoice_id
                ${whereClause ? whereClause + ' AND o.customer_id IS NOT NULL' : 'WHERE o.customer_id IS NOT NULL'}
                GROUP BY o.customer_id
            ),
            frequency_groups AS (
                SELECT 
                    CASE 
                        WHEN order_count = 1 THEN '1 order'
                        WHEN order_count = 2 THEN '2 orders'
                        WHEN order_count <= 5 THEN '3-5 orders'
                        WHEN order_count <= 10 THEN '6-10 orders'
                        WHEN order_count <= 20 THEN '11-20 orders'
                        ELSE '20+ orders'
                    END as freq_group
                FROM customer_stats
            ),
            value_segments AS (
                SELECT 
                    CASE 
                        WHEN total_revenue <= 100 THEN '£0-100'
                        WHEN total_revenue <= 500 THEN '£100-500'
                        WHEN total_revenue <= 1000 THEN '£500-1K'
                        WHEN total_revenue <= 2500 THEN '£1K-2.5K'
                        WHEN total_revenue <= 5000 THEN '£2.5K-5K'
                        ELSE '£5K+'
                    END as segment,
                    total_revenue
                FROM customer_stats
            )
            SELECT 
                (SELECT json_agg(f) FROM (SELECT freq_group, COUNT(*) as count FROM frequency_groups GROUP BY freq_group) f) as frequency,
                (SELECT json_agg(s) FROM (SELECT segment, COUNT(*) as customers, SUM(total_revenue) as total_revenue FROM value_segments GROUP BY segment) s) as segments,
                (SELECT AVG(total_revenue) FROM customer_stats) as avg_clv,
                (SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_revenue) FROM customer_stats) as median_clv,
                (SELECT COUNT(*)::float / (SELECT COUNT(*) FROM customer_stats) FROM customer_stats WHERE order_count > 1) as repeat_rate
            FROM customer_stats
            LIMIT 1
        `;

    // Execute all queries in parallel
    const [
      kpiRes, trendRes, dayRes, hourRes,
      countryRes, productRes, priceRes,
      customerRes, freqRes
    ] = await Promise.all([
      sql.unsafe(kpiQuery, values),
      sql.unsafe(trendQuery, values),
      sql.unsafe(dayQuery, values),
      sql.unsafe(hourQuery, values),
      sql.unsafe(countryQuery, values),
      sql.unsafe(productQuery, values),
      sql.unsafe(priceTierQuery, values),
      sql.unsafe(customerQuery, values),
      sql.unsafe(customerFrequencyQuery, values)
    ]);

    return NextResponse.json({
      kpis: kpiRes[0],
      charts: {
        revenueTrend: trendRes,
        revenueByDay: dayRes,
        revenueByHour: hourRes,
        countryRevenue: countryRes,
        topProducts: productRes,
        priceTiers: priceRes,
        topCustomers: customerRes,
        customerStats: freqRes[0]
      }
    });

  } catch (error: any) {
    console.error('Dashboard error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
