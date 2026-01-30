import { NextResponse } from 'next/server';
import { sql } from '@/lib/postgres';

export async function GET() {
    try {
        const yearsRes = await sql`
            SELECT DISTINCT TO_CHAR(invoice_date, 'YYYY') as year
            FROM orders
            ORDER BY year DESC
        `;

        const countriesRes = await sql`
            SELECT DISTINCT country
            FROM customers
            ORDER BY country ASC
        `;

        return NextResponse.json({
            years: yearsRes.map((r: any) => r.year),
            countries: countriesRes.map((r: any) => r.country)
        });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
