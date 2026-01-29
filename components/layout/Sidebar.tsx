'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const navItems = [
    { href: '/', label: 'Home', number: '01' },
    { href: '/dashboard', label: 'Dashboard', number: '02' },
    { href: '/copilot', label: 'AI Copilot', number: '03' },
    { href: '/dataset', label: 'Dataset', number: '04' },
];

export function Sidebar() {
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
                        {navItems.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        'group flex items-center gap-3 px-3 py-2 text-sm font-medium transition-all duration-200 rounded-lg',
                                        isActive
                                            ? 'text-amber-500 bg-amber-500/10 shadow-[0_0_20px_rgba(245,158,11,0.1)]'
                                            : 'text-slate-400 hover:text-white hover:bg-white/5'
                                    )}
                                >
                                    <span className={cn(
                                        "font-mono text-[0.75rem] font-bold transition-colors",
                                        isActive ? "text-amber-500" : "text-amber-600/50 group-hover:text-amber-500"
                                    )}>
                                        {item.number}
                                    </span>
                                    {item.label}
                                </Link>
                            );
                        })}
                    </nav>
                </div>

                <div className="px-2 mt-auto pb-10">
                    <h2 className="font-mono text-[0.7rem] font-bold tracking-[0.2em] text-amber-500 uppercase border-b border-white/10 pb-2 mb-4">
                        SYSTEM STATUS
                    </h2>
                    <div className="font-mono text-[0.75rem] space-y-2 text-slate-500">
                        <div className="flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                            Database connected
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                            AI model ready
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
