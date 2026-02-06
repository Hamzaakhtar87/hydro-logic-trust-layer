import React, { useState, useEffect } from 'react';
import { authAPI, APIKeyInfo, APIKeyCreated, UserProfile } from '../services/api';
import { Key, Plus, Copy, Trash2, Check, AlertCircle, Loader2, User, Building } from 'lucide-react';

export const Settings: React.FC = () => {
    const [profile, setProfile] = useState<UserProfile | null>(null);
    const [apiKeys, setApiKeys] = useState<APIKeyInfo[]>([]);
    const [newKey, setNewKey] = useState<APIKeyCreated | null>(null);
    const [newKeyName, setNewKeyName] = useState('');
    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);
    const [copied, setCopied] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [profileData, keysData] = await Promise.all([
                authAPI.getProfile(),
                authAPI.listAPIKeys(),
            ]);
            setProfile(profileData);
            setApiKeys(keysData);
        } catch (err) {
            setError('Failed to load settings');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateKey = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newKeyName.trim()) return;

        setCreating(true);
        setError('');

        try {
            const key = await authAPI.createAPIKey(newKeyName);
            setNewKey(key);
            setNewKeyName('');
            loadData();
        } catch (err) {
            setError('Failed to create API key');
        } finally {
            setCreating(false);
        }
    };

    const handleRevokeKey = async (keyId: number) => {
        if (!confirm('Are you sure you want to revoke this API key? This cannot be undone.')) {
            return;
        }

        try {
            await authAPI.revokeAPIKey(keyId);
            loadData();
        } catch (err) {
            setError('Failed to revoke API key');
        }
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
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
            <div>
                <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
                <p className="text-slate-400">Manage your account and API keys</p>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-red-400" />
                    <span className="text-red-400">{error}</span>
                </div>
            )}

            {/* Profile Section */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <User className="w-5 h-5" />
                    Profile
                </h2>

                {profile && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Email</label>
                            <p className="text-white">{profile.email}</p>
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Company</label>
                            <p className="text-white flex items-center gap-2">
                                <Building className="w-4 h-4" />
                                {profile.company_name || 'Not set'}
                            </p>
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Member Since</label>
                            <p className="text-white">
                                {new Date(profile.created_at).toLocaleDateString()}
                            </p>
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Status</label>
                            <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${profile.is_verified
                                    ? 'bg-green-500/20 text-green-400'
                                    : 'bg-yellow-500/20 text-yellow-400'
                                }`}>
                                {profile.is_verified ? 'Verified' : 'Pending Verification'}
                            </span>
                        </div>
                    </div>
                )}
            </div>

            {/* API Keys Section */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Key className="w-5 h-5" />
                    API Keys
                </h2>

                <p className="text-slate-400 mb-6">
                    Use API keys to authenticate your applications with Hydro-Logic.
                </p>

                {/* New Key Display */}
                {newKey && (
                    <div className="bg-green-500/10 border border-green-500/50 rounded-lg p-4 mb-6">
                        <div className="flex items-center gap-2 mb-2">
                            <Check className="w-5 h-5 text-green-400" />
                            <span className="text-green-400 font-medium">API Key Created!</span>
                        </div>
                        <p className="text-slate-300 text-sm mb-3">
                            {newKey.message}
                        </p>
                        <div className="flex items-center gap-2">
                            <code className="flex-1 bg-slate-900 px-4 py-2 rounded font-mono text-sm text-white overflow-x-auto">
                                {newKey.key}
                            </code>
                            <button
                                onClick={() => copyToClipboard(newKey.key)}
                                className="p-2 bg-slate-700 hover:bg-slate-600 rounded transition-colors"
                            >
                                {copied ? (
                                    <Check className="w-5 h-5 text-green-400" />
                                ) : (
                                    <Copy className="w-5 h-5 text-white" />
                                )}
                            </button>
                        </div>
                    </div>
                )}

                {/* Create New Key Form */}
                <form onSubmit={handleCreateKey} className="flex gap-3 mb-6">
                    <input
                        type="text"
                        value={newKeyName}
                        onChange={(e) => setNewKeyName(e.target.value)}
                        placeholder="Key name (e.g., Production Server)"
                        className="flex-1 bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <button
                        type="submit"
                        disabled={creating || !newKeyName.trim()}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50 transition-colors"
                    >
                        {creating ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <Plus className="w-5 h-5" />
                        )}
                        Create Key
                    </button>
                </form>

                {/* Existing Keys List */}
                {apiKeys.length === 0 ? (
                    <div className="text-center py-8 text-slate-400">
                        <Key className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>No API keys yet. Create one to get started.</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {apiKeys.map((key) => (
                            <div
                                key={key.id}
                                className="flex items-center justify-between bg-slate-700/30 rounded-lg p-4"
                            >
                                <div>
                                    <p className="text-white font-medium">{key.name}</p>
                                    <p className="text-sm text-slate-400">
                                        <code className="bg-slate-800 px-2 py-0.5 rounded">{key.key_prefix}...</code>
                                        {' · '}
                                        Created {new Date(key.created_at).toLocaleDateString()}
                                        {key.last_used_at && (
                                            <> · Last used {new Date(key.last_used_at).toLocaleDateString()}</>
                                        )}
                                    </p>
                                </div>
                                <button
                                    onClick={() => handleRevokeKey(key.id)}
                                    className="p-2 text-red-400 hover:bg-red-500/20 rounded transition-colors"
                                    title="Revoke key"
                                >
                                    <Trash2 className="w-5 h-5" />
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Usage Example */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Quick Start</h2>
                <p className="text-slate-400 mb-4">
                    Use your API key in the <code className="bg-slate-700 px-2 py-0.5 rounded">X-API-Key</code> header:
                </p>
                <pre className="bg-slate-900 rounded-lg p-4 overflow-x-auto text-sm">
                    <code className="text-green-400">{`curl -X POST https://api.hydro-logic.com/api/finops/route \\
  -H "X-API-Key: hl_your_api_key_here" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "Hello world"}'`}</code>
                </pre>
            </div>
        </div>
    );
};

export default Settings;
