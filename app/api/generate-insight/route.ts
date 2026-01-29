import { NextResponse } from 'next/server';
import { ClaudeService } from '@/lib/claude';

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { question, sql, data } = body;

        if (!question || !sql || !data) {
            return NextResponse.json({ error: 'Missing required parameters' }, { status: 400 });
        }

        const insight = await ClaudeService.generateInsight(question, data, sql);
        return NextResponse.json({ insight });
    } catch (error: any) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
