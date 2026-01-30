import { NextResponse } from 'next/server';
import { sql } from '@/lib/postgres';
import { SQLValidator } from '@/lib/sql-validator';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { sql: sqlQuery } = body;

        if (!sqlQuery) {
            return NextResponse.json({ error: 'SQL query is required' }, { status: 400 });
        }

        const { isValid, error, sql: validatedSql } = SQLValidator.validate(sqlQuery);

        if (!isValid) {
            return NextResponse.json({ error: `Invalid SQL: ${error}` }, { status: 400 });
        }

        const result = await sql.unsafe(validatedSql);

        // Extract column names from the first row
        let columns: string[] = [];
        if (result.length > 0) {
            columns = Object.keys(result[0]);
        }

        return NextResponse.json({
            data: result,
            columns: columns
        });
    } catch (error: any) {
        console.error('Database execution error:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
