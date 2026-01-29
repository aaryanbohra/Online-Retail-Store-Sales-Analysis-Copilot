import { describe, it, expect } from 'vitest';
import { SQLValidator } from '@/lib/sql-validator';

describe('SQLValidator', () => {
    describe('isSafe', () => {
        describe('valid SELECT queries', () => {
            it('allows simple SELECT query', () => {
                const result = SQLValidator.isSafe('SELECT * FROM orders');
                expect(result.isSafe).toBe(true);
            });

            it('allows SELECT with JOIN', () => {
                const result = SQLValidator.isSafe(
                    'SELECT o.invoice_id, oi.revenue FROM orders o JOIN order_items oi ON o.invoice_id = oi.invoice_id'
                );
                expect(result.isSafe).toBe(true);
            });

            it('allows SELECT with aggregations', () => {
                const result = SQLValidator.isSafe(
                    'SELECT country, SUM(revenue) FROM order_items GROUP BY country'
                );
                expect(result.isSafe).toBe(true);
            });

            it('allows SELECT with window functions', () => {
                const result = SQLValidator.isSafe(
                    'SELECT *, ROW_NUMBER() OVER (PARTITION BY country ORDER BY revenue DESC) as rn FROM orders'
                );
                expect(result.isSafe).toBe(true);
            });

            it('allows WITH (CTE) queries', () => {
                const result = SQLValidator.isSafe(
                    'WITH monthly AS (SELECT country, SUM(revenue) as total FROM orders GROUP BY country) SELECT * FROM monthly'
                );
                expect(result.isSafe).toBe(true);
            });

            it('allows SELECT with subqueries', () => {
                const result = SQLValidator.isSafe(
                    'SELECT * FROM (SELECT country, SUM(revenue) FROM orders GROUP BY country) sub WHERE total > 1000'
                );
                expect(result.isSafe).toBe(true);
            });

            it('allows SELECT with LIMIT', () => {
                const result = SQLValidator.isSafe('SELECT * FROM orders LIMIT 10');
                expect(result.isSafe).toBe(true);
            });

            it('allows SELECT with ORDER BY', () => {
                const result = SQLValidator.isSafe('SELECT * FROM orders ORDER BY invoice_date DESC');
                expect(result.isSafe).toBe(true);
            });

            it('allows query with trailing semicolon', () => {
                const result = SQLValidator.isSafe('SELECT * FROM orders;');
                expect(result.isSafe).toBe(true);
            });
        });

        describe('forbidden keywords', () => {
            it('blocks DROP statements (rejected as non-SELECT)', () => {
                const result = SQLValidator.isSafe('DROP TABLE orders');
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Only SELECT');
            });

            it('blocks DELETE statements (rejected as non-SELECT)', () => {
                const result = SQLValidator.isSafe('DELETE FROM orders WHERE 1=1');
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Only SELECT');
            });

            it('blocks UPDATE statements (rejected as non-SELECT)', () => {
                const result = SQLValidator.isSafe("UPDATE orders SET country = 'hacked'");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Only SELECT');
            });

            it('blocks INSERT statements (rejected as non-SELECT)', () => {
                const result = SQLValidator.isSafe("INSERT INTO orders VALUES ('test')");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Only SELECT');
            });

            it('blocks ALTER statements (rejected as non-SELECT)', () => {
                const result = SQLValidator.isSafe('ALTER TABLE orders ADD COLUMN hack TEXT');
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Only SELECT');
            });

            it('blocks TRUNCATE statements (rejected as non-SELECT)', () => {
                const result = SQLValidator.isSafe('TRUNCATE TABLE orders');
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Only SELECT');
            });

            it('blocks CREATE statements (rejected as non-SELECT)', () => {
                const result = SQLValidator.isSafe('CREATE TABLE hack (id INT)');
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Only SELECT');
            });

            it('blocks REPLACE statements (rejected as non-SELECT)', () => {
                const result = SQLValidator.isSafe("REPLACE INTO orders VALUES ('test')");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Only SELECT');
            });

            it('blocks DROP keyword embedded in SELECT subquery', () => {
                // Test that forbidden keywords are caught even in valid-looking SELECTs
                const result = SQLValidator.isSafe("SELECT * FROM (DROP TABLE orders) x");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Forbidden keyword');
            });

            it('blocks DELETE keyword embedded in SELECT', () => {
                const result = SQLValidator.isSafe("SELECT DELETE FROM orders");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Forbidden keyword');
            });
        });

        describe('SQL injection patterns', () => {
            it('blocks EXEC commands', () => {
                const result = SQLValidator.isSafe("SELECT * FROM orders; EXEC sp_executesql 'DROP'");
                expect(result.isSafe).toBe(false);
            });

            it('blocks xp_ stored procedures', () => {
                const result = SQLValidator.isSafe("SELECT * FROM orders WHERE xp_cmdshell('dir')");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('dangerous');
            });

            it('blocks sp_ stored procedures', () => {
                const result = SQLValidator.isSafe("SELECT sp_executesql FROM orders");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('dangerous');
            });

            it('blocks INTO OUTFILE', () => {
                const result = SQLValidator.isSafe("SELECT * FROM orders INTO OUTFILE '/tmp/hack.txt'");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('dangerous');
            });

            it('blocks INTO DUMPFILE', () => {
                const result = SQLValidator.isSafe("SELECT * FROM orders INTO DUMPFILE '/tmp/hack.bin'");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('dangerous');
            });

            it('blocks LOAD_FILE', () => {
                const result = SQLValidator.isSafe("SELECT LOAD_FILE('/etc/passwd') FROM orders");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('dangerous');
            });

            it('blocks UNION SELECT injection', () => {
                const result = SQLValidator.isSafe(
                    "SELECT * FROM orders WHERE id = 1 UNION SELECT * FROM customers"
                );
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('dangerous');
            });

            it('blocks SLEEP() time-based injection', () => {
                const result = SQLValidator.isSafe("SELECT * FROM orders WHERE SLEEP(10)");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('dangerous');
            });

            it('blocks BENCHMARK() time-based injection', () => {
                const result = SQLValidator.isSafe("SELECT BENCHMARK(10000000, SHA1('test')) FROM orders");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('dangerous');
            });

            it('blocks WAITFOR delay attacks', () => {
                const result = SQLValidator.isSafe("SELECT * FROM orders; WAITFOR DELAY '00:00:10'");
                expect(result.isSafe).toBe(false);
            });

            it('blocks pg_sleep for PostgreSQL', () => {
                const result = SQLValidator.isSafe("SELECT pg_sleep(10) FROM orders");
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('dangerous');
            });

            it('blocks ATTACH database attacks', () => {
                const result = SQLValidator.isSafe("ATTACH DATABASE '/tmp/hack.db' AS hack");
                expect(result.isSafe).toBe(false);
            });

            it('blocks DETACH database attacks', () => {
                const result = SQLValidator.isSafe('DETACH DATABASE main');
                expect(result.isSafe).toBe(false);
            });
        });

        describe('multiple statements', () => {
            it('blocks stacked queries with forbidden keyword', () => {
                // Note: DROP is caught first by forbidden keyword check
                const result = SQLValidator.isSafe('SELECT * FROM orders; DROP TABLE orders');
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Forbidden keyword');
            });

            it('blocks stacked SELECT queries', () => {
                const result = SQLValidator.isSafe('SELECT * FROM orders; SELECT * FROM customers');
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Multiple SQL statements');
            });

            it('blocks stacked queries with newline', () => {
                const result = SQLValidator.isSafe('SELECT * FROM orders\n; SELECT * FROM customers');
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Multiple SQL statements');
            });

            it('allows single statement with trailing semicolons', () => {
                const result = SQLValidator.isSafe('SELECT * FROM orders;;;');
                expect(result.isSafe).toBe(true);
            });
        });

        describe('SQL comments', () => {
            it('blocks single-line comments --', () => {
                const result = SQLValidator.isSafe('SELECT * FROM orders -- this is a comment');
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('comments');
            });

            it('blocks multi-line comments /* */', () => {
                const result = SQLValidator.isSafe('SELECT /* hidden */ * FROM orders');
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('comments');
            });
        });

        describe('obfuscation prevention', () => {
            it('blocks hex-encoded values', () => {
                const result = SQLValidator.isSafe('SELECT * FROM orders WHERE name = 0x48656C6C6F');
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Hex-encoded');
            });

            it('blocks CHAR() function', () => {
                const result = SQLValidator.isSafe(
                    'SELECT * FROM orders WHERE name = CHAR(72) || CHAR(101)'
                );
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('CHAR()');
            });
        });

        describe('case insensitivity', () => {
            it('blocks keywords regardless of case', () => {
                const dropVariants = ['drop', 'DROP', 'Drop', 'dRoP'];
                dropVariants.forEach((drop) => {
                    const result = SQLValidator.isSafe(`${drop} TABLE orders`);
                    expect(result.isSafe).toBe(false);
                });
            });
        });

        describe('non-SELECT queries', () => {
            it('rejects queries not starting with SELECT or WITH', () => {
                const result = SQLValidator.isSafe('SHOW TABLES');
                expect(result.isSafe).toBe(false);
                expect(result.error).toContain('Only SELECT queries');
            });
        });
    });

    describe('addLimitIfNeeded', () => {
        it('adds LIMIT to simple SELECT', () => {
            const result = SQLValidator.addLimitIfNeeded('SELECT * FROM orders');
            expect(result).toContain('LIMIT 100');
        });

        it('does not add LIMIT if already present', () => {
            const result = SQLValidator.addLimitIfNeeded('SELECT * FROM orders LIMIT 10');
            expect(result).toBe('SELECT * FROM orders LIMIT 10');
            expect(result.match(/LIMIT/g)?.length).toBe(1);
        });

        it('does not add LIMIT to GROUP BY queries', () => {
            const result = SQLValidator.addLimitIfNeeded(
                'SELECT country, COUNT(*) FROM orders GROUP BY country'
            );
            expect(result).not.toContain('LIMIT');
        });

        it('does not add LIMIT to COUNT queries', () => {
            const result = SQLValidator.addLimitIfNeeded('SELECT COUNT(*) FROM orders');
            expect(result).not.toContain('LIMIT');
        });

        it('does not add LIMIT to SUM queries', () => {
            const result = SQLValidator.addLimitIfNeeded('SELECT SUM(revenue) FROM order_items');
            expect(result).not.toContain('LIMIT');
        });

        it('does not add LIMIT to AVG queries', () => {
            const result = SQLValidator.addLimitIfNeeded('SELECT AVG(unit_price) FROM order_items');
            expect(result).not.toContain('LIMIT');
        });

        it('does not add LIMIT to MAX/MIN queries', () => {
            const maxResult = SQLValidator.addLimitIfNeeded('SELECT MAX(revenue) FROM order_items');
            const minResult = SQLValidator.addLimitIfNeeded('SELECT MIN(revenue) FROM order_items');
            expect(maxResult).not.toContain('LIMIT');
            expect(minResult).not.toContain('LIMIT');
        });

        it('strips trailing semicolons before adding LIMIT', () => {
            const result = SQLValidator.addLimitIfNeeded('SELECT * FROM orders;');
            expect(result).toBe('SELECT * FROM orders LIMIT 100;');
        });
    });

    describe('validate', () => {
        it('returns valid for safe SELECT query', () => {
            const result = SQLValidator.validate('SELECT * FROM orders');
            expect(result.isValid).toBe(true);
            expect(result.error).toBe('');
            expect(result.sql).toContain('LIMIT 100');
        });

        it('returns invalid for unsafe query', () => {
            const result = SQLValidator.validate('DROP TABLE orders');
            expect(result.isValid).toBe(false);
            expect(result.error).toContain('Only SELECT');
        });

        it('preserves LIMIT from original query', () => {
            const result = SQLValidator.validate('SELECT * FROM orders LIMIT 5');
            expect(result.isValid).toBe(true);
            expect(result.sql).toBe('SELECT * FROM orders LIMIT 5');
        });

        it('validates and limits aggregated queries correctly', () => {
            const result = SQLValidator.validate('SELECT country, SUM(revenue) FROM orders GROUP BY country');
            expect(result.isValid).toBe(true);
            expect(result.sql).not.toContain('LIMIT');
        });
    });

    describe('edge cases', () => {
        it('handles empty string', () => {
            const result = SQLValidator.isSafe('');
            expect(result.isSafe).toBe(false);
        });

        it('handles whitespace-only string', () => {
            const result = SQLValidator.isSafe('   ');
            expect(result.isSafe).toBe(false);
        });

        it('handles query with leading/trailing whitespace', () => {
            const result = SQLValidator.isSafe('   SELECT * FROM orders   ');
            expect(result.isSafe).toBe(true);
        });

        it('handles very long queries', () => {
            const longQuery = `SELECT ${'a, '.repeat(1000)} FROM orders`;
            const result = SQLValidator.isSafe(longQuery);
            expect(result.isSafe).toBe(true);
        });

        it('handles special characters in string literals', () => {
            const result = SQLValidator.isSafe(
                "SELECT * FROM orders WHERE country = 'United Kingdom'"
            );
            expect(result.isSafe).toBe(true);
        });
    });
});
