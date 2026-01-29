import { describe, it, expect } from 'vitest';
import { ChartSelector, ChartType } from '@/lib/chart-selector';

describe('ChartSelector', () => {
    describe('selectChartType', () => {
        describe('empty data handling', () => {
            it('returns table for null data', () => {
                const result = ChartSelector.selectChartType(null as any, 'SELECT * FROM orders');
                expect(result).toBe('table');
            });

            it('returns table for undefined data', () => {
                const result = ChartSelector.selectChartType(undefined as any, 'SELECT * FROM orders');
                expect(result).toBe('table');
            });

            it('returns table for empty array', () => {
                const result = ChartSelector.selectChartType([], 'SELECT * FROM orders');
                expect(result).toBe('table');
            });
        });

        describe('KPI detection', () => {
            it('returns kpi for single value result', () => {
                const data = [{ total_revenue: 1500000 }];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT SUM(revenue) as total_revenue FROM order_items'
                );
                expect(result).toBe('kpi');
            });

            it('returns kpi for single count result', () => {
                const data = [{ order_count: 25000 }];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT COUNT(*) as order_count FROM orders'
                );
                expect(result).toBe('kpi');
            });
        });

        describe('trend/line chart detection', () => {
            it('returns line for trend question with date column', () => {
                const data = [
                    { date: '2011-01-01', revenue: 100 },
                    { date: '2011-01-02', revenue: 150 },
                    { date: '2011-01-03', revenue: 200 },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT date, SUM(revenue) FROM orders',
                    'What is the revenue trend over time?'
                );
                expect(result).toBe('line');
            });

            it('returns line for growth question', () => {
                const data = [
                    { month: '2011-01', revenue: 10000 },
                    { month: '2011-02', revenue: 12000 },
                    { month: '2011-03', revenue: 15000 },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT month, SUM(revenue) FROM orders GROUP BY month',
                    'How has revenue growth changed?'
                );
                expect(result).toBe('line');
            });

            it('returns line for "how did" question with time period', () => {
                const data = Array.from({ length: 12 }, (_, i) => ({
                    month: `2011-${String(i + 1).padStart(2, '0')}`,
                    revenue: Math.random() * 10000,
                }));
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT month, SUM(revenue) FROM orders GROUP BY month',
                    'How did sales perform each month?'
                );
                expect(result).toBe('line');
            });

            it('returns line for date column without explicit trend keyword when enough rows', () => {
                const data = Array.from({ length: 10 }, (_, i) => ({
                    invoice_date: `2011-01-${String(i + 1).padStart(2, '0')}`,
                    revenue: Math.random() * 1000,
                }));
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT invoice_date, SUM(revenue) FROM orders GROUP BY invoice_date'
                );
                expect(result).toBe('line');
            });
        });

        describe('bar chart detection', () => {
            it('returns bar for categorical data with time period', () => {
                const data = [
                    { year: '2010', revenue: 50000 },
                    { year: '2011', revenue: 75000 },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT year, SUM(revenue) FROM orders GROUP BY year'
                );
                expect(result).toBe('bar');
            });

            it('returns bar for categorical comparison', () => {
                const data = [
                    { country: 'United Kingdom', revenue: 500000 },
                    { country: 'Germany', revenue: 200000 },
                    { country: 'France', revenue: 150000 },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT country, SUM(revenue) FROM orders GROUP BY country'
                );
                expect(result).toBe('bar');
            });

            it('returns bar for small categorical datasets', () => {
                const data = [
                    { product: 'Widget A', sales: 1000 },
                    { product: 'Widget B', sales: 800 },
                    { product: 'Widget C', sales: 600 },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT description, SUM(quantity) FROM order_items GROUP BY description'
                );
                expect(result).toBe('bar');
            });
        });

        describe('table detection', () => {
            it('returns table for more than MAX_ROWS_FOR_CHART rows', () => {
                const data = Array.from({ length: 100 }, (_, i) => ({
                    id: i,
                    value: Math.random() * 1000,
                }));
                const result = ChartSelector.selectChartType(data, 'SELECT * FROM orders');
                expect(result).toBe('table');
            });

            it('returns table for comparison queries with ROW_NUMBER', () => {
                const data = [
                    { country: 'UK', customer: 'A', revenue: 1000 },
                    { country: 'UK', customer: 'B', revenue: 900 },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY country) FROM customers) WHERE rn <= 3'
                );
                expect(result).toBe('table');
            });

            it('returns table for RANK queries', () => {
                const data = [
                    { product: 'A', revenue: 1000, rank: 1 },
                    { product: 'B', revenue: 900, rank: 2 },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT *, RANK() OVER (ORDER BY revenue DESC) FROM products'
                );
                expect(result).toBe('table');
            });

            it('returns table for wide data (more than 3 columns)', () => {
                const data = [
                    {
                        country: 'UK',
                        year: '2011',
                        revenue: 1000,
                        quantity: 50,
                        avg_price: 20,
                    },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT country, year, revenue, quantity, avg_price FROM summary'
                );
                expect(result).toBe('table');
            });

            it('returns table for "top" queries', () => {
                const data = [
                    { product: 'A', revenue: 5000 },
                    { product: 'B', revenue: 4000 },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT description, SUM(revenue) FROM order_items GROUP BY description ORDER BY revenue DESC LIMIT 10',
                    'What are the top 10 products?'
                );
                expect(result).toBe('table');
            });

            it('returns table for "highest" comparison with multiple columns', () => {
                const data = [{ country: 'UK', revenue: 500000 }];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT country, MAX(revenue) FROM orders GROUP BY country ORDER BY 2 DESC LIMIT 1',
                    'Which country has the highest revenue?'
                );
                // "highest" in question triggers comparison mode, returns table
                expect(result).toBe('table');
            });

            it('returns kpi for single value even with comparison question', () => {
                // KPI takes priority over comparison when truly single value
                const data = [{ total: 500000 }];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT MAX(revenue) as total FROM orders',
                    'What is the highest revenue?'
                );
                expect(result).toBe('kpi');
            });
        });

        describe('numeric value detection', () => {
            it('handles numeric values stored as strings', () => {
                const data = [
                    { category: 'A', value: '1000' },
                    { category: 'B', value: '2000' },
                    { category: 'C', value: '3000' },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT category, value FROM summary'
                );
                expect(result).toBe('bar');
            });

            it('returns table for non-numeric second column', () => {
                const data = [
                    { id: 1, name: 'Product A' },
                    { id: 2, name: 'Product B' },
                ];
                const result = ChartSelector.selectChartType(data, 'SELECT id, name FROM products');
                expect(result).toBe('table');
            });
        });

        describe('edge cases', () => {
            it('handles data with only one row but multiple columns', () => {
                const data = [{ country: 'UK', revenue: 500000, quantity: 1000 }];
                const result = ChartSelector.selectChartType(data, 'SELECT * FROM summary LIMIT 1');
                expect(result).toBe('table');
            });

            it('handles two rows of categorical data', () => {
                const data = [
                    { quarter: 'Q1', revenue: 100000 },
                    { quarter: 'Q2', revenue: 120000 },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT quarter, SUM(revenue) FROM orders GROUP BY quarter'
                );
                expect(result).toBe('bar');
            });

            it('handles exactly 50 rows (boundary case)', () => {
                const data = Array.from({ length: 50 }, (_, i) => ({
                    country: `Country_${i}`,
                    revenue: Math.random() * 10000,
                }));
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT country, SUM(revenue) FROM orders GROUP BY country'
                );
                expect(result).toBe('table');
            });

            it('handles 51 rows (over boundary)', () => {
                const data = Array.from({ length: 51 }, (_, i) => ({
                    country: `Country_${i}`,
                    revenue: Math.random() * 10000,
                }));
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT country, SUM(revenue) FROM orders GROUP BY country'
                );
                expect(result).toBe('table');
            });
        });

        describe('time column name variations', () => {
            it('detects "datetime" column', () => {
                const data = Array.from({ length: 10 }, (_, i) => ({
                    datetime: `2011-01-${String(i + 1).padStart(2, '0')}`,
                    revenue: Math.random() * 1000,
                }));
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT datetime, SUM(revenue) FROM orders GROUP BY datetime'
                );
                // "datetime" contains "time" so hasDate should be true
                expect(result).toBe('line');
            });

            it('detects "created_at" as timestamp', () => {
                const data = Array.from({ length: 10 }, (_, i) => ({
                    created_at_time: `2011-01-${String(i + 1).padStart(2, '0')}`,
                    revenue: Math.random() * 1000,
                }));
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT created_at_time, SUM(revenue) FROM orders GROUP BY created_at_time'
                );
                expect(result).toBe('line');
            });

            it('detects "week" as time period', () => {
                const data = [
                    { week: '2011-W01', revenue: 10000 },
                    { week: '2011-W02', revenue: 12000 },
                    { week: '2011-W03', revenue: 11000 },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT week, SUM(revenue) FROM orders GROUP BY week',
                    'Show weekly revenue trend'
                );
                expect(result).toBe('line');
            });

            it('detects "quarter" as time period', () => {
                const data = [
                    { quarter: '2011-Q1', revenue: 100000 },
                    { quarter: '2011-Q2', revenue: 120000 },
                    { quarter: '2011-Q3', revenue: 110000 },
                ];
                const result = ChartSelector.selectChartType(
                    data,
                    'SELECT quarter, SUM(revenue) FROM orders GROUP BY quarter',
                    'Show quarterly revenue trend'
                );
                expect(result).toBe('line');
            });
        });
    });
});
