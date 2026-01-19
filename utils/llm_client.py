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
    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = MODEL
        self.conversation_history = []

    def generate_sql(self, question: str, context: str = "") -> dict:
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
            sql = sql.replace('```sql', '').replace('```', '').strip()

            match = re.search(r'(?i)(WITH\s+.*|SELECT\s+.*)', sql, re.DOTALL)
            if match:
                sql = match.group(1)

            return {"sql": sql}

        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    def generate_insight(self, question: str, results_df, sql: str) -> str:
        if len(results_df) <= 50:
            results_preview = results_df.to_string(index=False)
            data_note = f"Complete results ({len(results_df)} rows):"
        else:
            results_preview = results_df.head(20).to_string(index=False)
            data_note = f"First 20 of {len(results_df)} rows:"

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
        self.conversation_history.append({"question": question, "sql": sql})
        if len(self.conversation_history) > 3:
            self.conversation_history.pop(0)

    def get_context(self) -> str:
        if not self.conversation_history:
            return ""

        context_parts = [f"Q: {item['question']}\nSQL: {item['sql']}" for item in self.conversation_history]
        return "\n\n".join(context_parts)
