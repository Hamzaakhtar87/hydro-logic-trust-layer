import { useEffect, useState } from 'react';
import { FileCheck, Droplet, Zap, Cloud, Download, CheckCircle, RefreshCw, Leaf } from 'lucide-react';
import { complianceApi } from '../services/api';

export default function CompliancePage() {
    const [status, setStatus] = useState<any>(null);
    const [metrics, setMetrics] = useState<any>(null);
    const [requirements, setRequirements] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [downloading, setDownloading] = useState(false);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [statusData, metricsData, requirementsData] = await Promise.all([
                complianceApi.getStatus().catch(() => null),
                complianceApi.getMetrics('month').catch(() => null),
                complianceApi.getRequirements().catch(() => null),
            ]);

            if (statusData) setStatus(statusData);
            if (metricsData) setMetrics(metricsData);
            if (requirementsData) setRequirements(requirementsData);
        } catch (err) {
            console.error('Failed to fetch compliance data:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const downloadReport = async () => {
        setDownloading(true);
        try {
            const blob = await complianceApi.generateSampleReport();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `compliance_report_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Failed to download report:', err);
        } finally {
            setDownloading(false);
        }
    };

    const metricCards = [
        {
            icon: Droplet,
            label: 'Water Usage',
            value: metrics?.water?.value || 0,
            unit: metrics?.water?.unit || 'liters',
            trend: metrics?.water?.trend || '-',
            color: 'text-blue-400',
            bgColor: 'bg-blue-500/20',
        },
        {
            icon: Zap,
            label: 'Energy Consumption',
            value: metrics?.energy?.value || 0,
            unit: metrics?.energy?.unit || 'kWh',
            trend: metrics?.energy?.trend || '-',
            color: 'text-yellow-400',
            bgColor: 'bg-yellow-500/20',
        },
        {
            icon: Cloud,
            label: 'CO₂ Emissions',
            value: metrics?.co2?.value || 0,
            unit: metrics?.co2?.unit || 'kg',
            trend: metrics?.co2?.trend || '-',
            color: 'text-slate-400',
            bgColor: 'bg-slate-500/20',
        },
        {
            icon: Leaf,
            label: 'Carbon Offset',
            value: metrics?.carbon_offset_equivalent || '0 trees/year',
            unit: '',
            trend: '',
            color: 'text-green-400',
            bgColor: 'bg-green-500/20',
        },
    ];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-purple-500/20 text-purple-400">
                        <FileCheck className="w-8 h-8" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold">EU Compliance Engine</h1>
                        <p className="text-slate-400">Environmental impact tracking & EU AI Act compliance</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={downloadReport}
                        disabled={downloading}
                        className="btn-primary flex items-center gap-2"
                    >
                        {downloading ? (
                            <RefreshCw className="w-4 h-4 animate-spin" />
                        ) : (
                            <Download className="w-4 h-4" />
                        )}
                        Download Report
                    </button>
                    <button
                        onClick={fetchData}
                        className="btn-secondary"
                        disabled={loading}
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* Compliance Status Banner */}
            <div className={`glass-card p-6 border-l-4 ${status?.eu_ai_act_compliant ? 'border-green-500' : 'border-yellow-500'
                }`}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <CheckCircle className={`w-10 h-10 ${status?.eu_ai_act_compliant ? 'text-green-400' : 'text-yellow-400'
                            }`} />
                        <div>
                            <h2 className="text-2xl font-bold">
                                {status?.eu_ai_act_compliant ? 'Fully Compliant' : 'Compliance Pending'}
                            </h2>
                            <p className="text-slate-400">EU AI Act Articles 52 & 65</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-3xl font-bold text-green-400">
                            {status?.environmental_rating || 'A'}
                        </div>
                        <p className="text-sm text-slate-400">Environmental Rating</p>
                    </div>
                </div>
            </div>

            {/* Environmental Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {metricCards.map((metric, i) => (
                    <div key={i} className="glass-card p-5">
                        <div className="flex items-center justify-between mb-3">
                            <div className={`p-2 rounded-lg ${metric.bgColor}`}>
                                <metric.icon className={`w-5 h-5 ${metric.color}`} />
                            </div>
                            {metric.trend && (
                                <span className={`text-sm font-medium ${metric.trend.startsWith('-') ? 'text-green-400' : 'text-yellow-400'
                                    }`}>
                                    {metric.trend}
                                </span>
                            )}
                        </div>
                        <div className="text-2xl font-bold">
                            {typeof metric.value === 'number' ? metric.value.toFixed(2) : metric.value}
                            {metric.unit && <span className="text-sm font-normal text-slate-400 ml-1">{metric.unit}</span>}
                        </div>
                        <p className="text-sm text-slate-400">{metric.label}</p>
                    </div>
                ))}
            </div>

            {/* Optimization Impact */}
            {metrics?.optimization_impact && (
                <div className="glass-card p-6 text-center">
                    <Leaf className="w-12 h-12 mx-auto mb-3 text-green-400" />
                    <h3 className="text-xl font-bold mb-2">Environmental Impact Reduction</h3>
                    <p className="text-3xl font-bold text-green-400">{metrics.optimization_impact}</p>
                    <p className="text-slate-400 mt-2">
                        By using Hydro-Logic's intelligent routing, you're significantly reducing your AI's environmental footprint.
                    </p>
                </div>
            )}

            {/* EU AI Act Requirements */}
            <div className="glass-card p-6">
                <h2 className="text-xl font-bold mb-4">EU AI Act Compliance</h2>
                <div className="space-y-4">
                    {requirements?.requirements?.map((req: any, i: number) => (
                        <div
                            key={i}
                            className="flex items-start gap-4 p-4 rounded-lg bg-dark-800/50 border border-white/5"
                        >
                            <CheckCircle className={`w-6 h-6 flex-shrink-0 ${req.status === 'compliant' ? 'text-green-400' : 'text-yellow-400'
                                }`} />
                            <div className="flex-1">
                                <div className="flex items-center justify-between">
                                    <h3 className="font-bold">{req.article}: {req.requirement}</h3>
                                    <span className={`px-2 py-1 rounded text-xs font-medium ${req.status === 'compliant'
                                            ? 'bg-green-500/20 text-green-400'
                                            : 'bg-yellow-500/20 text-yellow-400'
                                        }`}>
                                        {req.status?.toUpperCase()}
                                    </span>
                                </div>
                                <p className="text-sm text-slate-400 mt-1">{req.description}</p>
                                <p className="text-sm text-green-400 mt-2">{req.our_compliance}</p>
                            </div>
                        </div>
                    )) || (
                            <div className="text-center py-8 text-slate-400">
                                <FileCheck className="w-12 h-12 mx-auto mb-3 opacity-50" />
                                <p>Loading compliance requirements...</p>
                            </div>
                        )}
                </div>

                {requirements?.certification_ready && (
                    <div className="mt-6 p-4 rounded-lg bg-green-500/10 border border-green-500/30 text-center">
                        <p className="text-green-400 font-medium">
                            ✓ Your system is ready for EU AI Act certification
                        </p>
                    </div>
                )}
            </div>

            {/* Report Info */}
            <div className="glass-card p-6">
                <h2 className="text-xl font-bold mb-4">Compliance Reports</h2>
                <p className="text-slate-400 mb-4">
                    Generate EU AI Act compliant environmental impact reports for auditors and regulators.
                    Reports include water usage, energy consumption, CO2 emissions, and audit trail verification.
                </p>
                <div className="grid md:grid-cols-3 gap-4">
                    <div className="p-4 rounded-lg bg-dark-800/50 text-center">
                        <div className="text-3xl font-bold text-blue-400">PDF</div>
                        <p className="text-sm text-slate-400">Report Format</p>
                    </div>
                    <div className="p-4 rounded-lg bg-dark-800/50 text-center">
                        <div className="text-3xl font-bold text-purple-400">SHA-256</div>
                        <p className="text-sm text-slate-400">Verification Hash</p>
                    </div>
                    <div className="p-4 rounded-lg bg-dark-800/50 text-center">
                        <div className="text-3xl font-bold text-green-400">Gemini</div>
                        <p className="text-sm text-slate-400">Thought Signatures</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
