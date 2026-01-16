"""SQL validation and safety checks"""

import re
from config import FORBIDDEN_KEYWORDS, DEFAULT_LIMIT

# Additional dangerous patterns to block
DANGEROUS_PATTERNS = [
    r'\bEXEC\b', r'\bEXECUTE\b',  # Stored procedure execution
    r'\bxp_\w+', r'\bsp_\w+',      # SQL Server system procedures
    r'\bINTO\s+OUTFILE\b',         # File writes
    r'\bINTO\s+DUMPFILE\b',        # File writes
    r'\bLOAD_FILE\b',              # File reads
    r'\bUNION\s+SELECT\b',         # UNION injection
    r'\bSLEEP\s*\(',               # Time-based injection
    r'\bBENCHMARK\s*\(',           # Time-based injection
    r'\bWAITFOR\b',                # SQL Server delay
    r'\bPG_SLEEP\b',               # PostgreSQL delay
    r'\bATTACH\b',                 # SQLite attach database
    r'\bDETACH\b',                 # SQLite detach database
]

class SQLValidator:
    """Validates SQL queries for safety and correctness"""

    @staticmethod
    def is_safe(sql: str) -> tuple[bool, str]:
        """Check if SQL query is safe to execute"""
        sql_upper = sql.upper()
        sql_stripped = sql.strip()

        # Security: Must start with SELECT or WITH (for CTEs)
        if not (sql_stripped.upper().startswith('SELECT') or
                sql_stripped.upper().startswith('WITH')):
            return False, "Only SELECT queries are allowed"

        # Check for forbidden keywords
        for keyword in FORBIDDEN_KEYWORDS:
            # Use word boundary check to avoid false positives
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, sql_upper):
                return False, f"Forbidden keyword detected: {keyword}"

        # Check for dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, sql_upper):
                return False, f"Potentially dangerous SQL pattern detected"

        # Check for multiple statements (prevent stacked queries)
        # Allow semicolon only at the end
        sql_no_trailing = sql_stripped.rstrip(';')
        if ';' in sql_no_trailing:
            return False, "Multiple SQL statements not allowed"

        # Check for comments (can be used to bypass filters)
        if '--' in sql or '/*' in sql:
            return False, "SQL comments not allowed"

        # Check for hex-encoded strings (potential bypass)
        if re.search(r'0x[0-9a-fA-F]+', sql):
            return False, "Hex-encoded values not allowed"

        # Check for char() function (used to bypass string filters)
        if re.search(r'\bCHAR\s*\(', sql_upper):
            return False, "CHAR() function not allowed"

        return True, ""
    
    @staticmethod
    def add_limit_if_needed(sql: str) -> str:
        """Add LIMIT clause to non-aggregated queries"""
        sql_upper = sql.upper()
        
        if 'LIMIT' in sql_upper:
            return sql
        
        if any(keyword in sql_upper for keyword in ['GROUP BY', 'COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN(']):
            return sql
        
        sql = sql.rstrip(';')
        return f"{sql} LIMIT {DEFAULT_LIMIT};"
    
    @staticmethod
    def validate(sql: str) -> tuple[bool, str]:
        """Run all validation checks

        Args:
            sql: The SQL query to validate

        Returns:
            Tuple of (is_valid, result) where result is either error message or validated SQL
        """
        is_safe, error = SQLValidator.is_safe(sql)
        if not is_safe:
            return False, error

        sql = SQLValidator.add_limit_if_needed(sql)

        return True, sql