import { DEFAULT_LIMIT, FORBIDDEN_KEYWORDS } from './constants';

const DANGEROUS_PATTERNS = [
    /\bEXEC\b/i, /\bEXECUTE\b/i,
    /\bxp_\w+/i, /\bsp_\w+/i,
    /\bINTO\s+OUTFILE\b/i,
    /\bINTO\s+DUMPFILE\b/i,
    /\bLOAD_FILE\b/i,
    /\bUNION\s+SELECT\b/i,
    /\bSLEEP\s*\(/i,
    /\bBENCHMARK\s*\(/i,
    /\bWAITFOR\b/i,
    /\bPG_SLEEP\b/i,
    /\bATTACH\b/i,
    /\bDETACH\b/i,
];

export class SQLValidator {
    static isSafe(sql: string): { isSafe: boolean; error: string } {
        const sqlUpper = sql.toUpperCase();
        const sqlStripped = sql.trim();

        if (!sqlStripped.toUpperCase().startsWith('SELECT') &&
            !sqlStripped.toUpperCase().startsWith('WITH')) {
            return { isSafe: false, error: "Only SELECT queries are allowed" };
        }

        for (const keyword of FORBIDDEN_KEYWORDS) {
            // Word boundary check
            const pattern = new RegExp(`\\b${keyword}\\b`, 'i');
            if (pattern.test(sqlUpper)) {
                return { isSafe: false, error: `Forbidden keyword detected: ${keyword}` };
            }
        }

        for (const pattern of DANGEROUS_PATTERNS) {
            if (pattern.test(sqlUpper)) {
                return { isSafe: false, error: "Potentially dangerous SQL pattern detected" };
            }
        }

        const sqlNoTrailing = sqlStripped.replace(/;+$/, '');
        if (sqlNoTrailing.includes(';')) {
            return { isSafe: false, error: "Multiple SQL statements not allowed" };
        }

        if (sql.includes('--') || sql.includes('/*')) {
            return { isSafe: false, error: "SQL comments not allowed" };
        }

        if (/0x[0-9a-fA-F]+/.test(sql)) {
            return { isSafe: false, error: "Hex-encoded values not allowed" };
        }

        if (/\bCHAR\s*\(/.test(sqlUpper)) {
            return { isSafe: false, error: "CHAR() function not allowed" };
        }

        return { isSafe: true, error: "" };
    }

    static addLimitIfNeeded(sql: string): string {
        const sqlUpper = sql.toUpperCase();

        if (sqlUpper.includes('LIMIT')) {
            return sql;
        }

        // Don't add limit if using aggregates that return few rows usually
        // But check if GROUP BY is present? The Python logic checks these:
        const aggregations = ['GROUP BY', 'COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN('];
        if (aggregations.some(keyword => sqlUpper.includes(keyword))) {
            return sql;
        }

        const cleanedSql = sql.trim().replace(/;+$/, '');
        return `${cleanedSql} LIMIT ${DEFAULT_LIMIT};`;
    }

    static validate(sql: string): { isValid: boolean; error: string; sql: string } {
        const { isSafe, error } = SQLValidator.isSafe(sql);
        if (!isSafe) {
            return { isValid: false, error, sql };
        }

        const newSql = SQLValidator.addLimitIfNeeded(sql);
        return { isValid: true, error: "", sql: newSql };
    }
}
