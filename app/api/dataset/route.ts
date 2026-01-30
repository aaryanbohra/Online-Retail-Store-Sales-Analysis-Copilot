import { NextResponse } from 'next/server';
import { sql } from '@/lib/postgres';

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url);
        const limit = parseInt(searchParams.get('limit') || '50');
        const offset = parseInt(searchParams.get('offset') || '0');

        // Get total count
        const countResult = await sql`SELECT COUNT(*) as total FROM order_items`;
        const total = parseInt(countResult[0].total);

        const result = await sql`
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
            LIMIT ${limit} OFFSET ${offset}
        `;

        return NextResponse.json({
            data: result,
            total,
            limit,
            offset
        });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
