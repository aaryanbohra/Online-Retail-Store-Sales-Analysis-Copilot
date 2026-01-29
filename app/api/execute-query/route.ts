import { NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { SQLValidator } from '@/lib/sql-validator';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { sql } = body;

        if (!sql) {
            return NextResponse.json({ error: 'SQL query is required' }, { status: 400 });
        }

        const { isValid, error, sql: validatedSql } = SQLValidator.validate(sql);

        if (!isValid) {
            return NextResponse.json({ error: `Invalid SQL: ${error}` }, { status: 400 });
        }

        const result = await db.query(validatedSql);

        // Extract column names from the first row or fields
        let columns: string[] = [];
        if (result.fields) {
            columns = result.fields.map(f => f.name);
        } else if (result.rows.length > 0) {
            columns = Object.keys(result.rows[0]);
        }

        return NextResponse.json({
            data: result.rows,
            columns: columns
        });
    } catch (error: any) {
        console.error('Database execution error:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
