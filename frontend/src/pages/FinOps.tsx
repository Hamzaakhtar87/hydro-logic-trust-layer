import { useEffect, useState } from 'react';
import { DollarSign, TrendingDown, BarChart3, Zap, RefreshCw, ArrowRight } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { finopsApi } from '../services/api';

const LEVEL_COLORS = {
    minimal: '#10b981',
    low: '#3b82f6',
    medium: '#f59e0b',
    high: '#ef4444',
};

export default function FinOpsPage() {
    const [savings, setSavings] = useState<any>(null);
    const [breakdown, setBreakdown] = useState<any>(null);
    const [history, setHistory] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [testQuery, setTestQuery] = useState('');
    const [routeResult, setRouteResult] = useState<any>(null);
    const [generating, setGenerating] = useState(false);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [savingsData, breakdownData, historyData] = await Promise.all([
                finopsApi.getSavings('all').catch(() => null),
                finopsApi.getBreakdown().catch(() => null),
                finopsApi.getHistory(7).catch(() => []),
            ]);

            if (savingsData) setSavings(savingsData);
            if (breakdownData) setBreakdown(breakdownData);
            if (historyData) setHistory(historyData);
        } catch (err) {
            console.error('Failed to fetch finops data:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const generateDemoData = async () => {
        setGenerating(true);
        try {
            await finopsApi.processDemo(100);
            await fetchData();
        } catch (err) {
            console.error('Failed to generate demo data:', err);
        } finally {
            setGenerating(false);
        }
    };

    const analyzeQuery = async () => {
        if (!testQuery.trim()) return;
        try {
            const result = await finopsApi.route(testQuery);
            setRouteResult(result);
        } catch (err) {
            console.error('Failed to analyze query:', err);
        }
    };

    const sampleQueries = [
        { label: 'Simple', query: 'Hi there!', level: 'minimal' },
        { label: 'Basic', query: 'What is the capital of France?', level: 'low' },
        { label: 'Analytical', query: 'Compare Python and JavaScript for web development. What are the pros and cons?', level: 'medium' },
        { label: 'Complex', query: 'Design a comprehensive security architecture for a distributed AI agent system.', level: 'high' },
    ];

    const pieData = breakdown ? Object.entries(breakdown.by_level || {})
        .filter(([_, v]: [string, any]) => v.count > 0)
        .map(([level, data]: [string, any]) => ({
            name: level.charAt(0).toUpperCase() + level.slice(1),
            value: data.count,
            color: LEVEL_COLORS[level as keyof typeof LEVEL_COLORS] || '#64748b',
        })) : [];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-green-500/20 text-green-400">
                        <DollarSign className="w-8 h-8" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold">FinOps Gateway</h1>
                        <p className="text-slate-400">Intelligent cost optimization through query routing</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={generateDemoData}
                        disabled={generating}
                        className="btn-primary flex items-center gap-2"
                    >
                        {generating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                        Generate Demo Data
                    </button>
                    <button
                        onClick={fetchData}
                        className="btn-secondary flex items-center gap-2"
                        disabled={loading}
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* Savings Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Before/After Comparison */}
                <div className="lg:col-span-2 glass-card p-6">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <TrendingDown className="w-5 h-5 text-green-400" />
                        Cost Comparison
                    </h2>
                    <div className="flex items-center justify-center gap-8">
                        <div className="text-center">
                            <p className="text-sm text-slate-400 mb-2">Without Hydro-Logic</p>
                            <div className="text-4xl font-bold text-red-400">
                                ${savings?.naive_cost?.toFixed(2) || '0.00'}
                            </div>
                            <p className="text-xs text-slate-500">Always HIGH thinking</p>
                        </div>

                        <div className="flex flex-col items-center">
                            <ArrowRight className="w-8 h-8 text-green-400" />
                            <div className="mt-2 px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-sm font-bold">
                                {savings?.savings_percent?.toFixed(1) || 0}% SAVED
                            </div>
                        </div>

                        <div className="text-center">
                            <p className="text-sm text-slate-400 mb-2">With Hydro-Logic</p>
                            <div className="text-4xl font-bold text-green-400">
                                ${savings?.optimized_cost?.toFixed(2) || '0.00'}
                            </div>
                            <p className="text-xs text-slate-500">Smart routing</p>
                        </div>
                    </div>

                    <div className="mt-6 pt-6 border-t border-white/10 grid grid-cols-3 gap-4 text-center">
                        <div>
                            <div className="text-2xl font-bold text-green-400">
                                ${savings?.savings?.toFixed(2) || '0.00'}
                            </div>
                            <p className="text-sm text-slate-400">Total Saved</p>
                        </div>
                        <div>
                            <div className="text-2xl font-bold">
                                {savings?.queries_processed || 0}
                            </div>
                            <p className="text-sm text-slate-400">Queries Routed</p>
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-yellow-400">
                                40-60%
                            </div>
                            <p className="text-sm text-slate-400">Typical Savings</p>
                        </div>
                    </div>
                </div>

                {/* Query Distribution Pie */}
                <div className="glass-card p-6">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-blue-400" />
                        Query Distribution
                    </h2>
                    {pieData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={200}>
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={40}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {pieData.map((entry, index) => (
                                        <Cell key={index} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    ) : (
                        <div className="h-[200px] flex items-center justify-center text-slate-400">
                            Generate demo data to see distribution
                        </div>
                    )}
                    <div className="flex flex-wrap justify-center gap-3 mt-2">
                        {Object.entries(LEVEL_COLORS).map(([level, color]) => (
                            <div key={level} className="flex items-center gap-1 text-xs">
                                <div className="w-3 h-3 rounded-full" style={{ background: color }} />
                                <span className="capitalize">{level}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Cost History Chart */}
            {history.length > 0 && (
                <div className="glass-card p-6">
                    <h2 className="text-xl font-bold mb-4">Cost Trend (Last 7 Days)</h2>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={history}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                            <YAxis stroke="#64748b" fontSize={12} />
                            <Tooltip
                                contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                            />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="naive"
                                stroke="#ef4444"
                                strokeWidth={2}
                                name="Without Optimization"
                                dot={false}
                            />
                            <Line
                                type="monotone"
                                dataKey="optimized"
                                stroke="#10b981"
                                strokeWidth={2}
                                name="With Hydro-Logic"
                                dot={false}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* Query Analyzer */}
            <div className="glass-card p-6">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    Query Analyzer
                </h2>
                <p className="text-slate-400 text-sm mb-4">
                    See how Hydro-Logic classifies queries and routes them to optimal thinking levels.
                </p>

                <div className="flex gap-2 mb-4">
                    <input
                        type="text"
                        value={testQuery}
                        onChange={(e) => setTestQuery(e.target.value)}
                        placeholder="Enter a query to analyze..."
                        className="flex-1 bg-dark-800 border border-white/10 rounded-lg px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
                        onKeyPress={(e) => e.key === 'Enter' && analyzeQuery()}
                    />
                    <button onClick={analyzeQuery} className="btn-primary">
                        Analyze
                    </button>
                </div>

                <div className="flex flex-wrap gap-2 mb-4">
                    {sampleQueries.map((sample, i) => (
                        <button
                            key={i}
                            onClick={() => {
                                setTestQuery(sample.query);
                                finopsApi.route(sample.query).then(setRouteResult);
                            }}
                            className="px-3 py-1 rounded-full text-sm border border-white/10 hover:bg-white/5 transition-colors"
                        >
                            {sample.label}
                        </button>
                    ))}
                </div>

                {routeResult && (
                    <div className="p-4 rounded-lg bg-dark-800/50 border border-white/10">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <span className="text-sm text-slate-400">Recommended Level:</span>
                                <div className="text-2xl font-bold capitalize" style={{ color: LEVEL_COLORS[routeResult.thinking_level as keyof typeof LEVEL_COLORS] }}>
                                    {routeResult.thinking_level}
                                </div>
                            </div>
                            <div className="text-right">
                                <span className="text-sm text-slate-400">Potential Savings:</span>
                                <div className="text-2xl font-bold text-green-400">
                                    {routeResult.potential_savings_percent}%
                                </div>
                            </div>
                        </div>

                        <div className="text-sm text-slate-400">
                            <strong>Reasoning:</strong>
                            <ul className="mt-1 list-disc list-inside">
                                {routeResult.reasoning?.map((reason: string, i: number) => (
                                    <li key={i}>{reason}</li>
                                ))}
                            </ul>
                        </div>

                        <div className="mt-3 pt-3 border-t border-white/10 flex gap-4 text-sm text-slate-500">
                            <span>Token Budget: {routeResult.token_budget?.toLocaleString()}</span>
                            <span>Cost/1K: ${routeResult.cost_per_1k_tokens?.toFixed(4)}</span>
                            <span>Words: {routeResult.query_stats?.word_count}</span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
