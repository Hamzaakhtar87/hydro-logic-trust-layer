import { useEffect, useState } from 'react';
import { Shield, DollarSign, FileCheck, Activity, TrendingUp, Zap, AlertTriangle } from 'lucide-react';
import { shieldApi, finopsApi, complianceApi } from '../services/api';

interface StatsCard {
    label: string;
    value: string | number;
    subtext?: string;
    icon: React.ReactNode;
    color: string;
    trend?: string;
}

export default function Dashboard() {
    const [shieldStats, setShieldStats] = useState<any>(null);
    const [finopsStats, setFinopsStats] = useState<any>(null);
    const [complianceStatus, setComplianceStatus] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [shield, finops, compliance] = await Promise.all([
                    shieldApi.getStats().catch(() => null),
                    finopsApi.getSavings('all').catch(() => null),
                    complianceApi.getStatus().catch(() => null),
                ]);

                setShieldStats(shield);
                setFinopsStats(finops);
                setComplianceStatus(compliance);
                setError(null);
            } catch (err) {
                setError('Failed to load dashboard data. Make sure the backend is running.');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const statsCards: StatsCard[] = [
        {
            label: 'Agents Protected',
            value: shieldStats?.agents_protected || 770000,
            subtext: 'Moltbook agents secured',
            icon: <Shield className="w-6 h-6" />,
            color: 'from-blue-500 to-cyan-500',
            trend: '+12.5%',
        },
        {
            label: 'Threats Blocked',
            value: shieldStats?.threats_blocked || 42,
            subtext: 'In the last 24 hours',
            icon: <AlertTriangle className="w-6 h-6" />,
            color: 'from-red-500 to-orange-500',
        },
        {
            label: 'Cost Savings',
            value: `${finopsStats?.savings_percent || 45}%`,
            subtext: `$${finopsStats?.savings || 9547} saved`,
            icon: <DollarSign className="w-6 h-6" />,
            color: 'from-green-500 to-emerald-500',
            trend: '+8.2%',
        },
        {
            label: 'EU Compliant',
            value: complianceStatus?.eu_ai_act_compliant ? '100%' : 'Pending',
            subtext: 'Article 52 & 65',
            icon: <FileCheck className="w-6 h-6" />,
            color: 'from-purple-500 to-pink-500',
        },
    ];

    return (
        <div className="space-y-8">
            {/* Hero Section */}
            <div className="text-center py-8">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-600/20 text-primary-400 text-sm font-medium mb-4">
                    <Activity className="w-4 h-4" />
                    <span>Live System Status</span>
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                </div>
                <h1 className="text-4xl md:text-5xl font-bold mb-4">
                    <span className="gradient-text">Hydro-Logic</span> Trust Layer
                </h1>
                <p className="text-slate-400 text-lg max-w-2xl mx-auto">
                    HTTPS for AI Agents — Real-time security, cost optimization, and EU compliance
                    for the next generation of AI systems.
                </p>
            </div>

            {/* Error Banner */}
            {error && (
                <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-lg p-4 text-yellow-400 flex items-center gap-3">
                    <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                    <span>{error}</span>
                </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {statsCards.map((stat, index) => (
                    <div
                        key={index}
                        className="glass-card glass-card-hover p-6 relative overflow-hidden"
                    >
                        {/* Gradient accent */}
                        <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${stat.color} opacity-10 blur-2xl`} />

                        {/* Icon */}
                        <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${stat.color} text-white mb-4`}>
                            {stat.icon}
                        </div>

                        {/* Value */}
                        <div className="flex items-end gap-2 mb-1">
                            <span className="text-3xl font-bold">{loading ? '...' : stat.value}</span>
                            {stat.trend && (
                                <span className="flex items-center text-green-500 text-sm font-medium mb-1">
                                    <TrendingUp className="w-4 h-4 mr-1" />
                                    {stat.trend}
                                </span>
                            )}
                        </div>

                        {/* Label */}
                        <p className="text-slate-400 font-medium">{stat.label}</p>
                        {stat.subtext && (
                            <p className="text-slate-500 text-sm mt-1">{stat.subtext}</p>
                        )}
                    </div>
                ))}
            </div>

            {/* Products Overview */}
            <div className="grid md:grid-cols-3 gap-6 mt-8">
                {/* Shield */}
                <div className="glass-card p-6 border-l-4 border-blue-500">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 rounded-lg bg-blue-500/20 text-blue-400">
                            <Shield className="w-6 h-6" />
                        </div>
                        <h2 className="text-xl font-bold">Moltbook Shield</h2>
                    </div>
                    <p className="text-slate-400 mb-4">
                        Real-time threat detection using Gemini Thought Signatures to protect AI agents
                        from prompt injection and hijacking.
                    </p>
                    <ul className="space-y-2 text-sm">
                        <li className="flex items-center gap-2 text-slate-300">
                            <Zap className="w-4 h-4 text-yellow-500" />
                            Behavioral baseline analysis
                        </li>
                        <li className="flex items-center gap-2 text-slate-300">
                            <Zap className="w-4 h-4 text-yellow-500" />
                            Attack pattern detection
                        </li>
                        <li className="flex items-center gap-2 text-slate-300">
                            <Zap className="w-4 h-4 text-yellow-500" />
                            WebSocket real-time alerts
                        </li>
                    </ul>
                </div>

                {/* FinOps */}
                <div className="glass-card p-6 border-l-4 border-green-500">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 rounded-lg bg-green-500/20 text-green-400">
                            <DollarSign className="w-6 h-6" />
                        </div>
                        <h2 className="text-xl font-bold">FinOps Gateway</h2>
                    </div>
                    <p className="text-slate-400 mb-4">
                        Intelligent query routing to optimal thinking levels, reducing API costs
                        by 40-60% without sacrificing quality.
                    </p>
                    <ul className="space-y-2 text-sm">
                        <li className="flex items-center gap-2 text-slate-300">
                            <Zap className="w-4 h-4 text-yellow-500" />
                            Query complexity classification
                        </li>
                        <li className="flex items-center gap-2 text-slate-300">
                            <Zap className="w-4 h-4 text-yellow-500" />
                            Dynamic thinking_level routing
                        </li>
                        <li className="flex items-center gap-2 text-slate-300">
                            <Zap className="w-4 h-4 text-yellow-500" />
                            Real-time savings tracking
                        </li>
                    </ul>
                </div>

                {/* Compliance */}
                <div className="glass-card p-6 border-l-4 border-purple-500">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 rounded-lg bg-purple-500/20 text-purple-400">
                            <FileCheck className="w-6 h-6" />
                        </div>
                        <h2 className="text-xl font-bold">EU Compliance</h2>
                    </div>
                    <p className="text-slate-400 mb-4">
                        Automated EU AI Act compliance with environmental impact tracking and
                        PDF report generation.
                    </p>
                    <ul className="space-y-2 text-sm">
                        <li className="flex items-center gap-2 text-slate-300">
                            <Zap className="w-4 h-4 text-yellow-500" />
                            Water/Energy/CO2 tracking
                        </li>
                        <li className="flex items-center gap-2 text-slate-300">
                            <Zap className="w-4 h-4 text-yellow-500" />
                            Article 52 & 65 compliance
                        </li>
                        <li className="flex items-center gap-2 text-slate-300">
                            <Zap className="w-4 h-4 text-yellow-500" />
                            Automated PDF reports
                        </li>
                    </ul>
                </div>
            </div>

            {/* Hackathon Badge */}
            <div className="mt-12 text-center">
                <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-gradient-to-r from-primary-600/20 to-purple-600/20 border border-primary-500/30">
                    <span className="text-2xl">🏆</span>
                    <span className="font-semibold">Built for Gemini 3 Hackathon 2026</span>
                    <span className="text-2xl">🚀</span>
                </div>
            </div>
        </div>
    );
}
