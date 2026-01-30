import Anthropic from '@anthropic-ai/sdk';
import { ANTHROPIC_API_KEY, SQL_SYSTEM_PROMPT, INSIGHT_SYSTEM_PROMPT } from './constants';

const anthropic = new Anthropic({
    apiKey: ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY,
});

// Use Sonnet for better reasoning on complex analytical queries
const MODEL = "claude-sonnet-4-20250514";
const MAX_TOKENS = 4096;

export interface ConversationItem {
    question?: string;
    sql?: string;
}

export class ClaudeService {
    static async generateSQL(question: string, context: ConversationItem[] = []): Promise<string> {
        let userMessage = question;
        if (context && context.length > 0) {
            const contextStr = context.map(c => `Q: ${c.question}\nSQL: ${c.sql}`).join('\n\n');
            userMessage = `Previous context:\n${contextStr}\n\nNew question: ${question}`;
        }

        try {
            const response = await anthropic.messages.create({
                model: MODEL,
                max_tokens: MAX_TOKENS,
                temperature: 0,
                system: SQL_SYSTEM_PROMPT,
                messages: [{ role: 'user', content: userMessage }],
            });

            // Extract text content
            let text = '';
            for (const block of response.content) {
                if (block.type === 'text') {
                    text += block.text;
                }
            }

            // Formatting cleanup - remove markdown code blocks
            let sql = text.replace(/```sql/gi, '').replace(/```/g, '').trim();

            // Extract SELECT/WITH statement if there's surrounding text
            const selectMatch = sql.match(/(WITH[\s\S]*|SELECT[\s\S]*)/i);
            if (selectMatch) {
                sql = selectMatch[0].trim();
            }

            return sql;
        } catch (e: any) {
            console.error("Anthropic API error:", e);
            throw new Error(`Anthropic API error: ${e.message}`);
        }
    }

    static async generateInsight(question: string, data: any[], sql: string): Promise<string> {
        let resultsPreview = '';
        let dataNote = '';

        if (data.length <= 50) {
            resultsPreview = JSON.stringify(data, null, 2);
            dataNote = `Complete results (${data.length} rows):`;
        } else {
            resultsPreview = JSON.stringify(data.slice(0, 20), null, 2);
            dataNote = `First 20 of ${data.length} rows:`;
        }

        const userMessage = `
Question: ${question}

SQL Query:
${sql}

${dataNote}
${resultsPreview}

Provide a business insight based on these results.
`;

        try {
            const response = await anthropic.messages.create({
                model: MODEL,
                max_tokens: MAX_TOKENS,
                temperature: 0,
                system: INSIGHT_SYSTEM_PROMPT,
                messages: [{ role: 'user', content: userMessage }],
            });

            let text = '';
            for (const block of response.content) {
                if (block.type === 'text') {
                    text += block.text;
                }
            }
            return text.trim();
        } catch (e: any) {
            return `Could not generate insight: ${e.message}`;
        }
    }
}
