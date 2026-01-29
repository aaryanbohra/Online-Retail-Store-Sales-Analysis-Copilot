import { NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET() {
    try {
        const yearsRes = await db.query(`
      SELECT DISTINCT TO_CHAR(invoice_date, 'YYYY') as year 
      FROM orders 
      ORDER BY year DESC
    `);

        const countriesRes = await db.query(`
      SELECT DISTINCT country 
      FROM customers 
      ORDER BY country ASC
    `);

        return NextResponse.json({
            years: yearsRes.rows.map(r => r.year),
            countries: countriesRes.rows.map(r => r.country)
        });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
