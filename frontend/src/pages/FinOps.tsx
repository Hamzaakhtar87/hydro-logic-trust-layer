import React, { useState, useEffect } from 'react';
import { finopsAPI, RouteResponse, SavingsResponse, BreakdownResponse, HistoryItem } from '../services/api';
import { DollarSign, RefreshCw, Loader2, AlertTriangle, TrendingUp, Send, Zap } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';

const LEVEL_COLORS = {
    minimal: '#10b981',
    low: '#3b82f6',
    medium: '#f59e0b',
    high: '#ef4444',
};

export const FinOpsPage: React.FC = () => {
    const [loading, setLoading] = useState(true);
    const [savings, setSavings] = useState<SavingsResponse | null>(null);
    const [breakdown, setBreakdown] = useState<BreakdownResponse | null>(null);
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [error, setError] = useState('');

    // Query analyzer state
    const [query, setQuery] = useState('');
    const [analyzing, setAnalyzing] = useState(false);
    const [routeResult, setRouteResult] = useState<RouteResponse | null>(null);

    const loadData = async () => {
        setLoading(true);
        setError('');

        try {
            const [savingsData, breakdownData, historyData] = await Promise.all([
                finopsAPI.getSavings('month'),
                finopsAPI.getBreakdown(),
                finopsAPI.getHistory(7),
            ]);
            setSavings(savingsData);
            setBreakdown(breakdownData);
            setHistory(historyData);
        } catch (err) {
            setError('Failed to load FinOps data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const handleAnalyze = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setAnalyzing(true);
        setRouteResult(null);
        setError('');

        try {
            const result = await finopsAPI.route({ query });
            setRouteResult(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Analysis failed');
        } finally {
            setAnalyzing(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-green-400" />
            </div>
        );
    }

    // Prepare pie chart data
    const pieData = breakdown?.by_level.map(item => ({
        name: item.level.charAt(0).toUpperCase() + item.level.slice(1),
        value: item.count,
        color: LEVEL_COLORS[item.level as keyof typeof LEVEL_COLORS] || '#6b7280',
    })) || [];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                        <DollarSign className="w-8 h-8 text-green-400" />
                        FinOps Gateway
                    </h1>
                    <p className="text-slate-400">Intelligent cost optimization through query routing</p>
                </div>
                <button
                    onClick={loadData}
                    className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
                >
                    <RefreshCw className="w-5 h-5" />
                </button>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-center gap-3">
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                    <span className="text-red-400">{error}</span>
                </div>
            )}

            {/* Cost Comparison */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-white mb-6">Cost Comparison</h2>

                    <div className="flex items-center justify-between mb-6">
                        <div className="text-center">
                            <p className="text-slate-400 text-sm mb-1">Without Hydro-Logic</p>
                            <p className="text-3xl font-bold text-slate-400">${savings?.naive_cost?.toFixed(2) || '0.00'}</p>
                            <p className="text-xs text-slate-500">Always HIGH thinking</p>
                        </div>
                        <div className="flex flex-col items-center">
                            <TrendingUp className="w-8 h-8 text-green-400 mb-1" />
                            <span className="text-green-400 font-bold text-lg">
                                {savings?.savings_percent?.toFixed(1) || 0}% SAVED
                            </span>
                        </div>
                        <div className="text-center">
                            <p className="text-slate-400 text-sm mb-1">With Hydro-Logic</p>
                            <p className="text-3xl font-bold text-green-400">${savings?.optimized_cost?.toFixed(2) || '0.00'}</p>
                            <p className="text-xs text-slate-500">Smart routing</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 text-center pt-4 border-t border-slate-700">
                        <div>
                            <p className="text-2xl font-bold text-white">${savings?.savings?.toFixed(2) || '0.00'}</p>
                            <p className="text-xs text-slate-400">Total Saved</p>
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-white">{savings?.queries_processed || 0}</p>
                            <p className="text-xs text-slate-400">Queries Routed</p>
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-white">40-60%</p>
                            <p className="text-xs text-slate-400">Typical Savings</p>
                        </div>
                    </div>
                </div>

                {/* Query Distribution */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-white mb-4">Query Distribution</h2>

                    {pieData.length === 0 ? (
                        <div className="flex items-center justify-center h-48 text-slate-400">
                            No data yet. Analyze some queries to see distribution.
                        </div>
                    ) : (
                        <div className="h-48">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={40}
                                        outerRadius={70}
                                        paddingAngle={2}
                                        dataKey="value"
                                    >
                                        {pieData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                                        labelStyle={{ color: '#fff' }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    )}

                    <div className="flex justify-center gap-4 mt-4">
                        {Object.entries(LEVEL_COLORS).map(([level, color]) => (
                            <div key={level} className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                                <span className="text-sm text-slate-400 capitalize">{level}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Cost Trend Chart */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Cost Trend (Last 7 Days)</h2>

                {history.length === 0 ? (
                    <div className="flex items-center justify-center h-48 text-slate-400">
                        No historical data yet. Start using the API to see trends.
                    </div>
                ) : (
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={history}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                                <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `$${v}`} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                                    labelStyle={{ color: '#fff' }}
                                    formatter={(value: number) => [`$${value.toFixed(2)}`, '']}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="naive"
                                    stroke="#64748b"
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
            </div>

            {/* Query Analyzer */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    Query Analyzer
                </h2>
                <p className="text-slate-400 mb-4">
                    Test how Hydro-Logic would route any query to the optimal thinking level.
                </p>

                <form onSubmit={handleAnalyze} className="flex gap-3 mb-6">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Enter a query, e.g., 'Compare Python vs JavaScript for ML'"
                        className="flex-1 bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                    <button
                        type="submit"
                        disabled={analyzing || !query.trim()}
                        className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg flex items-center gap-2 disabled:opacity-50 transition-colors"
                    >
                        {analyzing ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Send className="w-5 h-5" />
                                Analyze
                            </>
                        )}
                    </button>
                </form>

                {/* Analysis Result */}
                {routeResult && (
                    <div className="bg-slate-700/30 rounded-lg p-6">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                            <div>
                                <p className="text-slate-400 text-sm">Thinking Level</p>
                                <p className="text-xl font-bold capitalize" style={{
                                    color: LEVEL_COLORS[routeResult.thinking_level as keyof typeof LEVEL_COLORS]
                                }}>
                                    {routeResult.thinking_level}
                                </p>
                            </div>
                            <div>
                                <p className="text-slate-400 text-sm">Cost Multiplier</p>
                                <p className="text-xl font-bold text-white">
                                    {(routeResult.cost_multiplier * 100).toFixed(0)}%
                                </p>
                            </div>
                            <div>
                                <p className="text-slate-400 text-sm">Cost per 1K</p>
                                <p className="text-xl font-bold text-white">
                                    ${routeResult.cost_per_1k_tokens}
                                </p>
                            </div>
                            <div>
                                <p className="text-slate-400 text-sm">Potential Savings</p>
                                <p className="text-xl font-bold text-green-400">
                                    {routeResult.potential_savings_percent}%
                                </p>
                            </div>
                        </div>

                        <div>
                            <p className="text-slate-400 text-sm mb-2">Reasoning:</p>
                            <ul className="space-y-1">
                                {routeResult.reasoning.map((reason, idx) => (
                                    <li key={idx} className="text-slate-300 flex items-center gap-2">
                                        <span className="w-1.5 h-1.5 bg-green-400 rounded-full" />
                                        {reason}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                )}
            </div>

            {/* Breakdown Table */}
            {breakdown && breakdown.by_level.length > 0 && (
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-white mb-4">Usage Breakdown</h2>

                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="text-left text-slate-400 text-sm border-b border-slate-700">
                                    <th className="pb-3">Level</th>
                                    <th className="pb-3">Queries</th>
                                    <th className="pb-3">Tokens</th>
                                    <th className="pb-3">Cost</th>
                                </tr>
                            </thead>
                            <tbody>
                                {breakdown.by_level.map((item) => (
                                    <tr key={item.level} className="border-b border-slate-700/50">
                                        <td className="py-3">
                                            <span className="font-medium capitalize" style={{
                                                color: LEVEL_COLORS[item.level as keyof typeof LEVEL_COLORS]
                                            }}>
                                                {item.level}
                                            </span>
                                        </td>
                                        <td className="py-3 text-white">{item.count.toLocaleString()}</td>
                                        <td className="py-3 text-white">{item.tokens.toLocaleString()}</td>
                                        <td className="py-3 text-white">${item.cost.toFixed(2)}</td>
                                    </tr>
                                ))}
                                <tr className="font-semibold">
                                    <td className="py-3 text-white">Total</td>
                                    <td className="py-3 text-white">{breakdown.total_queries.toLocaleString()}</td>
                                    <td className="py-3 text-white">{breakdown.total_tokens.toLocaleString()}</td>
                                    <td className="py-3 text-green-400">${breakdown.total_cost.toFixed(2)}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FinOpsPage;
