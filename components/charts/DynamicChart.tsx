'use client';

import {
    LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    AreaChart, Area, PieChart, Pie, Cell
} from 'recharts';
import { Card, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

interface DynamicChartProps {
    type: 'line' | 'bar' | 'area' | 'pie' | 'table' | 'kpi';
    data: any[];
    horizontal?: boolean;
    height?: number;
}

const COLORS = ['#f59e0b', '#fbbf24', '#d97706', '#b45309', '#92400e', '#78350f'];

function formatValue(val: unknown): string {
    if (typeof val === 'number') {
        if (val > 1000000) return `${(val / 1000000).toFixed(1)}M`;
        if (val > 1000) return `${(val / 1000).toFixed(1)}K`;
        return val.toLocaleString(undefined, { maximumFractionDigits: 2 });
    }
    return String(val ?? '');
}

interface TooltipPayloadItem {
    name: string;
    value: unknown;
}

interface CustomTooltipProps {
    active?: boolean;
    payload?: TooltipPayloadItem[];
    label?: string;
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps): React.ReactElement | null {
    if (!active || !payload || payload.length === 0) return null;

    return (
        <div className="bg-[#0a0f18] border border-amber-500/20 p-3 rounded-xl shadow-2xl backdrop-blur-md">
            <p className="text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-1">{label}</p>
            {payload.map((entry, i) => (
                <p key={i} className="text-[0.85rem] font-medium text-slate-200">
                    {entry.name}: <span className="accent-gradient font-bold">{formatValue(entry.value)}</span>
                </p>
            ))}
        </div>
    );
}

function renderLineChart(data: any[], xAxisKey: string, dataKeys: string[]): React.ReactElement {
    return (
        <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey={xAxisKey} stroke="#64748b" fontSize={11} tickMargin={10} />
            <YAxis stroke="#64748b" fontSize={11} tickFormatter={formatValue} />
            <Tooltip content={<CustomTooltip />} />
            {dataKeys.map((key, i) => (
                <Line key={key} type="monotone" dataKey={key} stroke={COLORS[i % COLORS.length]} strokeWidth={3} dot={{ r: 4, fill: COLORS[i % COLORS.length] }} activeDot={{ r: 6 }} />
            ))}
        </LineChart>
    );
}

function renderAreaChart(data: any[], xAxisKey: string, dataKeys: string[]): React.ReactElement {
    return (
        <AreaChart data={data}>
            <defs>
                <linearGradient id="colorArea" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey={xAxisKey} stroke="#64748b" fontSize={11} tickMargin={10} />
            <YAxis stroke="#64748b" fontSize={11} tickFormatter={formatValue} />
            <Tooltip content={<CustomTooltip />} />
            {dataKeys.map((key, i) => (
                <Area key={key} type="monotone" dataKey={key} stroke={COLORS[i % COLORS.length]} fillOpacity={1} fill="url(#colorArea)" strokeWidth={3} />
            ))}
        </AreaChart>
    );
}

function renderBarChart(data: any[], xAxisKey: string, dataKeys: string[], horizontal: boolean): React.ReactElement {
    return (
        <BarChart data={data} layout={horizontal ? 'vertical' : 'horizontal'}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            {horizontal ? (
                <>
                    <XAxis type="number" stroke="#64748b" fontSize={11} tickFormatter={formatValue} />
                    <YAxis dataKey={xAxisKey} type="category" stroke="#64748b" fontSize={11} width={100} />
                </>
            ) : (
                <>
                    <XAxis dataKey={xAxisKey} stroke="#64748b" fontSize={11} />
                    <YAxis stroke="#64748b" fontSize={11} tickFormatter={formatValue} />
                </>
            )}
            <Tooltip content={<CustomTooltip />} />
            {dataKeys.map((key, i) => (
                <Bar key={key} dataKey={key} fill={COLORS[i % COLORS.length]} radius={horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0]} barSize={20} />
            ))}
        </BarChart>
    );
}

function renderPieChart(data: any[], keys: string[]): React.ReactElement {
    return (
        <PieChart>
            <Pie
                data={data}
                dataKey={keys[1]}
                nameKey={keys[0]}
                cx="50%" cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                stroke="none"
            >
                {data.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
        </PieChart>
    );
}

export function DynamicChart({ type, data, horizontal = false, height = 350 }: DynamicChartProps): React.ReactElement {
    if (!data || data.length === 0) {
        return (
            <div className="flex items-center justify-center p-8 bg-slate-950/50 rounded-2xl border border-white/5 font-mono text-[0.7rem] text-slate-500 uppercase tracking-widest">
                // NO_DATA_AVAILABLE
            </div>
        );
    }

    const keys = Object.keys(data[0]);
    const xAxisKey = keys[0];
    const dataKeys = keys.slice(1);

    if (type === 'kpi') {
        const value = data[0][keys[0]];
        return (
            <Card className="glass-card border-none rounded-2xl overflow-hidden relative">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-amber-500" />
                <CardContent className="pt-6 text-center">
                    <div className="text-3xl font-bold accent-gradient">{formatValue(value)}</div>
                    <div className="text-[0.65rem] font-bold text-slate-500 uppercase tracking-widest mt-2">{keys[0]}</div>
                </CardContent>
            </Card>
        );
    }

    if (type === 'table') {
        return (
            <div className="border border-white/5 rounded-2xl overflow-hidden bg-slate-950/50">
                <Table>
                    <TableHeader className="bg-slate-900/50">
                        <TableRow className="border-white/5">
                            {keys.map(k => <TableHead key={k} className="font-mono text-[0.65rem] text-amber-500 uppercase tracking-widest">{k}</TableHead>)}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {data.map((row, i) => (
                            <TableRow key={i} className="border-white/5 hover:bg-white/5 transition-colors">
                                {keys.map((k) => (
                                    <TableCell key={k} className="text-[0.8rem] text-slate-400 font-mono">
                                        {formatValue(row[k])}
                                    </TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        );
    }

    function renderChart(): React.ReactElement {
        switch (type) {
            case 'line':
                return renderLineChart(data, xAxisKey, dataKeys);
            case 'area':
                return renderAreaChart(data, xAxisKey, dataKeys);
            case 'bar':
                return renderBarChart(data, xAxisKey, dataKeys, horizontal);
            case 'pie':
                return renderPieChart(data, keys);
            default:
                return renderBarChart(data, xAxisKey, dataKeys, false);
        }
    }

    return (
        <ResponsiveContainer width="100%" height={height}>
            {renderChart()}
        </ResponsiveContainer>
    );
}
