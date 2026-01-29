import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { BarChart3, Globe, Package, Zap, History, Database, LayoutDashboard } from 'lucide-react';

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-16 animate-fade-in-up">
      {/* Hero Section */}
      <div className="mb-16 relative">
        <div className="inline-flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 rounded-full px-4 py-2 text-amber-500 font-mono text-xs font-bold mb-6 before:w-1.5 before:h-1.5 before:bg-amber-500 before:rounded-full before:animate-pulse">
          ANALYTICS PLATFORM v2.0
        </div>
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white mb-6 leading-[1.05]">
          Online Retail<br />
          <span className="accent-gradient">Sales Analysis</span>
        </h1>
        <p className="text-xl text-slate-400 max-w-xl leading-relaxed mb-8">
          AI-powered business intelligence platform. Query your data with natural language,
          visualize trends, and uncover insights in real-time.
        </p>
        <div className="flex gap-4">
          <Button asChild size="lg" className="bg-amber-500 hover:bg-amber-600 text-[#0a0f18] font-bold rounded-xl shadow-[0_0_20px_rgba(245,158,11,0.2)] h-12 px-8 border-none">
            <Link href="/copilot">Start Analyzing</Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="border-amber-500/50 text-amber-500 hover:bg-amber-500/10 rounded-xl h-12 px-8">
            <Link href="/dashboard">View Dashboard</Link>
          </Button>
        </div>
        <div className="w-16 h-1 bg-gradient-to-r from-amber-500 to-amber-300 rounded-full mt-12" />
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
        {[
          { icon: <BarChart3 className="text-amber-500" size={28} />, value: '1M+', label: 'Transactions' },
          { icon: <History className="text-amber-500" size={28} />, value: '2009-11', label: 'Time Period' },
          { icon: <Globe className="text-amber-500" size={28} />, value: '40+', label: 'Countries' },
          { icon: <Package className="text-amber-500" size={28} />, value: '4,000+', label: 'Products' },
        ].map((stat, i) => (
          <Card key={i} className="glass-card p-8 rounded-[20px] transition-all hover:-translate-y-2 hover:border-amber-500/40 group overflow-hidden relative">
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-amber-300 via-amber-500 to-amber-700 opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="mb-4 transition-transform group-hover:scale-110">{stat.icon}</div>
            <div className="text-4xl font-bold accent-gradient mb-1">{stat.value}</div>
            <div className="font-mono text-[0.7rem] font-medium text-slate-500 uppercase tracking-widest">{stat.label}</div>
          </Card>
        ))}
      </div>

      <div className="mb-6">
        <span className="font-mono text-[0.75rem] font-bold text-amber-500 uppercase tracking-[0.15em] pl-4 border-l-[3px] border-amber-500">
          PLATFORM CAPABILITIES
        </span>
      </div>

      {/* Feature Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[
          { icon: <Zap className="text-amber-500" size={32} />, title: 'AI Query Engine', desc: 'Natural language to SQL translation powered by Claude AI. Ask questions in plain English and receive instant, accurate database queries.' },
          { icon: <BarChart3 className="text-amber-500" size={32} />, title: 'Intelligent Visualization', desc: 'Automatic chart type selection based on your data structure. Line charts for trends, bar charts for comparisons, KPIs for metrics.' },
          { icon: <LayoutDashboard className="text-amber-500" size={32} />, title: 'Interactive Dashboard', desc: 'Explore revenue patterns, geographic distribution, product performance, and customer analytics with real-time filtering.' },
          { icon: <Database className="text-amber-500" size={32} />, title: 'Data Explorer', desc: 'Browse and analyze the raw transaction data. High-performance access to over 800,000 sales records.' },
        ].map((feature, i) => (
          <Card key={i} className="glass-card p-8 rounded-[20px] transition-all hover:translate-x-2 relative group flex flex-col items-start text-left">
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-amber-300 via-amber-500 to-amber-700 opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="mb-4 group-hover:rotate-[-5deg] transition-transform">{feature.icon}</div>
            <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
            <p className="text-slate-400 leading-relaxed text-[0.95rem]">{feature.desc}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
