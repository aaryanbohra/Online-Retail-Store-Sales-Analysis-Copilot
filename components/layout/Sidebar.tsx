'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { LayoutDashboard, MessageSquareText, Database, Home, LucideIcon } from 'lucide-react';

interface NavItem {
    href: string;
    label: string;
    icon: LucideIcon;
    number: string;
}

const NAV_ITEMS: NavItem[] = [
    { href: '/', label: 'Home', icon: Home, number: '01' },
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, number: '02' },
    { href: '/copilot', label: 'AI Copilot', icon: MessageSquareText, number: '03' },
    { href: '/dataset', label: 'Dataset', icon: Database, number: '04' },
];

const STATUS_ITEMS = [
    { label: 'Database connected' },
    { label: 'AI model ready' },
];

function StatusIndicator({ label }: { label: string }): React.ReactElement {
    return (
        <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
            {label}
        </div>
    );
}

export function Sidebar(): React.ReactElement {
    const pathname = usePathname();

    return (
        <div className="flex h-screen w-64 flex-col bg-[#0a0f18] border-r border-white/5 backdrop-blur-xl relative">
            <div className="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-amber-500 via-amber-400 to-amber-500 z-10" />

            <div className="flex flex-col gap-8 px-4 pt-10">
                <div className="px-2">
                    <h2 className="font-mono text-[0.7rem] font-bold tracking-[0.2em] text-amber-500 uppercase border-b border-white/10 pb-2 mb-4">
                        // NAVIGATION
                    </h2>
                    <nav className="flex flex-col gap-2">
                        {NAV_ITEMS.map((item) => {
                            const isActive = pathname === item.href;
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        'group flex items-center gap-3 px-3 py-2.5 text-sm font-medium transition-all duration-300 rounded-xl relative overflow-hidden',
                                        isActive
                                            ? 'text-amber-500 bg-amber-500/10'
                                            : 'text-slate-400 hover:text-white hover:bg-white/5'
                                    )}
                                >
                                    {isActive && (
                                        <div className="absolute left-0 top-0 bottom-0 w-[2px] bg-amber-500" />
                                    )}
                                    <span className={cn(
                                        "font-mono text-[0.7rem] font-bold transition-colors opacity-50",
                                        isActive ? "text-amber-500 opacity-100" : "group-hover:text-amber-500"
                                    )}>
                                        {item.number}
                                    </span>
                                    <Icon size={18} className={cn(
                                        "transition-all duration-300",
                                        isActive ? "text-amber-500 scale-110" : "opacity-40 group-hover:opacity-100 group-hover:scale-110"
                                    )} />
                                    {item.label}
                                </Link>
                            );
                        })}
                    </nav>
                </div>

                <div className="px-2 mt-auto pb-10">
                    <h2 className="font-mono text-[0.7rem] font-bold tracking-[0.2em] text-amber-500 uppercase border-b border-white/10 pb-2 mb-4">
                        // SYSTEM_STATUS
                    </h2>
                    <div className="font-mono text-[0.75rem] space-y-2 text-slate-500">
                        {STATUS_ITEMS.map((item) => (
                            <StatusIndicator key={item.label} label={item.label} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
