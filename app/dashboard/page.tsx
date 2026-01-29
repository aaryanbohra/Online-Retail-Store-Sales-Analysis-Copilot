'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DollarSign, ShoppingBag, Users, TrendingUp, Globe, Sparkles } from 'lucide-react';
import { DynamicChart } from '@/components/charts/DynamicChart';

export default function DashboardPage() {
    const [selectedYear, setSelectedYear] = useState<string>('all');
    const [selectedCountry, setSelectedCountry] = useState<string>('all');

    const { data: filters } = useQuery({
        queryKey: ['dashboard-filters'],
        queryFn: async () => {
            const res = await fetch('/api/dashboard/filters');
            if (!res.ok) throw new Error('Failed to fetch filters');
            return res.json();
        }
    });

    const { data, isLoading, error } = useQuery({
        queryKey: ['dashboard-data', selectedYear, selectedCountry],
        queryFn: async () => {
            const params = new URLSearchParams();
            if (selectedYear && selectedYear !== 'all') params.append('year', selectedYear);
            if (selectedCountry && selectedCountry !== 'all') params.append('country', selectedCountry);
            const res = await fetch(`/api/dashboard?${params.toString()}`);
            if (!res.ok) throw new Error('Failed to fetch dashboard data');
            return res.json();
        }
    });

    if (error) return <div className="p-8 text-red-500 font-mono">// ERROR: {error.message}</div>;

    const kpis = data?.kpis || {};
    const charts = data?.charts || {};
    const custStats = charts.customerStats || {};

    const formatCurrency = (val: number) =>
        new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 }).format(val);

    const formatNumber = (val: number) =>
        new Intl.NumberFormat('en-US').format(val);

    return (
        <div className="space-y-8 animate-fade-in-up pb-10">
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6">
                <div>
                    <h1 className="text-4xl font-extrabold tracking-tight text-white mb-2">Sales Dashboard</h1>
                    <p className="text-slate-400 font-medium">Real-time business intelligence for Online Retail.</p>
                </div>

                <div className="flex flex-wrap gap-3 bg-slate-950/50 p-2 rounded-2xl border border-white/5 backdrop-blur-md">
                    <Select value={selectedYear} onValueChange={setSelectedYear}>
                        <SelectTrigger className="w-[140px] bg-slate-900/50 border-white/10 text-white rounded-xl focus:ring-amber-500/50">
                            <SelectValue placeholder="All Years" />
                        </SelectTrigger>
                        <SelectContent className="bg-[#0a0f18] border-white/10 text-white">
                            <SelectItem value="all">All Years</SelectItem>
                            {filters?.years?.map((y: string) => (
                                <SelectItem key={y} value={y}>{y}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>

                    <Select value={selectedCountry} onValueChange={setSelectedCountry}>
                        <SelectTrigger className="w-[180px] bg-slate-900/50 border-white/10 text-white rounded-xl focus:ring-amber-500/50">
                            <SelectValue placeholder="All Countries" />
                        </SelectTrigger>
                        <SelectContent className="bg-[#0a0f18] border-white/10 text-white">
                            <SelectItem value="all">All Countries</SelectItem>
                            {filters?.countries?.map((c: string) => (
                                <SelectItem key={c} value={c}>{c}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {isLoading ? (
                <div className="flex flex-col items-center justify-center h-96 text-slate-400 font-mono space-y-4">
                    <div className="w-12 h-12 border-4 border-amber-500/20 border-t-amber-500 rounded-full animate-spin" />
                    <span>// FETCHING_ANALYTICS_DATA...</span>
                </div>
            ) : (
                <>
                    {/* KPI Cards */}
                    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-5">
                        {[
                            { label: 'Total Revenue', value: formatCurrency(Number(kpis.total_revenue || 0)), icon: <DollarSign size={18} /> },
                            { label: 'Orders', value: formatNumber(Number(kpis.total_orders || 0)), icon: <ShoppingBag size={18} /> },
                            { label: 'Customers', value: formatNumber(Number(kpis.total_customers || 0)), icon: <Users size={18} /> },
                            { label: 'Avg Order Value', value: `£${Number(kpis.avg_order_value || 0).toFixed(2)}`, icon: <TrendingUp size={18} /> },
                            { label: 'Countries', value: kpis.total_countries || 0, icon: <Globe size={18} /> },
                        ].map((kpi, i) => (
                            <Card key={i} className="glass-card p-5 rounded-2xl relative group overflow-hidden border-none hover:translate-y-[-4px] transition-all duration-300">
                                <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-amber-400 to-amber-600" />
                                <div className="flex items-center justify-between mb-3 text-slate-500">
                                    <span className="font-mono text-[0.6rem] font-bold uppercase tracking-widest">{kpi.label}</span>
                                    <div className="text-amber-500/80 group-hover:text-amber-400 transition-colors">{kpi.icon}</div>
                                </div>
                                <div className="text-2xl font-bold accent-gradient tracking-tight">{kpi.value}</div>
                            </Card>
                        ))}
                    </div>

                    <Tabs defaultValue="revenue" className="space-y-8 mt-10">
                        <TabsList className="bg-slate-950/50 p-1 rounded-2xl border border-white/5 inline-flex backdrop-blur-md">
                            <TabsTrigger value="revenue" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-amber-500 data-[state=active]:text-[#0a0f18] font-bold tracking-tight transition-all text-slate-400 text-sm">Revenue Trends</TabsTrigger>
                            <TabsTrigger value="geographic" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-amber-500 data-[state=active]:text-[#0a0f18] font-bold tracking-tight transition-all text-slate-400 text-sm">Geographic</TabsTrigger>
                            <TabsTrigger value="products" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-amber-500 data-[state=active]:text-[#0a0f18] font-bold tracking-tight transition-all text-slate-400 text-sm">Products</TabsTrigger>
                            <TabsTrigger value="customers" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-amber-500 data-[state=active]:text-[#0a0f18] font-bold tracking-tight transition-all text-slate-400 text-sm">Customers</TabsTrigger>
                        </TabsList>

                        {/* Revenue Trends Tab */}
                        <TabsContent value="revenue" className="space-y-6">
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <Card className="glass-card p-6 border-none rounded-3xl lg:col-span-2">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Monthly Revenue Trend</h3>
                                    <DynamicChart type="area" data={charts.revenueTrend?.map((d: any) => ({ ...d, revenue: Number(d.revenue) }))} height={350} />
                                </Card>
                                <Card className="glass-card p-6 border-none rounded-3xl">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Revenue by Day of Week</h3>
                                    <DynamicChart type="bar" data={charts.revenueByDay?.map((d: any) => ({ Day: d.day_name.trim(), Revenue: Number(d.revenue) }))} height={300} />
                                </Card>
                                <Card className="glass-card p-6 border-none rounded-3xl">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Hourly Performance</h3>
                                    <DynamicChart type="line" data={charts.revenueByHour?.map((h: any) => ({ Hour: `${h.hour}:00`, Revenue: Number(h.revenue) }))} height={300} />
                                </Card>
                            </div>
                        </TabsContent>

                        {/* Geographic Tab */}
                        <TabsContent value="geographic" className="space-y-6">
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                                <Card className="glass-card p-6 border-none rounded-3xl lg:col-span-2">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Revenue by Country</h3>
                                    <DynamicChart type="bar" data={charts.countryRevenue?.map((c: any) => ({ Country: c.country, Revenue: Number(c.revenue) }))} horizontal height={400} />
                                </Card>
                                <Card className="glass-card p-6 border-none rounded-3xl">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Revenue Distribution</h3>
                                    <DynamicChart type="pie" data={charts.countryRevenue?.map((c: any) => ({ name: c.country, value: Number(c.revenue) }))} height={400} />
                                </Card>
                                <Card className="glass-card p-0 border-none rounded-3xl lg:col-span-3 overflow-hidden">
                                    <div className="p-6 pb-2">
                                        <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest pl-4 border-l-2 border-amber-500">Geographic Drilldown</h3>
                                    </div>
                                    <DynamicChart type="table" data={charts.countryRevenue?.map((c: any) => ({
                                        Country: c.country,
                                        Revenue: `£${Number(c.revenue).toLocaleString()}`,
                                        Orders: c.orders,
                                        Customers: c.customers,
                                        'Avg/Order': `£${(Number(c.revenue) / c.orders).toFixed(2)}`
                                    }))} />
                                </Card>
                            </div>
                        </TabsContent>

                        {/* Products Tab */}
                        <TabsContent value="products" className="space-y-6">
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <Card className="glass-card p-6 border-none rounded-3xl">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Top Products by Revenue</h3>
                                    <DynamicChart type="bar" data={charts.topProducts?.slice(0, 10).map((p: any) => ({ Product: p.description, Revenue: Number(p.revenue) }))} horizontal height={400} />
                                </Card>
                                <Card className="glass-card p-6 border-none rounded-3xl">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Top Products by Quantity</h3>
                                    <DynamicChart type="bar" data={charts.topProducts?.sort((a: any, b: any) => b.quantity - a.quantity).slice(0, 10).map((p: any) => ({ Product: p.description, Qty: p.quantity }))} horizontal height={400} />
                                </Card>
                                <Card className="glass-card p-6 border-none rounded-3xl">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Revenue by Price Tier</h3>
                                    <DynamicChart type="bar" data={charts.priceTiers?.map((t: any) => ({ Tier: t.tier, Revenue: Number(t.revenue) }))} height={300} />
                                </Card>
                                <Card className="glass-card p-6 border-none rounded-3xl">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Units Sold by Tier</h3>
                                    <DynamicChart type="pie" data={charts.priceTiers?.map((t: any) => ({ name: t.tier, value: Number(t.units_sold) }))} height={300} />
                                </Card>
                            </div>
                        </TabsContent>

                        {/* Customers Tab */}
                        <TabsContent value="customers" className="space-y-6">
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <Card className="glass-card p-6 border-none rounded-3xl">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Top Customers (Revenue)</h3>
                                    <DynamicChart type="bar" data={charts.topCustomers?.map((c: any) => ({ Customer: `ID ${c.customer_id}`, Revenue: Number(c.revenue) }))} horizontal height={400} />
                                </Card>
                                <Card className="glass-card p-6 border-none rounded-3xl">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Order Frequency</h3>
                                    <DynamicChart type="pie" data={custStats.frequency?.map((f: any) => ({ name: f.freq_group, value: Number(f.count) }))} height={400} />
                                </Card>
                                <Card className="glass-card p-6 border-none rounded-3xl">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Value Segments (Customers)</h3>
                                    <DynamicChart type="bar" data={custStats.segments?.map((s: any) => ({ Segment: s.segment, Customers: s.customers }))} height={300} />
                                </Card>
                                <Card className="glass-card p-6 border-none rounded-3xl">
                                    <h3 className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest mb-6 pl-4 border-l-2 border-amber-500">Revenue by Segment</h3>
                                    <DynamicChart type="pie" data={custStats.segments?.map((s: any) => ({ name: s.segment, value: Number(s.total_revenue) }))} height={300} />
                                </Card>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
                                <Card className="glass-card p-6 border-none rounded-3xl text-center relative overflow-hidden">
                                    <Sparkles className="absolute top-2 right-2 text-amber-500/10 w-12 h-12" />
                                    <div className="text-[0.6rem] font-bold text-slate-500 uppercase tracking-[0.2em] mb-2">Average CLV</div>
                                    <div className="text-3xl font-extrabold accent-gradient tracking-tight">£{Number(custStats.avg_clv || 0).toLocaleString()}</div>
                                </Card>
                                <Card className="glass-card p-6 border-none rounded-3xl text-center relative overflow-hidden">
                                    <Users className="absolute top-2 right-2 text-amber-500/10 w-12 h-12" />
                                    <div className="text-[0.6rem] font-bold text-slate-500 uppercase tracking-[0.2em] mb-2">Median CLV</div>
                                    <div className="text-3xl font-extrabold accent-gradient tracking-tight">£{Number(custStats.median_clv || 0).toLocaleString()}</div>
                                </Card>
                                <Card className="glass-card p-6 border-none rounded-3xl text-center relative overflow-hidden">
                                    <TrendingUp className="absolute top-2 right-2 text-amber-500/10 w-12 h-12" />
                                    <div className="text-[0.6rem] font-bold text-slate-500 uppercase tracking-[0.2em] mb-2">Repeat Purchase Rate</div>
                                    <div className="text-3xl font-extrabold accent-gradient tracking-tight">{(Number(custStats.repeat_rate || 0) * 100).toFixed(1)}%</div>
                                </Card>
                            </div>
                        </TabsContent>
                    </Tabs>
                </>
            )}
        </div>
    );
}
