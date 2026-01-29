import { MAX_ROWS_FOR_CHART } from './constants';

export type ChartType = 'kpi' | 'table' | 'line' | 'bar' | 'area' | 'pie';

const TREND_KEYWORDS = [
    'trend', 'over time', 'overtime', 'growth', 'change', 'evolution',
    'progression', 'trajectory', 'pattern over', 'how has', 'how did'
];

const TIME_PERIOD_KEYWORDS = ['month', 'year', 'week', 'quarter'];

const SQL_COMPARISON_KEYWORDS = [
    'row_number', 'rank', 'dense_rank', 'partition by', 'max(', 'min('
];

const QUESTION_COMPARISON_KEYWORDS = [
    'top ', 'top-', 'highest', 'lowest', 'best', 'worst',
    'most', 'least', 'biggest', 'smallest', 'largest'
];

function containsAny(text: string, keywords: string[]): boolean {
    return keywords.some(keyword => text.includes(keyword));
}

function isNumericValue(value: unknown): boolean {
    return typeof value === 'number' || !isNaN(Number(value));
}

function selectChartType(data: Record<string, unknown>[], sql: string, question: string = ""): ChartType {
    if (!data || data.length === 0) return 'table';

    const columns = Object.keys(data[0]);
    const rowCount = data.length;
    const colCount = columns.length;

    if (rowCount === 1 && colCount === 1) return 'kpi';
    if (rowCount > MAX_ROWS_FOR_CHART) return 'table';
    if (colCount > 3) return 'table';

    const questionLower = question.toLowerCase();
    const sqlLower = sql.toLowerCase();
    const colNamesStr = columns.map(c => c.toLowerCase()).join(' ');

    const hasDateColumn = (colNamesStr.includes('date') || colNamesStr.includes('time')) && !colNamesStr.includes('month');
    const hasTimePeriod = containsAny(colNamesStr, TIME_PERIOD_KEYWORDS);
    const userWantsTrend = containsAny(questionLower, TREND_KEYWORDS);

    if (userWantsTrend && (hasDateColumn || hasTimePeriod) && rowCount >= 2) {
        return 'line';
    }

    const isComparisonQuery = containsAny(sqlLower, SQL_COMPARISON_KEYWORDS) ||
        containsAny(questionLower, QUESTION_COMPARISON_KEYWORDS);

    if (isComparisonQuery) return 'table';

    if (colCount === 2 && rowCount <= 20 && isNumericValue(data[0][columns[1]])) {
        if (hasDateColumn && rowCount >= 7) return 'line';
        if (hasTimePeriod && rowCount >= 2) return 'bar';
        if (!hasTimePeriod && !hasDateColumn && rowCount >= 2 && rowCount <= 15) return 'bar';
    }

    return 'table';
}

export const ChartSelector = {
    selectChartType
};
