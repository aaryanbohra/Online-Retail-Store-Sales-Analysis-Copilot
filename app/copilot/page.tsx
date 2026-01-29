'use client';

import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from '@/components/ui/collapsible';
import { Bot, Send, User, Terminal, Sparkles } from 'lucide-react';
import { DynamicChart } from '@/components/charts/DynamicChart';
import { ChartSelector, ChartType } from '@/lib/chart-selector';

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

const INITIAL_MESSAGE: Message = {
    id: '1',
    role: 'assistant',
    content: 'Hello! I am your AI Copilot. Ask me any business question about your retail sales data.'
};

async function postJson<T>(url: string, body: unknown): Promise<T> {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error((await res.json()).error);
    return res.json();
}

export default function CopilotPage() {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Load chat history from localStorage on mount
    useEffect(() => {
        const saved = localStorage.getItem('copilot_history');
        if (saved) {
            try {
                setMessages(JSON.parse(saved));
            } catch {
                // Ignore parse errors - keep default state
            }
        }
    }, []);

    // Save chat history to localStorage when messages change
    useEffect(() => {
        if (messages.length > 1) {
            localStorage.setItem('copilot_history', JSON.stringify(messages));
        }
    }, [messages]);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    function clearHistory(): void {
        localStorage.removeItem('copilot_history');
        setMessages([INITIAL_MESSAGE]);
    }

    function updateMessage(id: string, updates: Partial<Message>): void {
        setMessages(prev => prev.map(m => m.id === id ? { ...m, ...updates } : m));
    }

    const generateSqlMutation = useMutation({
        mutationFn: (data: { question: string; context: unknown[] }) =>
            postJson<{ sql: string }>('/api/generate-sql', data)
    });

    const executeQueryMutation = useMutation({
        mutationFn: (sql: string) =>
            postJson<{ data: unknown[] }>('/api/execute-query', { sql })
    });

    const generateInsightMutation = useMutation({
        mutationFn: (data: { question: string; sql: string; data: unknown[] }) =>
            postJson<{ insight: string }>('/api/generate-insight', data)
    });

    async function handleSubmit(e: React.FormEvent): Promise<void> {
        e.preventDefault();
        if (!input.trim() || generateSqlMutation.isPending) return;

        const question = input;
        setInput('');

        const userMsgId = Date.now().toString();
        const loadingId = (Date.now() + 1).toString();

        setMessages(prev => [
            ...prev,
            { id: userMsgId, role: 'user', content: question },
            { id: loadingId, role: 'assistant', content: 'ANALYZING_QUERY...' }
        ]);

        try {
            // Build context from recent messages
            const context = messages
                .slice(-6)
                .filter(m => m.role === 'user' || (m.role === 'assistant' && m.sql))
                .map(m => ({
                    question: m.role === 'user' ? m.content : undefined,
                    sql: m.role === 'assistant' ? m.sql : undefined
                }))
                .filter(item => item.question || item.sql);

            // Step 1: Generate SQL
            const { sql } = await generateSqlMutation.mutateAsync({ question, context });
            updateMessage(loadingId, { content: 'EXECUTING_SQL...', sql });

            // Step 2: Execute query
            const { data } = await executeQueryMutation.mutateAsync(sql);
            const chartType = ChartSelector.selectChartType(data as any[], sql, question);
            updateMessage(loadingId, { content: 'GENERATING_INSIGHT...', data: data as any[], chartType });

            // Step 3: Generate insight
            const { insight } = await generateInsightMutation.mutateAsync({ question, sql, data: data as any[] });
            updateMessage(loadingId, { content: undefined, insight });

        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
            updateMessage(loadingId, { content: undefined, error: errorMessage });
        }
    }

    const isLoading = generateSqlMutation.isPending || executeQueryMutation.isPending || generateInsightMutation.isPending;

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)] animate-fade-in-up">
            <div className="flex-1 overflow-y-auto mb-6 space-y-8 pr-4 custom-scrollbar">
                {messages.map((m) => (
                    <div key={m.id} className={`flex gap-6 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-lg ${m.role === 'user' ? 'bg-amber-500 text-[#0a0f18]' : 'bg-[#1e293b] text-amber-500 border border-white/10'}`}>
                            {m.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                        </div>

                        <div className={`flex-1 max-w-[85%] space-y-6`}>
                            {/* Text Content */}
                            {m.content && (
                                <div className={`p-5 rounded-2xl relative ${m.role === 'user' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'bg-[#1e293b]/40 text-slate-300 border border-white/5 backdrop-blur-md'}`}>
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
                                        <div className="p-5 bg-[#0a0f18] border border-white/5 rounded-2xl text-[0.8rem] overflow-x-auto font-mono text-emerald-400 mb-4 shadow-2xl">
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
                <div className="flex justify-end mb-2">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={clearHistory}
                        className="text-[0.65rem] font-mono text-slate-500 hover:text-red-400 uppercase tracking-widest transition-colors"
                    >
                        // CLEAR_CONVERSATION_HISTORY
                    </Button>
                </div>
                <form onSubmit={handleSubmit} className="relative group">
                    <div className="absolute -inset-1 bg-gradient-to-r from-amber-500 to-amber-300 rounded-2xl blur opacity-20 group-focus-within:opacity-40 transition duration-500" />
                    <Card className="relative bg-[#0a0f18] border-white/10 rounded-2xl overflow-hidden shadow-2xl">
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
                                className="bg-amber-500 hover:bg-amber-400 text-[#0a0f18] font-bold rounded-xl px-6 h-12 shadow-lg transition-all border-none"
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
