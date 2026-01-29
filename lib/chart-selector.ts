import { MAX_ROWS_FOR_CHART } from './constants';

export type ChartType = 'kpi' | 'table' | 'line' | 'bar' | 'area' | 'pie';

export class ChartSelector {
    static selectChartType(data: any[], sql: string, question: string = ""): ChartType {
        if (!data || data.length === 0) return 'table';

        const columns = Object.keys(data[0]);
        const rowCount = data.length;
        const colCount = columns.length;

        if (rowCount === 1 && colCount === 1) {
            return 'kpi';
        }

        if (rowCount > MAX_ROWS_FOR_CHART) {
            return 'table';
        }

        const questionLower = question.toLowerCase();
        const trendKeywords = ['trend', 'over time', 'overtime', 'growth', 'change', 'evolution',
            'progression', 'trajectory', 'pattern over', 'how has', 'how did'];
        const userWantsTrend = trendKeywords.some(keyword => questionLower.includes(keyword));

        const colNamesStr = columns.map(c => c.toLowerCase()).join(' ');
        // Simple heuristics for date columns
        const hasDate = (colNamesStr.includes('date') || colNamesStr.includes('time')) && !colNamesStr.includes('month');
        const hasTimePeriod = ['month', 'year', 'week', 'quarter'].some(word => colNamesStr.includes(word));

        if (userWantsTrend && (hasDate || hasTimePeriod) && rowCount >= 2) {
            return 'line';
        }

        const sqlLower = sql.toLowerCase();
        const sqlComparisonKeywords = [
            'row_number', 'rank', 'dense_rank', 'partition by',
            'max(', 'min('
        ];
        const questionComparisonKeywords = [
            'top ', 'top-', 'highest', 'lowest', 'best', 'worst',
            'most', 'least', 'biggest', 'smallest', 'largest'
        ];
        const isSqlComparison = sqlComparisonKeywords.some(keyword => sqlLower.includes(keyword));
        const isQuestionComparison = questionComparisonKeywords.some(keyword => questionLower.includes(keyword));

        if (isSqlComparison || isQuestionComparison) {
            return 'table';
        }

        if (colCount > 3) {
            return 'table';
        }

        if (colCount === 2 && rowCount <= 20) {
            // Check if second column is numeric (usually label, value)
            const secondColVal = data[0][columns[1]];
            const isNumeric = typeof secondColVal === 'number' || !isNaN(Number(secondColVal));

            if (isNumeric) {
                if (hasDate && rowCount >= 7) {
                    return 'line';
                }
                if (hasTimePeriod && rowCount >= 2) {
                    return 'bar';
                }
                if (!hasTimePeriod && !hasDate && rowCount >= 2 && rowCount <= 15) {
                    return 'bar';
                }
            }
        }

        return 'table';
    }
}
