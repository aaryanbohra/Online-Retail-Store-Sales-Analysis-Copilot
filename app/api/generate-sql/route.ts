import { NextResponse } from 'next/server';
import { ClaudeService } from '@/lib/claude';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { question, context } = body;

        if (!question) {
            return NextResponse.json({ error: 'Question is required' }, { status: 400 });
        }

        const sql = await ClaudeService.generateSQL(question, context);
        return NextResponse.json({ sql });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
