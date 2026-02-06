import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { shieldAPI, finopsAPI, complianceAPI, ShieldStats, SavingsResponse, ComplianceStatus } from '../services/api';
import { Shield, DollarSign, FileCheck, AlertTriangle, TrendingUp, Loader2, RefreshCw } from 'lucide-react';

export const Dashboard: React.FC = () => {
    const [loading, setLoading] = useState(true);
    const [shieldStats, setShieldStats] = useState<ShieldStats | null>(null);
    const [finopsStats, setFinopsStats] = useState<SavingsResponse | null>(null);
    const [complianceStatus, setComplianceStatus] = useState<ComplianceStatus | null>(null);
    const [error, setError] = useState('');

    const loadData = async () => {
        setLoading(true);
        setError('');

        try {
            const [shield, finops, compliance] = await Promise.all([
                shieldAPI.getStats(),
                finopsAPI.getSavings('month'),
                complianceAPI.getStatus(),
            ]);
            setShieldStats(shield);
            setFinopsStats(finops);
            setComplianceStatus(compliance);
        } catch (err) {
            setError('Failed to load dashboard data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-yellow-400" />
                <p className="text-slate-400 mb-4">{error}</p>
                <button
                    onClick={loadData}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg"
                >
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
                    <p className="text-slate-400">Overview of your Hydro-Logic Trust Layer</p>
                </div>
                <button
                    onClick={loadData}
                    className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
                >
                    <RefreshCw className="w-5 h-5" />
                </button>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Agents Protected */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-3 bg-indigo-500/20 rounded-xl">
                            <Shield className="w-6 h-6 text-indigo-400" />
                        </div>
                    </div>
                    <p className="text-3xl font-bold text-white">
                        {shieldStats?.agents_protected || 0}
                    </p>
                    <p className="text-slate-400 text-sm mt-1">Agents Protected</p>
                </div>

                {/* Threats Blocked */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-3 bg-red-500/20 rounded-xl">
                            <AlertTriangle className="w-6 h-6 text-red-400" />
                        </div>
                    </div>
                    <p className="text-3xl font-bold text-white">
                        {shieldStats?.threats_blocked || 0}
                    </p>
                    <p className="text-slate-400 text-sm mt-1">Threats Blocked</p>
                </div>

                {/* Cost Savings */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-3 bg-green-500/20 rounded-xl">
                            <DollarSign className="w-6 h-6 text-green-400" />
                        </div>
                        {finopsStats && finopsStats.savings_percent > 0 && (
                            <span className="text-green-400 text-sm font-medium flex items-center gap-1">
                                <TrendingUp className="w-4 h-4" />
                                {finopsStats.savings_percent.toFixed(1)}%
                            </span>
                        )}
                    </div>
                    <p className="text-3xl font-bold text-white">
                        ${finopsStats?.savings?.toFixed(2) || '0.00'}
                    </p>
                    <p className="text-slate-400 text-sm mt-1">Savings This Month</p>
                </div>

                {/* Compliance Status */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-3 bg-purple-500/20 rounded-xl">
                            <FileCheck className="w-6 h-6 text-purple-400" />
                        </div>
                    </div>
                    <p className="text-3xl font-bold text-white">
                        {complianceStatus?.environmental_rating || 'N/A'}
                    </p>
                    <p className="text-slate-400 text-sm mt-1">Environmental Rating</p>
                </div>
            </div>

            {/* Product Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Shield Card */}
                <Link
                    to="/shield"
                    className="bg-gradient-to-br from-indigo-900/50 to-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-indigo-500/50 transition-all group"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-3 bg-indigo-500/20 rounded-xl">
                            <Shield className="w-6 h-6 text-indigo-400" />
                        </div>
                        <h3 className="text-xl font-semibold text-white">Moltbook Shield</h3>
                    </div>
                    <p className="text-slate-400 mb-4">
                        Real-time threat detection using Gemini's Thought Signatures
                    </p>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <p className="text-slate-500">Interactions</p>
                            <p className="text-white font-medium">{shieldStats?.total_interactions || 0}</p>
                        </div>
                        <div>
                            <p className="text-slate-500">Uptime</p>
                            <p className="text-white font-medium">{shieldStats?.uptime || '99.9%'}</p>
                        </div>
                    </div>
                    <p className="text-indigo-400 text-sm mt-4 group-hover:underline">
                        View Shield →
                    </p>
                </Link>

                {/* FinOps Card */}
                <Link
                    to="/finops"
                    className="bg-gradient-to-br from-green-900/50 to-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-green-500/50 transition-all group"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-3 bg-green-500/20 rounded-xl">
                            <DollarSign className="w-6 h-6 text-green-400" />
                        </div>
                        <h3 className="text-xl font-semibold text-white">FinOps Gateway</h3>
                    </div>
                    <p className="text-slate-400 mb-4">
                        Intelligent query routing for 40-60% cost reduction
                    </p>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <p className="text-slate-500">Queries Processed</p>
                            <p className="text-white font-medium">{finopsStats?.queries_processed || 0}</p>
                        </div>
                        <div>
                            <p className="text-slate-500">Total Cost</p>
                            <p className="text-white font-medium">${finopsStats?.optimized_cost?.toFixed(2) || '0.00'}</p>
                        </div>
                    </div>
                    <p className="text-green-400 text-sm mt-4 group-hover:underline">
                        View FinOps →
                    </p>
                </Link>

                {/* Compliance Card */}
                <Link
                    to="/compliance"
                    className="bg-gradient-to-br from-purple-900/50 to-slate-800/50 border border-slate-700 rounded-xl p-6 hover:border-purple-500/50 transition-all group"
                >
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-3 bg-purple-500/20 rounded-xl">
                            <FileCheck className="w-6 h-6 text-purple-400" />
                        </div>
                        <h3 className="text-xl font-semibold text-white">EU Compliance</h3>
                    </div>
                    <p className="text-slate-400 mb-4">
                        Automated EU AI Act environmental reporting
                    </p>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <p className="text-slate-500">Status</p>
                            <p className="text-white font-medium">{complianceStatus?.status || 'PENDING'}</p>
                        </div>
                        <div>
                            <p className="text-slate-500">Reports Generated</p>
                            <p className="text-white font-medium">{complianceStatus?.total_reports || 0}</p>
                        </div>
                    </div>
                    <p className="text-purple-400 text-sm mt-4 group-hover:underline">
                        View Compliance →
                    </p>
                </Link>
            </div>

            {/* Getting Started (shown when no data) */}
            {shieldStats?.agents_protected === 0 && finopsStats?.queries_processed === 0 && (
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 text-center">
                    <h2 className="text-xl font-semibold text-white mb-2">Getting Started</h2>
                    <p className="text-slate-400 mb-6 max-w-lg mx-auto">
                        You haven't started using Hydro-Logic yet. Create an API key and integrate with your application to start protecting your AI agents.
                    </p>
                    <Link
                        to="/settings"
                        className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                    >
                        Create API Key →
                    </Link>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
