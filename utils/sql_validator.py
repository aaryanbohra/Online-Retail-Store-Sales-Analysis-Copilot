import re
from config import FORBIDDEN_KEYWORDS, DEFAULT_LIMIT

DANGEROUS_PATTERNS = [
    r'\bEXEC\b', r'\bEXECUTE\b',
    r'\bxp_\w+', r'\bsp_\w+',
    r'\bINTO\s+OUTFILE\b',
    r'\bINTO\s+DUMPFILE\b',
    r'\bLOAD_FILE\b',
    r'\bUNION\s+SELECT\b',
    r'\bSLEEP\s*\(',
    r'\bBENCHMARK\s*\(',
    r'\bWAITFOR\b',
    r'\bPG_SLEEP\b',
    r'\bATTACH\b',
    r'\bDETACH\b',
]


class SQLValidator:
    @staticmethod
    def is_safe(sql: str) -> tuple[bool, str]:
        sql_upper = sql.upper()
        sql_stripped = sql.strip()

        if not (sql_stripped.upper().startswith('SELECT') or
                sql_stripped.upper().startswith('WITH')):
            return False, "Only SELECT queries are allowed"

        for keyword in FORBIDDEN_KEYWORDS:
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, sql_upper):
                return False, f"Forbidden keyword detected: {keyword}"

        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, sql_upper):
                return False, "Potentially dangerous SQL pattern detected"

        sql_no_trailing = sql_stripped.rstrip(';')
        if ';' in sql_no_trailing:
            return False, "Multiple SQL statements not allowed"

        if '--' in sql or '/*' in sql:
            return False, "SQL comments not allowed"

        if re.search(r'0x[0-9a-fA-F]+', sql):
            return False, "Hex-encoded values not allowed"

        if re.search(r'\bCHAR\s*\(', sql_upper):
            return False, "CHAR() function not allowed"

        return True, ""

    @staticmethod
    def add_limit_if_needed(sql: str) -> str:
        sql_upper = sql.upper()

        if 'LIMIT' in sql_upper:
            return sql

        if any(keyword in sql_upper for keyword in ['GROUP BY', 'COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN(']):
            return sql

        sql = sql.rstrip(';')
        return f"{sql} LIMIT {DEFAULT_LIMIT};"

    @staticmethod
    def validate(sql: str) -> tuple[bool, str]:
        is_safe, error = SQLValidator.is_safe(sql)
        if not is_safe:
            return False, error

        sql = SQLValidator.add_limit_if_needed(sql)
        return True, sql
