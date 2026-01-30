import fs from 'fs';
import path from 'path';

const COST_TRACKER_FILE = path.join(process.cwd(), '.cost-tracking.json');
const DAILY_LIMIT = 1.0; // $1 per day

// Claude Sonnet 4 pricing (per 1M tokens)
const PRICING = {
  input: 3.0,      // $3 per 1M input tokens
  output: 15.0,    // $15 per 1M output tokens
};

interface CostData {
  date: string;
  totalCost: number;
  requests: number;
}

function getTodayDate(): string {
  return new Date().toISOString().split('T')[0];
}

function getCostData(): CostData {
  try {
    if (fs.existsSync(COST_TRACKER_FILE)) {
      const data = JSON.parse(fs.readFileSync(COST_TRACKER_FILE, 'utf-8'));
      const today = getTodayDate();

      // Reset if it's a new day
      if (data.date !== today) {
        return { date: today, totalCost: 0, requests: 0 };
      }
      return data;
    }
  } catch (e) {
    console.error('Error reading cost tracker:', e);
  }

  return { date: getTodayDate(), totalCost: 0, requests: 0 };
}

function saveCostData(data: CostData): void {
  try {
    fs.writeFileSync(COST_TRACKER_FILE, JSON.stringify(data, null, 2));
  } catch (e) {
    console.error('Error saving cost tracker:', e);
  }
}

export function calculateRequestCost(inputTokens: number, outputTokens: number): number {
  const inputCost = (inputTokens / 1_000_000) * PRICING.input;
  const outputCost = (outputTokens / 1_000_000) * PRICING.output;
  return inputCost + outputCost;
}

export function checkCostLimit(): boolean {
  const data = getCostData();
  return data.totalCost < DAILY_LIMIT;
}

export function recordCost(inputTokens: number, outputTokens: number): void {
  const cost = calculateRequestCost(inputTokens, outputTokens);
  const data = getCostData();
  data.totalCost += cost;
  data.requests += 1;
  saveCostData(data);

  console.log(`Cost tracked: $${cost.toFixed(4)} | Daily total: $${data.totalCost.toFixed(2)}/$${DAILY_LIMIT}`);
}

export function getRemainingBudget(): number {
  const data = getCostData();
  return Math.max(0, DAILY_LIMIT - data.totalCost);
}

export function getCostSummary(): string {
  const data = getCostData();
  return `Today's usage: $${data.totalCost.toFixed(2)}/$${DAILY_LIMIT} (${data.requests} requests)`;
}
