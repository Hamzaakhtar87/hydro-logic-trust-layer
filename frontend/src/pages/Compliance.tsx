import React, { useState, useEffect } from 'react';
import { complianceAPI, ComplianceStatus, MetricsResponse, ReportInfo, Requirement } from '../services/api';
import { FileCheck, RefreshCw, Loader2, AlertTriangle, Download, Droplets, Zap, Cloud, TreePine, CheckCircle } from 'lucide-react';

export const CompliancePage: React.FC = () => {
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState<ComplianceStatus | null>(null);
    const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
    const [reports, setReports] = useState<ReportInfo[]>([]);
    const [requirements, setRequirements] = useState<Requirement[]>([]);
    const [error, setError] = useState('');

    // Report generation
    const [companyName, setCompanyName] = useState('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [generating, setGenerating] = useState(false);

    const loadData = async () => {
        setLoading(true);
        setError('');

        try {
            const [statusData, metricsData, reportsData, reqData] = await Promise.all([
                complianceAPI.getStatus(),
                complianceAPI.getMetrics('month'),
                complianceAPI.listReports(),
                complianceAPI.getRequirements(),
            ]);
            setStatus(statusData);
            setMetrics(metricsData);
            setReports(reportsData);
            setRequirements(reqData.requirements);
        } catch (err) {
            setError('Failed to load compliance data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();

        // Set default dates
        const now = new Date();
        const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        setEndDate(now.toISOString().split('T')[0]);
        setStartDate(monthAgo.toISOString().split('T')[0]);
    }, []);

    const handleGenerateReport = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!companyName.trim() || !startDate || !endDate) return;

        setGenerating(true);
        setError('');

        try {
            const blob = await complianceAPI.generateReport({
                company_name: companyName,
                start_date: startDate,
                end_date: endDate,
            });

            // Download the PDF
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `compliance_report_${companyName.replace(/\s+/g, '_')}_${startDate}_${endDate}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            // Refresh reports list
            loadData();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to generate report');
        } finally {
            setGenerating(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                        <FileCheck className="w-8 h-8 text-purple-400" />
                        EU Compliance Engine
                    </h1>
                    <p className="text-slate-400">Environmental impact tracking & EU AI Act compliance</p>
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

            {/* Status & Rating */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-white">Compliance Status</h2>
                        {status?.eu_ai_act_compliant && (
                            <span className="flex items-center gap-1 text-green-400 bg-green-500/20 px-3 py-1 rounded-full text-sm">
                                <CheckCircle className="w-4 h-4" />
                                EU AI Act Compliant
                            </span>
                        )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <p className="text-slate-400 text-sm">Status</p>
                            <p className={`text-xl font-bold ${status?.status === 'COMPLIANT' ? 'text-green-400' : 'text-yellow-400'
                                }`}>
                                {status?.status || 'PENDING'}
                            </p>
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm">Reports Generated</p>
                            <p className="text-xl font-bold text-white">{status?.total_reports || 0}</p>
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm">Last Report</p>
                            <p className="text-white">
                                {status?.last_report_date
                                    ? new Date(status.last_report_date).toLocaleDateString()
                                    : 'Never'
                                }
                            </p>
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-br from-purple-900/50 to-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-white mb-4">Environmental Rating</h2>
                    <div className="flex items-center gap-6">
                        <div className="text-7xl font-bold text-purple-400">
                            {status?.environmental_rating || 'N/A'}
                        </div>
                        <div className="flex-1">
                            <p className="text-slate-400 mb-2">
                                {status?.environmental_rating === 'A+' || status?.environmental_rating === 'A'
                                    ? 'Excellent! You are optimizing AI usage efficiently.'
                                    : status?.environmental_rating === 'B' || status?.environmental_rating === 'C'
                                        ? 'Good, but there is room for improvement.'
                                        : 'Start using Hydro-Logic routing to improve your rating.'}
                            </p>
                            {metrics?.optimization_impact && (
                                <p className="text-green-400 font-medium">{metrics.optimization_impact}</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Environmental Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-3 bg-blue-500/20 rounded-xl">
                            <Droplets className="w-6 h-6 text-blue-400" />
                        </div>
                    </div>
                    <p className="text-2xl font-bold text-white">
                        {metrics?.water.value?.toFixed(2) || '0'} <span className="text-sm text-slate-400">liters</span>
                    </p>
                    <p className="text-slate-400 text-sm mt-1">Water Usage</p>
                    {metrics?.water.trend && (
                        <p className={`text-sm mt-2 ${metrics.water.trend.startsWith('-') ? 'text-green-400' :
                                metrics.water.trend.startsWith('+') ? 'text-red-400' : 'text-slate-400'
                            }`}>
                            {metrics.water.trend}
                        </p>
                    )}
                </div>

                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-3 bg-yellow-500/20 rounded-xl">
                            <Zap className="w-6 h-6 text-yellow-400" />
                        </div>
                    </div>
                    <p className="text-2xl font-bold text-white">
                        {metrics?.energy.value?.toFixed(2) || '0'} <span className="text-sm text-slate-400">kWh</span>
                    </p>
                    <p className="text-slate-400 text-sm mt-1">Energy Consumption</p>
                    {metrics?.energy.trend && (
                        <p className={`text-sm mt-2 ${metrics.energy.trend.startsWith('-') ? 'text-green-400' :
                                metrics.energy.trend.startsWith('+') ? 'text-red-400' : 'text-slate-400'
                            }`}>
                            {metrics.energy.trend}
                        </p>
                    )}
                </div>

                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-3 bg-slate-500/20 rounded-xl">
                            <Cloud className="w-6 h-6 text-slate-400" />
                        </div>
                    </div>
                    <p className="text-2xl font-bold text-white">
                        {metrics?.co2.value?.toFixed(2) || '0'} <span className="text-sm text-slate-400">kg</span>
                    </p>
                    <p className="text-slate-400 text-sm mt-1">CO₂ Emissions</p>
                    {metrics?.co2.trend && (
                        <p className={`text-sm mt-2 ${metrics.co2.trend.startsWith('-') ? 'text-green-400' :
                                metrics.co2.trend.startsWith('+') ? 'text-red-400' : 'text-slate-400'
                            }`}>
                            {metrics.co2.trend}
                        </p>
                    )}
                </div>

                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-3 bg-green-500/20 rounded-xl">
                            <TreePine className="w-6 h-6 text-green-400" />
                        </div>
                    </div>
                    <p className="text-2xl font-bold text-white">
                        {metrics?.inference_events || 0}
                    </p>
                    <p className="text-slate-400 text-sm mt-1">Inference Events</p>
                </div>
            </div>

            {/* Generate Report */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Download className="w-5 h-5 text-purple-400" />
                    Generate Compliance Report
                </h2>
                <p className="text-slate-400 mb-4">
                    Generate an EU AI Act compliant PDF report for auditors and regulators.
                </p>

                <form onSubmit={handleGenerateReport} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm text-slate-400 mb-2">Company Name</label>
                            <input
                                type="text"
                                value={companyName}
                                onChange={(e) => setCompanyName(e.target.value)}
                                className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                placeholder="Acme Corp"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-2">Start Date</label>
                            <input
                                type="date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-2">End Date</label>
                            <input
                                type="date"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                                className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                required
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={generating || !companyName.trim()}
                        className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg flex items-center gap-2 disabled:opacity-50 transition-colors"
                    >
                        {generating ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <Download className="w-5 h-5" />
                                Download Report
                            </>
                        )}
                    </button>
                </form>
            </div>

            {/* EU AI Act Requirements */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">EU AI Act Requirements</h2>

                <div className="space-y-4">
                    {requirements.map((req, idx) => (
                        <div key={idx} className="bg-slate-700/30 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-3">
                                    <span className="bg-purple-500/20 text-purple-400 text-sm px-2 py-1 rounded">
                                        {req.article}
                                    </span>
                                    <span className="text-white font-medium">{req.requirement}</span>
                                </div>
                                <span className={`flex items-center gap-1 text-sm ${req.status === 'compliant' ? 'text-green-400' : 'text-yellow-400'
                                    }`}>
                                    {req.status === 'compliant' && <CheckCircle className="w-4 h-4" />}
                                    {req.status.charAt(0).toUpperCase() + req.status.slice(1)}
                                </span>
                            </div>
                            <p className="text-slate-400 text-sm mb-2">{req.description}</p>
                            <p className="text-green-400 text-sm">✓ {req.our_compliance}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Previous Reports */}
            {reports.length > 0 && (
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-white mb-4">Previous Reports</h2>

                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="text-left text-slate-400 text-sm border-b border-slate-700">
                                    <th className="pb-3">Company</th>
                                    <th className="pb-3">Period</th>
                                    <th className="pb-3">Water</th>
                                    <th className="pb-3">Energy</th>
                                    <th className="pb-3">CO₂</th>
                                    <th className="pb-3">Generated</th>
                                </tr>
                            </thead>
                            <tbody>
                                {reports.map((report) => (
                                    <tr key={report.id} className="border-b border-slate-700/50">
                                        <td className="py-3 text-white">{report.company_name}</td>
                                        <td className="py-3 text-slate-300">
                                            {new Date(report.start_date).toLocaleDateString()} - {new Date(report.end_date).toLocaleDateString()}
                                        </td>
                                        <td className="py-3 text-slate-300">{report.total_water_liters.toFixed(2)} L</td>
                                        <td className="py-3 text-slate-300">{report.total_energy_kwh.toFixed(2)} kWh</td>
                                        <td className="py-3 text-slate-300">{report.total_co2_kg.toFixed(2)} kg</td>
                                        <td className="py-3 text-slate-400">
                                            {new Date(report.generated_at).toLocaleDateString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CompliancePage;
