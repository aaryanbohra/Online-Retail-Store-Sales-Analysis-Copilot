'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const PAGE_SIZE = 50;

export default function DatasetPage() {
    const [page, setPage] = useState(1);

    const { data, isLoading, error } = useQuery({
        queryKey: ['dataset', page],
        queryFn: async () => {
            const offset = (page - 1) * PAGE_SIZE;
            const res = await fetch(`/api/dataset?limit=${PAGE_SIZE}&offset=${offset}`);
            if (!res.ok) throw new Error('Failed to fetch dataset');
            return res.json();
        }
    });

    if (error) return <div className="p-8 text-red-500 font-mono">// ERROR: {error.message}</div>;

    const dataset = data?.data || [];
    const total = data?.total || 0;
    const totalPages = Math.ceil(total / PAGE_SIZE);

    return (
        <div className="space-y-8 animate-fade-in-up">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-extrabold tracking-tight text-white mb-2">Dataset Explorer</h1>
                    <p className="text-slate-400 font-medium font-mono text-sm leading-relaxed">
                        // BROWSING_RAW_TRANSACTIONS
                    </p>
                </div>
                <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl px-4 py-2 font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest hidden sm:block">
                    Total Records: {total.toLocaleString()}
                </div>
            </div>

            <Card className="glass-card border-none rounded-3xl overflow-hidden p-0 relative">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-amber-300 via-amber-500 to-amber-700 z-10" />

                <div className="overflow-x-auto">
                    <Table>
                        <TableHeader>
                            <TableRow className="bg-[#1e293b]/30 border-white/5 hover:bg-[#1e293b]/40">
                                <TableHead className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest h-14">Invoice</TableHead>
                                <TableHead className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest h-14">Date</TableHead>
                                <TableHead className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest h-14">Customer</TableHead>
                                <TableHead className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest h-14">Country</TableHead>
                                <TableHead className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest h-14">Product</TableHead>
                                <TableHead className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest h-14">Qty</TableHead>
                                <TableHead className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest h-14">Price</TableHead>
                                <TableHead className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest h-14 text-right pr-6">Revenue</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {isLoading ? (
                                Array.from({ length: 10 }).map((_, i) => (
                                    <TableRow key={i} className="border-white/5 animate-pulse">
                                        {Array.from({ length: 8 }).map((_, j) => (
                                            <TableCell key={j} className="h-12">
                                                <div className="h-2 bg-[#1e293b]/20 rounded w-full opacity-50" />
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                ))
                            ) : (
                                dataset.map((row: any, i: number) => (
                                    <TableRow key={i} className="group border-white/5 data-[state=selected]:bg-amber-500/5 hover:bg-amber-500/5 transition-colors">
                                        <TableCell className="font-mono text-[0.8rem] text-slate-400 group-hover:text-amber-500 transition-colors">{row.invoice_id}</TableCell>
                                        <TableCell className="text-[0.85rem] text-slate-400 whitespace-nowrap">{row.invoice_date?.split('T')[0]}</TableCell>
                                        <TableCell className="text-[0.85rem] text-slate-400 font-mono">{row.customer_id}</TableCell>
                                        <TableCell className="text-[0.85rem] text-slate-400">{row.country}</TableCell>
                                        <TableCell className="text-[0.85rem] text-slate-300 font-medium max-w-[200px] truncate" title={row.description}>{row.description}</TableCell>
                                        <TableCell className="text-[0.85rem] text-slate-400 font-mono">{row.quantity}</TableCell>
                                        <TableCell className="text-[0.85rem] text-slate-400 font-mono font-bold tracking-tight">£{Number(row.unit_price).toFixed(2)}</TableCell>
                                        <TableCell className="text-[0.85rem] font-bold text-right pr-6 accent-gradient tracking-tight font-mono">£{Number(row.revenue).toFixed(2)}</TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </div>

                <div className="p-4 bg-[#0a0f18]/80 border-t border-white/5 flex items-center justify-between">
                    <div className="font-mono text-[0.7rem] font-bold text-slate-500 uppercase tracking-widest pl-4">
                        Page {page} // {totalPages}
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            disabled={page === 1 || isLoading}
                            className="bg-transparent border-white/10 text-slate-400 hover:text-amber-500 hover:border-amber-500/50 rounded-lg px-4"
                        >
                            <ChevronLeft size={16} className="mr-2" /> PREV
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                            disabled={page === totalPages || isLoading}
                            className="bg-transparent border-white/10 text-slate-400 hover:text-amber-500 hover:border-amber-500/50 rounded-lg px-4"
                        >
                            NEXT <ChevronRight size={16} className="ml-2" />
                        </Button>
                    </div>
                </div>
            </Card>
        </div>
    );
}
