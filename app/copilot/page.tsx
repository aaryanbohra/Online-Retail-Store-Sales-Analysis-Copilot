'use client';

import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Bot, Send, User, Terminal, Sparkles } from 'lucide-react';
import { DynamicChart } from '@/components/charts/DynamicChart';
import { ChartSelector, ChartType } from '@/lib/chart-selector';
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '@/components/ui/collapsible';
import { Badge } from '@/components/ui/badge';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content?: string;
    sql?: string;
    data?: any[];
    chartType?: ChartType;
    insight?: string;
    error?: string;
}

export default function CopilotPage() {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([
        { id: '1', role: 'assistant', content: 'Hello! I am your AI Copilot. Ask me any business question about your retail sales data.' }
    ]);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    const generateSqlParams = useMutation({
        mutationFn: async (data: { question: string, context: any[] }) => {
            const res = await fetch('/api/generate-sql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            if (!res.ok) throw new Error((await res.json()).error);
            return res.json();
        }
    });

    const executeQueryParams = useMutation({
        mutationFn: async (sql: string) => {
            const res = await fetch('/api/execute-query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sql }),
            });
            if (!res.ok) throw new Error((await res.json()).error);
            return res.json();
        }
    });

    const generateInsightParams = useMutation({
        mutationFn: async (data: { question: string, sql: string, data: any[] }) => {
            const res = await fetch('/api/generate-insight', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            if (!res.ok) throw new Error((await res.json()).error);
            return res.json();
        }
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || generateSqlParams.isPending) return;

        const question = input;
        setInput('');

        // Add User Message
        const userMsgId = Date.now().toString();
        setMessages(prev => [...prev, { id: userMsgId, role: 'user', content: question }]);

        // Add loading placeholder
        const loadingId = (Date.now() + 1).toString();
        setMessages(prev => [...prev, { id: loadingId, role: 'assistant', content: 'ANALYZING_QUERY...' }]);

        try {
            const context = messages.slice(-6).filter(m => m.role === 'user' || (m.role === 'assistant' && m.sql)).map(m => ({
                question: m.role === 'user' ? m.content : undefined,
                sql: m.role === 'assistant' ? m.sql : undefined
            })).filter(i => i.question || i.sql);

            const sqlRes = await generateSqlParams.mutateAsync({ question, context });
            const sql = sqlRes.sql;

            setMessages(prev => prev.map(m =>
                m.id === loadingId ? { ...m, content: 'EXECUTING_SQL...', sql } : m
            ));

            const execRes = await executeQueryParams.mutateAsync(sql);
            const data = execRes.data;
            const chartType = ChartSelector.selectChartType(data, sql, question);

            setMessages(prev => prev.map(m =>
                m.id === loadingId ? { ...m, content: 'GENERATING_INSIGHT...', data, chartType } : m
            ));

            const insightRes = await generateInsightParams.mutateAsync({ question, sql, data });
            const insight = insightRes.insight;

            setMessages(prev => prev.map(m =>
                m.id === loadingId ? { ...m, content: undefined, insight } : m
            ));

        } catch (err: any) {
            setMessages(prev => prev.map(m =>
                m.id === loadingId ? { ...m, content: undefined, error: err.message } : m
            ));
        }
    };

    const isLoading = generateSqlParams.isPending || executeQueryParams.isPending || generateInsightParams.isPending;

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] animate-fade-in-up">
            <div className="flex-1 overflow-y-auto mb-6 space-y-8 pr-4 custom-scrollbar">
                {messages.map((m) => (
                    <div key={m.id} className={`flex gap-6 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-lg ${m.role === 'user' ? 'bg-amber-500 text-[#0f172a]' : 'bg-slate-800 text-amber-500 border border-white/10'}`}>
                            {m.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                        </div>

                        <div className={`flex-1 max-w-[85%] space-y-6`}>
                            {/* Text Content */}
                            {m.content && (
                                <div className={`p-5 rounded-2xl relative ${m.role === 'user' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'bg-slate-800/50 text-slate-300 border border-white/5 backdrop-blur-md'}`}>
                                    <p className={m.role === 'assistant' && m.content.includes('_') ? 'font-mono text-xs text-amber-500' : 'text-[0.95rem] font-medium leading-relaxed'}>
                                        {m.content}
                                    </p>
                                </div>
                            )}

                            {/* Error */}
                            {m.error && (
                                <div className="p-5 rounded-2xl bg-red-500/10 text-red-400 border border-red-500/20 font-mono text-sm">
                                    <div className="flex items-center gap-2 mb-2 font-bold uppercase tracking-widest text-xs">
                                        <Terminal size={14} /> // ERROR_LOG
                                    </div>
                                    <p>{m.error}</p>
                                </div>
                            )}

                            {/* Results */}
                            {m.data && (
                                <Card className="glass-card p-6 border-none rounded-3xl overflow-hidden relative">
                                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-amber-300 via-amber-500 to-amber-700" />
                                    <div className="flex items-center justify-between mb-6">
                                        <div className="font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-[0.15em] pl-4 border-l-[3px] border-amber-500">
                                            VISUALIZATION_RESULT
                                        </div>
                                        <Badge className="bg-amber-500/10 text-amber-500 border-none font-mono text-[0.65rem]">{m.data.length} ROWS</Badge>
                                    </div>
                                    <DynamicChart type={m.chartType || 'table'} data={m.data} />
                                </Card>
                            )}

                            {/* SQL Toggle */}
                            {m.sql && !m.error && (
                                <Collapsible>
                                    <CollapsibleTrigger className="flex items-center gap-2 font-mono text-[0.65rem] font-bold text-slate-500 hover:text-amber-500 transition-colors uppercase tracking-widest mb-3 pl-1">
                                        <Terminal size={14} />
                                        // VIEW_GENERATED_SQL
                                    </CollapsibleTrigger>
                                    <CollapsibleContent>
                                        <div className="p-5 bg-slate-900 border border-white/5 rounded-2xl text-[0.8rem] overflow-x-auto font-mono text-emerald-400 mb-4 shadow-2xl">
                                            {m.sql}
                                        </div>
                                    </CollapsibleContent>
                                </Collapsible>
                            )}

                            {/* Insight */}
                            {m.insight && (
                                <div className="p-6 rounded-2xl bg-amber-500/5 border-l-[3px] border-amber-500/50 backdrop-blur-sm animate-fade-in">
                                    <div className="flex items-center gap-2 mb-3 font-mono text-[0.7rem] font-bold text-amber-500 uppercase tracking-widest">
                                        <Sparkles size={14} /> AI_INSIGHT
                                    </div>
                                    <p className="text-slate-300 text-[0.95rem] leading-relaxed italic">
                                        "{m.insight}"
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                <div ref={scrollRef} />
            </div>

            <div className="relative pt-4">
                <form onSubmit={handleSubmit} className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-amber-500 to-amber-300 rounded-2xl blur opacity-20 group-focus-within:opacity-40 transition duration-500" />
                    <Card className="relative bg-slate-900 border-white/10 rounded-2xl overflow-hidden shadow-2xl">
                        <CardContent className="p-2 flex gap-2">
                            <Input
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                placeholder="Ask about trends, top products, or revenue..."
                                className="bg-transparent border-none text-white focus-visible:ring-0 focus-visible:ring-offset-0 text-[0.95rem] py-6 px-4"
                                disabled={isLoading}
                            />
                            <Button
                                type="submit"
                                disabled={isLoading || !input.trim()}
                                className="bg-amber-500 hover:bg-amber-400 text-[#0f172a] font-bold rounded-xl px-6 h-12 shadow-lg transition-all border-none"
                            >
                                {isLoading ? <Sparkles className="animate-spin" size={18} /> : <Send size={18} />}
                            </Button>
                        </CardContent>
                    </Card>
                </form>
            </div>
        </div>
    );
}
