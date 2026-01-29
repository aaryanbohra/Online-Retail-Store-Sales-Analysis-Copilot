import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock the database module
vi.mock('@/lib/db', () => ({
    db: {
        query: vi.fn(),
    },
}));

// Mock the claude module
vi.mock('@/lib/claude', () => ({
    ClaudeService: {
        generateSQL: vi.fn(),
        generateInsight: vi.fn(),
    },
}));

import { db } from '@/lib/db';
import { ClaudeService } from '@/lib/claude';
import { POST as generateSqlHandler } from '@/app/api/generate-sql/route';
import { POST as executeQueryHandler } from '@/app/api/execute-query/route';
import { POST as generateInsightHandler } from '@/app/api/generate-insight/route';

// Helper to create a mock Request
function createMockRequest(body: object): Request {
    return new Request('http://localhost', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
}

describe('API Routes', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('POST /api/generate-sql', () => {
        it('generates SQL for a valid question', async () => {
            const mockSQL = 'SELECT country, SUM(revenue) FROM order_items GROUP BY country';
            vi.mocked(ClaudeService.generateSQL).mockResolvedValue(mockSQL);

            const request = createMockRequest({
                question: 'What is the revenue by country?',
            });

            const response = await generateSqlHandler(request);
            const data = await response.json();

            expect(response.status).toBe(200);
            expect(data.sql).toBe(mockSQL);
            expect(ClaudeService.generateSQL).toHaveBeenCalledWith(
                'What is the revenue by country?',
                undefined
            );
        });

        it('passes context to Claude service', async () => {
            const mockSQL = 'SELECT country, SUM(revenue) FROM order_items GROUP BY country';
            vi.mocked(ClaudeService.generateSQL).mockResolvedValue(mockSQL);

            const context = [
                { question: 'Total revenue?', sql: 'SELECT SUM(revenue) FROM order_items' },
            ];

            const request = createMockRequest({
                question: 'Break it down by country',
                context,
            });

            const response = await generateSqlHandler(request);
            expect(response.status).toBe(200);
            expect(ClaudeService.generateSQL).toHaveBeenCalledWith(
                'Break it down by country',
                context
            );
        });

        it('returns 400 when question is missing', async () => {
            const request = createMockRequest({});

            const response = await generateSqlHandler(request);
            const data = await response.json();

            expect(response.status).toBe(400);
            expect(data.error).toBe('Question is required');
        });

        it('returns 500 on Claude API error', async () => {
            vi.mocked(ClaudeService.generateSQL).mockRejectedValue(
                new Error('API rate limit exceeded')
            );

            const request = createMockRequest({
                question: 'What is the total revenue?',
            });

            const response = await generateSqlHandler(request);
            const data = await response.json();

            expect(response.status).toBe(500);
            expect(data.error).toBe('API rate limit exceeded');
        });
    });

    describe('POST /api/execute-query', () => {
        it('executes a valid SELECT query', async () => {
            const mockRows = [
                { country: 'UK', revenue: 500000 },
                { country: 'Germany', revenue: 200000 },
            ];
            vi.mocked(db.query).mockResolvedValue({
                rows: mockRows,
                fields: [{ name: 'country' }, { name: 'revenue' }],
            } as any);

            const request = createMockRequest({
                sql: 'SELECT country, SUM(revenue) as revenue FROM order_items GROUP BY country',
            });

            const response = await executeQueryHandler(request);
            const data = await response.json();

            expect(response.status).toBe(200);
            expect(data.data).toEqual(mockRows);
            expect(data.columns).toEqual(['country', 'revenue']);
        });

        it('returns 400 when SQL is missing', async () => {
            const request = createMockRequest({});

            const response = await executeQueryHandler(request);
            const data = await response.json();

            expect(response.status).toBe(400);
            expect(data.error).toBe('SQL query is required');
        });

        it('returns 400 for DROP statement', async () => {
            const request = createMockRequest({
                sql: 'DROP TABLE orders',
            });

            const response = await executeQueryHandler(request);
            const data = await response.json();

            expect(response.status).toBe(400);
            expect(data.error).toContain('Invalid SQL');
            expect(data.error).toContain('Only SELECT');
        });

        it('returns 400 for DELETE statement', async () => {
            const request = createMockRequest({
                sql: 'DELETE FROM orders WHERE 1=1',
            });

            const response = await executeQueryHandler(request);
            const data = await response.json();

            expect(response.status).toBe(400);
            expect(data.error).toContain('Invalid SQL');
        });

        it('returns 400 for SQL injection attempt', async () => {
            const request = createMockRequest({
                sql: "SELECT * FROM orders; DROP TABLE customers; --",
            });

            const response = await executeQueryHandler(request);
            const data = await response.json();

            expect(response.status).toBe(400);
            expect(data.error).toContain('Invalid SQL');
        });

        it('returns 400 for UNION SELECT injection', async () => {
            const request = createMockRequest({
                sql: "SELECT * FROM orders WHERE id = 1 UNION SELECT * FROM customers",
            });

            const response = await executeQueryHandler(request);
            const data = await response.json();

            expect(response.status).toBe(400);
            expect(data.error).toContain('Invalid SQL');
        });

        it('adds LIMIT to unlimited queries', async () => {
            vi.mocked(db.query).mockResolvedValue({
                rows: [{ id: 1 }],
                fields: [{ name: 'id' }],
            } as any);

            const request = createMockRequest({
                sql: 'SELECT * FROM orders',
            });

            await executeQueryHandler(request);

            expect(db.query).toHaveBeenCalledWith(expect.stringContaining('LIMIT 100'));
        });

        it('preserves existing LIMIT', async () => {
            vi.mocked(db.query).mockResolvedValue({
                rows: [{ id: 1 }],
                fields: [{ name: 'id' }],
            } as any);

            const request = createMockRequest({
                sql: 'SELECT * FROM orders LIMIT 10',
            });

            await executeQueryHandler(request);

            expect(db.query).toHaveBeenCalledWith('SELECT * FROM orders LIMIT 10');
        });

        it('returns 500 on database error', async () => {
            vi.mocked(db.query).mockRejectedValue(new Error('Connection refused'));

            const request = createMockRequest({
                sql: 'SELECT * FROM orders',
            });

            const response = await executeQueryHandler(request);
            const data = await response.json();

            expect(response.status).toBe(500);
            expect(data.error).toBe('Connection refused');
        });

        it('extracts columns from rows when fields not available', async () => {
            vi.mocked(db.query).mockResolvedValue({
                rows: [{ a: 1, b: 2, c: 3 }],
            } as any);

            const request = createMockRequest({
                sql: 'SELECT a, b, c FROM test',
            });

            const response = await executeQueryHandler(request);
            const data = await response.json();

            expect(data.columns).toEqual(['a', 'b', 'c']);
        });
    });

    describe('POST /api/generate-insight', () => {
        it('generates insight for valid input', async () => {
            const mockInsight =
                'Revenue in the UK accounts for 70% of total sales, indicating a strong domestic market.';
            vi.mocked(ClaudeService.generateInsight).mockResolvedValue(mockInsight);

            const request = createMockRequest({
                question: 'What is the revenue by country?',
                sql: 'SELECT country, SUM(revenue) FROM order_items GROUP BY country',
                data: [
                    { country: 'UK', revenue: 500000 },
                    { country: 'Germany', revenue: 200000 },
                ],
            });

            const response = await generateInsightHandler(request);
            const data = await response.json();

            expect(response.status).toBe(200);
            expect(data.insight).toBe(mockInsight);
        });

        it('returns 400 when question is missing', async () => {
            const request = createMockRequest({
                sql: 'SELECT * FROM orders',
                data: [],
            });

            const response = await generateInsightHandler(request);
            const data = await response.json();

            expect(response.status).toBe(400);
            expect(data.error).toBe('Missing required parameters');
        });

        it('returns 400 when sql is missing', async () => {
            const request = createMockRequest({
                question: 'What is revenue?',
                data: [],
            });

            const response = await generateInsightHandler(request);
            const data = await response.json();

            expect(response.status).toBe(400);
            expect(data.error).toBe('Missing required parameters');
        });

        it('returns 400 when data is missing', async () => {
            const request = createMockRequest({
                question: 'What is revenue?',
                sql: 'SELECT SUM(revenue) FROM order_items',
            });

            const response = await generateInsightHandler(request);
            const data = await response.json();

            expect(response.status).toBe(400);
            expect(data.error).toBe('Missing required parameters');
        });

        it('returns 500 on Claude API error', async () => {
            vi.mocked(ClaudeService.generateInsight).mockRejectedValue(
                new Error('Service unavailable')
            );

            const request = createMockRequest({
                question: 'What is revenue?',
                sql: 'SELECT SUM(revenue) FROM order_items',
                data: [{ total: 1000000 }],
            });

            const response = await generateInsightHandler(request);
            const data = await response.json();

            expect(response.status).toBe(500);
            expect(data.error).toBe('Service unavailable');
        });
    });
});
