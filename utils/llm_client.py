"""Wrapper for Anthropic API interactions"""

import re
from anthropic import Anthropic
from config import (
    ANTHROPIC_API_KEY,
    MODEL,
    MAX_TOKENS,
    SQL_SYSTEM_PROMPT,
    INSIGHT_SYSTEM_PROMPT,
    SCHEMA,
)


class LLMClient:
    """Handles all interactions with Anthropic API"""

    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = MODEL
        self.conversation_history = []
    
    def generate_sql(self, question: str, context: str = "") -> dict:
        """
        Generate SQL query from natural language question
        
        Args:
            question: User's question in natural language
            context: Optional context from previous queries
            
        Returns:
            Dict with 'sql' and optional 'reasoning' keys
        """
        
        system_prompt = SQL_SYSTEM_PROMPT.format(schema=SCHEMA)

        user_message = question
        if context:
            user_message = f"Previous context: {context}\n\nNew question: {question}"

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            sql = "".join(block.text for block in response.content if getattr(block, "text", None))
            
            # Clean up any markdown formatting
            sql = sql.replace('```sql', '').replace('```', '').strip()
            
            # Remove common conversational prefixes if present (e.g. "sqlite", "sql", "Here is the query:")
            # Regex to find SQL starting with WITH (CTE) or SELECT (case insensitive)
            match = re.search(r'(?i)(WITH\s+.*|SELECT\s+.*)', sql, re.DOTALL)
            if match:
                sql = match.group(1)
            
            result = {"sql": sql}
            
            return result
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def generate_insight(self, question: str, results_df, sql: str) -> str:
        """
        Generate business insight from query results

        Args:
            question: Original user question
            results_df: Pandas DataFrame with query results
            sql: The SQL query that was executed

        Returns:
            Business insight text
        """

        # Send all data if small enough, otherwise summarize
        if len(results_df) <= 50:
            results_preview = results_df.to_string(index=False)
            data_note = f"Complete results ({len(results_df)} rows):"
        else:
            results_preview = results_df.head(20).to_string(index=False)
            data_note = f"First 20 of {len(results_df)} rows:"

            # Add summary statistics for numeric columns
            numeric_cols = results_df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                stats = results_df[numeric_cols].agg(['min', 'max', 'mean', 'sum']).to_string()
                results_preview += f"\n\nSummary statistics:\n{stats}"

        user_message = f"""
Question: {question}

SQL Query:
{sql}

{data_note}
{results_preview}

Provide a business insight based on these results.
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=INSIGHT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            return "".join(block.text for block in response.content if getattr(block, "text", None)).strip()
            
        except Exception as e:
            return f"Could not generate insight: {str(e)}"
    
    def add_to_history(self, question: str, sql: str):
        """Store conversation history for context"""
        self.conversation_history.append({
            "question": question,
            "sql": sql
        })
        
        # Keep only last 3 interactions
        if len(self.conversation_history) > 3:
            self.conversation_history.pop(0)
    
    def get_context(self) -> str:
        """Get formatted conversation history"""
        if not self.conversation_history:
            return ""
        
        context_parts = []
        for item in self.conversation_history:
            context_parts.append(f"Q: {item['question']}\nSQL: {item['sql']}")
        
        return "\n\n".join(context_parts)
