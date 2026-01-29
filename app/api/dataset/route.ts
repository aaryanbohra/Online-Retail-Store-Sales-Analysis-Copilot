import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url);
        const limit = parseInt(searchParams.get('limit') || '50');
        const offset = parseInt(searchParams.get('offset') || '0');

        // Get total count (approximation or exact?)
        // Exact count is slow on large tables. We can query count separately or just rely on huge number.
        // For now, simple count on order_items.
        const countResult = await db.query('SELECT COUNT(*) as total FROM order_items');
        const total = parseInt(countResult.rows[0].total);

        const query = `
      SELECT 
        oi.invoice_id,
        TO_CHAR(o.invoice_date, 'YYYY-MM-DD HH24:MI:SS') as invoice_date,
        oi.stock_code,
        oi.description,
        oi.quantity,
        oi.unit_price,
        oi.revenue,
        c.customer_id,
        c.country
      FROM order_items oi
      JOIN orders o ON oi.invoice_id = o.invoice_id
      JOIN customers c ON o.customer_id = c.customer_id
      ORDER BY o.invoice_date DESC
      LIMIT $1 OFFSET $2
    `;

        const result = await db.query(query, [limit, offset]);

        return NextResponse.json({
            data: result.rows,
            total,
            limit,
            offset
        });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
