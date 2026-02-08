import React, { useState, useEffect } from 'react';
import { shieldAPI, ShieldStats, ThreatRecord, AgentInfo, ThreatInfo } from '../services/api';
import { Shield, AlertTriangle, RefreshCw, Loader2, CheckCircle, XCircle, Send, Zap } from 'lucide-react';

// Extended result type for real Gemini integration
interface AnalyzeResult {
    is_safe: boolean;
    threats_detected: ThreatInfo[];
    confidence: number;
    action: string;
    analysis_id: string;
    analyzed_at: string;
    gemini_response?: string;
    thought_signature?: string;
    thinking_level?: string;
    thinking_tokens?: number;
    output_tokens?: number;
}

export const ShieldPage: React.FC = () => {
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState<ShieldStats | null>(null);
    const [threats, setThreats] = useState<ThreatRecord[]>([]);
    const [agents, setAgents] = useState<AgentInfo[]>([]);
    const [error, setError] = useState('');

    // Test verification state
    const [testAgentId, setTestAgentId] = useState('test_agent_001');
    const [testMessage, setTestMessage] = useState('');
    const [testResponse, setTestResponse] = useState('');
    const [verifying, setVerifying] = useState(false);
    const [verifyResult, setVerifyResult] = useState<AnalyzeResult | null>(null);

    // NEW: Toggle between simulated and real Gemini
    const [useRealGemini, setUseRealGemini] = useState(true);
    const [thinkingLevel, setThinkingLevel] = useState('medium');

    const loadData = async () => {
        setLoading(true);
        setError('');

        try {
            const [statsData, threatsData, agentsData] = await Promise.all([
                shieldAPI.getStats(),
                shieldAPI.getThreats(20),
                shieldAPI.getAgents(),
            ]);
            setStats(statsData);
            setThreats(threatsData);
            setAgents(agentsData);
        } catch (err) {
            setError('Failed to load Shield data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const handleVerify = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!testMessage.trim()) return;

        setVerifying(true);
        setVerifyResult(null);
        setError('');

        try {
            let result: AnalyzeResult;

            if (useRealGemini) {
                // 🚀 REAL GEMINI INTEGRATION
                result = await shieldAPI.analyze({
                    agent_id: testAgentId,
                    message: testMessage,
                    thinking_level: thinkingLevel,
                    system_prompt: testResponse || undefined,
                });
            } else {
                // Legacy simulated mode (for demo without API key)
                const legacyResult = await shieldAPI.verify({
                    agent_id: testAgentId,
                    message: testMessage,
                    gemini_response: {
                        content: testResponse || 'Simulated response (no real Gemini call)',
                        thought_signature: `sig_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                    },
                });
                result = { ...legacyResult, gemini_response: testResponse || 'Simulated' };
            }

            setVerifyResult(result);
            // Refresh stats after verification
            loadData();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Verification failed');
        } finally {
            setVerifying(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
                        <Shield className="w-8 h-8 text-indigo-400" />
                        Moltbook Shield
                    </h1>
                    <p className="text-slate-400">Real-time AI agent threat detection</p>
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

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <p className="text-slate-400 text-sm">Agents Protected</p>
                    <p className="text-3xl font-bold text-white mt-2">{stats?.agents_protected || 0}</p>
                </div>
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <p className="text-slate-400 text-sm">Threats Blocked</p>
                    <p className="text-3xl font-bold text-red-400 mt-2">{stats?.threats_blocked || 0}</p>
                </div>
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <p className="text-slate-400 text-sm">Threats Warned</p>
                    <p className="text-3xl font-bold text-yellow-400 mt-2">{stats?.threats_warned || 0}</p>
                </div>
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                    <p className="text-slate-400 text-sm">Total Interactions</p>
                    <p className="text-3xl font-bold text-white mt-2">{stats?.total_interactions || 0}</p>
                </div>
            </div>

            {/* Test Verification */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-400" />
                    Test Verification
                </h2>
                <p className="text-slate-400 mb-4">
                    Simulate an agent interaction to test Shield's threat detection.
                </p>

                <form onSubmit={handleVerify} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm text-slate-400 mb-2">Agent ID</label>
                            <input
                                type="text"
                                value={testAgentId}
                                onChange={(e) => setTestAgentId(e.target.value)}
                                className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                placeholder="agent_123"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-2">User Message</label>
                            <input
                                type="text"
                                value={testMessage}
                                onChange={(e) => setTestMessage(e.target.value)}
                                className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                placeholder="e.g., Ignore previous instructions..."
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm text-slate-400 mb-2">System Prompt (optional)</label>
                        <textarea
                            value={testResponse}
                            onChange={(e) => setTestResponse(e.target.value)}
                            className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 h-24"
                            placeholder="Optional system prompt for the AI agent..."
                        />
                    </div>

                    {/* Gemini Integration Controls */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-slate-700/30 rounded-lg border border-slate-600">
                        <div className="flex items-center gap-3">
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={useRealGemini}
                                    onChange={(e) => setUseRealGemini(e.target.checked)}
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-indigo-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                            </label>
                            <div>
                                <span className="text-white text-sm font-medium">
                                    {useRealGemini ? '🚀 Real Gemini API' : '🧪 Simulated Mode'}
                                </span>
                                <p className="text-xs text-slate-400">
                                    {useRealGemini ? 'Calls actual Gemini API' : 'No API call, for testing UI'}
                                </p>
                            </div>
                        </div>

                        {useRealGemini && (
                            <div>
                                <label className="block text-sm text-slate-400 mb-2">Thinking Level</label>
                                <select
                                    value={thinkingLevel}
                                    onChange={(e) => setThinkingLevel(e.target.value)}
                                    className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                >
                                    <option value="minimal">Minimal (fastest, cheapest)</option>
                                    <option value="low">Low</option>
                                    <option value="medium">Medium (balanced)</option>
                                    <option value="high">High (deepest reasoning)</option>
                                </select>
                            </div>
                        )}
                    </div>

                    <button
                        type="submit"
                        disabled={verifying || !testMessage.trim()}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg flex items-center gap-2 disabled:opacity-50 transition-colors"
                    >
                        {verifying ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Send className="w-5 h-5" />
                                Verify Interaction
                            </>
                        )}
                    </button>
                </form>

                {/* Verification Result */}
                {verifyResult && (
                    <div className={`mt-6 p-4 rounded-lg border ${verifyResult.is_safe
                        ? 'bg-green-500/10 border-green-500/50'
                        : 'bg-red-500/10 border-red-500/50'
                        }`}>
                        <div className="flex items-center gap-3 mb-3">
                            {verifyResult.is_safe ? (
                                <CheckCircle className="w-6 h-6 text-green-400" />
                            ) : (
                                <XCircle className="w-6 h-6 text-red-400" />
                            )}
                            <span className={`text-lg font-semibold ${verifyResult.is_safe ? 'text-green-400' : 'text-red-400'
                                }`}>
                                {verifyResult.action.toUpperCase()}
                            </span>
                            <span className="text-slate-400 text-sm">
                                Confidence: {(verifyResult.confidence * 100).toFixed(0)}%
                            </span>
                        </div>

                        {verifyResult.threats_detected.length > 0 && (
                            <div className="space-y-2">
                                <p className="text-slate-300 font-medium">Threats Detected:</p>
                                {verifyResult.threats_detected.map((threat, idx) => (
                                    <div key={idx} className="bg-slate-800/50 rounded p-3">
                                        <span className={`text-xs px-2 py-1 rounded mr-2 ${threat.severity === 'critical' ? 'bg-red-500/30 text-red-300' :
                                            threat.severity === 'high' ? 'bg-orange-500/30 text-orange-300' :
                                                threat.severity === 'medium' ? 'bg-yellow-500/30 text-yellow-300' :
                                                    'bg-blue-500/30 text-blue-300'
                                            }`}>
                                            {threat.severity.toUpperCase()}
                                        </span>
                                        <span className="text-white">{threat.type}</span>
                                        <p className="text-slate-400 text-sm mt-1">{threat.details}</p>
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* 🔐 Thought Signature Display */}
                        {verifyResult.thought_signature && (
                            <div className="mt-4 p-4 bg-slate-700/30 rounded-lg border border-slate-600">
                                <div className="flex items-center gap-2 mb-3">
                                    <span className="text-lg">🔐</span>
                                    <h3 className="text-white font-semibold">Thought Signature</h3>
                                    <span className="text-xs px-2 py-1 rounded bg-indigo-500/30 text-indigo-300">
                                        Gemini 3
                                    </span>
                                </div>
                                <div className="bg-slate-800/70 p-3 rounded font-mono text-sm break-all">
                                    <span className="text-green-400">{verifyResult.thought_signature}</span>
                                </div>
                                <p className="text-xs text-slate-400 mt-2">
                                    This cryptographic signature proves the AI response is authentic and unmodified.
                                </p>
                            </div>
                        )}

                        {/* 🤖 Gemini Response Display */}
                        {verifyResult.gemini_response && (
                            <div className="mt-4 p-4 bg-slate-700/30 rounded-lg border border-slate-600">
                                <div className="flex items-center gap-2 mb-3">
                                    <span className="text-lg">🤖</span>
                                    <h3 className="text-white font-semibold">AI Response</h3>
                                    {verifyResult.thinking_level && (
                                        <span className="text-xs px-2 py-1 rounded bg-purple-500/30 text-purple-300">
                                            Thinking: {verifyResult.thinking_level}
                                        </span>
                                    )}
                                </div>
                                <p className="text-slate-200">{verifyResult.gemini_response}</p>
                                {verifyResult.thinking_tokens !== undefined && (
                                    <div className="flex gap-4 mt-2 text-xs text-slate-400">
                                        <span>Thinking tokens: {verifyResult.thinking_tokens}</span>
                                        <span>Output tokens: {verifyResult.output_tokens}</span>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Agents List */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Protected Agents</h2>

                {agents.length === 0 ? (
                    <div className="text-center py-8 text-slate-400">
                        <Shield className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>No agents registered yet.</p>
                        <p className="text-sm">Use the test verification above to register your first agent.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="text-left text-slate-400 text-sm border-b border-slate-700">
                                    <th className="pb-3">Agent ID</th>
                                    <th className="pb-3">Interactions</th>
                                    <th className="pb-3">Threats</th>
                                    <th className="pb-3">Baseline</th>
                                    <th className="pb-3">Last Seen</th>
                                </tr>
                            </thead>
                            <tbody>
                                {agents.map((agent) => (
                                    <tr key={agent.id} className="border-b border-slate-700/50">
                                        <td className="py-3 text-white font-mono">{agent.agent_id}</td>
                                        <td className="py-3 text-slate-300">{agent.interaction_count}</td>
                                        <td className="py-3">
                                            {agent.threat_count > 0 ? (
                                                <span className="text-red-400">{agent.threat_count}</span>
                                            ) : (
                                                <span className="text-green-400">0</span>
                                            )}
                                        </td>
                                        <td className="py-3">
                                            {agent.baseline_built ? (
                                                <span className="text-green-400">Built</span>
                                            ) : (
                                                <span className="text-yellow-400">Pending</span>
                                            )}
                                        </td>
                                        <td className="py-3 text-slate-400">
                                            {agent.last_seen_at
                                                ? new Date(agent.last_seen_at).toLocaleString()
                                                : 'Never'
                                            }
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Recent Threats */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Recent Threats</h2>

                {threats.length === 0 ? (
                    <div className="text-center py-8 text-slate-400">
                        <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-400 opacity-50" />
                        <p>No threats detected yet. Your agents are safe!</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {threats.map((threat) => (
                            <div
                                key={threat.id}
                                className="bg-slate-700/30 rounded-lg p-4 flex items-start justify-between"
                            >
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={`text-xs px-2 py-1 rounded ${threat.severity === 'critical' ? 'bg-red-500/30 text-red-300' :
                                            threat.severity === 'high' ? 'bg-orange-500/30 text-orange-300' :
                                                threat.severity === 'medium' ? 'bg-yellow-500/30 text-yellow-300' :
                                                    'bg-blue-500/30 text-blue-300'
                                            }`}>
                                            {threat.severity.toUpperCase()}
                                        </span>
                                        <span className="text-white font-medium">{threat.threat_type}</span>
                                    </div>
                                    <p className="text-sm text-slate-400">
                                        Agent: <code className="bg-slate-800 px-1 rounded">{threat.agent_id}</code>
                                        {' · '}
                                        Action: <span className={
                                            threat.action === 'block' ? 'text-red-400' :
                                                threat.action === 'warn' ? 'text-yellow-400' :
                                                    'text-green-400'
                                        }>{threat.action}</span>
                                    </p>
                                </div>
                                <span className="text-slate-500 text-sm">
                                    {new Date(threat.detected_at).toLocaleString()}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ShieldPage;
