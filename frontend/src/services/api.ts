/**
 * API Client for Hydro-Logic Trust Layer
 * Production version with authentication
 */

const API_BASE = import.meta.env.VITE_API_URL || '';

// Token management
let accessToken: string | null = localStorage.getItem('access_token');
let refreshToken: string | null = localStorage.getItem('refresh_token');

export const setTokens = (access: string, refresh: string) => {
    accessToken = access;
    refreshToken = refresh;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
};

export const clearTokens = () => {
    accessToken = null;
    refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
};

export const getAccessToken = () => accessToken;
export const isAuthenticated = () => !!accessToken;

// API request helper with auth
async function apiRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    requireAuth = true
): Promise<T> {
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (requireAuth && accessToken) {
        (headers as Record<string, string>)['Authorization'] = `Bearer ${accessToken}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });

    // Handle 401 - try refresh
    if (response.status === 401 && refreshToken && requireAuth) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            (headers as Record<string, string>)['Authorization'] = `Bearer ${accessToken}`;
            const retryResponse = await fetch(`${API_BASE}${endpoint}`, {
                ...options,
                headers,
            });
            if (!retryResponse.ok) {
                throw new Error(`API error: ${retryResponse.status}`);
            }
            return retryResponse.json();
        } else {
            clearTokens();
            window.location.href = '/login';
            throw new Error('Session expired');
        }
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `API error: ${response.status}`);
    }

    // Handle empty responses
    const text = await response.text();
    return text ? JSON.parse(text) : ({} as T);
}

async function refreshAccessToken(): Promise<boolean> {
    if (!refreshToken) return false;

    try {
        const response = await fetch(`${API_BASE}/api/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (response.ok) {
            const data = await response.json();
            setTokens(data.access_token, data.refresh_token);
            return true;
        }
    } catch {
        // Refresh failed
    }
    return false;
}

// ============ Auth API ============

export interface SignupRequest {
    email: string;
    password: string;
    company_name?: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
}

export interface UserProfile {
    id: number;
    email: string;
    company_name: string | null;
    is_verified: boolean;
    created_at: string;
}

export interface APIKeyInfo {
    id: number;
    key_prefix: string;
    name: string;
    created_at: string;
    last_used_at: string | null;
    is_active: boolean;
}

export interface APIKeyCreated {
    id: number;
    key: string;
    key_prefix: string;
    name: string;
    message: string;
}

export const authAPI = {
    signup: (data: SignupRequest) =>
        apiRequest<TokenResponse>('/api/auth/signup', {
            method: 'POST',
            body: JSON.stringify(data),
        }, false),

    login: (data: LoginRequest) =>
        apiRequest<TokenResponse>('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify(data),
        }, false),

    getProfile: () =>
        apiRequest<UserProfile>('/api/auth/me'),

    createAPIKey: (name: string) =>
        apiRequest<APIKeyCreated>('/api/auth/api-keys', {
            method: 'POST',
            body: JSON.stringify({ name }),
        }),

    listAPIKeys: () =>
        apiRequest<APIKeyInfo[]>('/api/auth/api-keys'),

    revokeAPIKey: (keyId: number) =>
        apiRequest<void>(`/api/auth/api-keys/${keyId}`, {
            method: 'DELETE',
        }),

    logout: () => {
        clearTokens();
        window.location.href = '/login';
    },
};

// ============ Shield API ============

export interface VerifyRequest {
    agent_id: string;
    message: string;
    gemini_response: {
        content: string;
        thought_signature?: string;
    };
}

export interface ThreatInfo {
    type: string;
    severity: string;
    details: string;
}

export interface VerifyResponse {
    is_safe: boolean;
    threats_detected: ThreatInfo[];
    confidence: number;
    action: string;
    analysis_id: string;
    analyzed_at: string;
}

export interface ShieldStats {
    agents_protected: number;
    threats_blocked: number;
    threats_warned: number;
    total_interactions: number;
    uptime: string;
}

export interface AgentInfo {
    id: number;
    agent_id: string;
    name: string | null;
    created_at: string;
    last_seen_at: string | null;
    baseline_built: boolean;
    interaction_count: number;
    threat_count: number;
}

export interface ThreatRecord {
    id: number;
    agent_id: string;
    threat_type: string;
    severity: string;
    details: string | null;
    action: string;
    detected_at: string;
}

export const shieldAPI = {
    verify: (data: VerifyRequest) =>
        apiRequest<VerifyResponse>('/api/shield/verify', {
            method: 'POST',
            body: JSON.stringify(data),
        }),

    getStats: () =>
        apiRequest<ShieldStats>('/api/shield/stats'),

    getThreats: (limit = 50, agentId?: string) => {
        const params = new URLSearchParams({ limit: String(limit) });
        if (agentId) params.append('agent_id', agentId);
        return apiRequest<ThreatRecord[]>(`/api/shield/threats?${params}`);
    },

    getAgents: () =>
        apiRequest<AgentInfo[]>('/api/shield/agents'),

    buildBaseline: (agentId: string) =>
        apiRequest<{ message: string }>(`/api/shield/baseline/${agentId}`, {
            method: 'POST',
        }),

    deleteAgent: (agentId: string) =>
        apiRequest<{ message: string }>(`/api/shield/agents/${agentId}`, {
            method: 'DELETE',
        }),
};

// ============ FinOps API ============

export interface RouteRequest {
    query: string;
    context?: Record<string, unknown>;
}

export interface RouteResponse {
    thinking_level: string;
    token_budget: number;
    cost_per_1k_tokens: number;
    potential_savings_percent: number;
    reasoning: string[];
    query_stats: {
        word_count: number;
        question_count: number;
        character_count: number;
    };
}

export interface RecordUsageRequest {
    query: string;
    thinking_level: string;
    tokens_used: number;
}

export interface SavingsResponse {
    timeframe: string;
    optimized_cost: number;
    naive_cost: number;
    savings: number;
    savings_percent: number;
    queries_processed: number;
}

export interface BreakdownItem {
    level: string;
    count: number;
    tokens: number;
    cost: number;
}

export interface BreakdownResponse {
    by_level: BreakdownItem[];
    total_cost: number;
    total_queries: number;
    total_tokens: number;
}

export interface HistoryItem {
    date: string;
    optimized: number;
    naive: number;
    queries: number;
}

export const finopsAPI = {
    route: (data: RouteRequest) =>
        apiRequest<RouteResponse>('/api/finops/route', {
            method: 'POST',
            body: JSON.stringify(data),
        }),

    recordUsage: (data: RecordUsageRequest) =>
        apiRequest<unknown>('/api/finops/record', {
            method: 'POST',
            body: JSON.stringify(data),
        }),

    getSavings: (timeframe = 'month') =>
        apiRequest<SavingsResponse>(`/api/finops/savings?timeframe=${timeframe}`),

    getBreakdown: () =>
        apiRequest<BreakdownResponse>('/api/finops/breakdown'),

    getHistory: (days = 7) =>
        apiRequest<HistoryItem[]>(`/api/finops/history?days=${days}`),

    getPricing: () =>
        apiRequest<{ pricing: Record<string, unknown> }>('/api/finops/pricing', {}, false),
};

// ============ Compliance API ============

export interface ImpactResponse {
    total_water_liters: number;
    total_energy_kwh: number;
    total_co2_kg: number;
    inference_events: number;
    timeframe: string;
}

export interface MetricDetail {
    value: number;
    unit: string;
    trend: string | null;
}

export interface MetricsResponse {
    timeframe: string;
    water: MetricDetail;
    energy: MetricDetail;
    co2: MetricDetail;
    inference_events: number;
    optimization_impact: string;
}

export interface ComplianceStatus {
    status: string;
    eu_ai_act_compliant: boolean;
    last_report_date: string | null;
    total_reports: number;
    environmental_rating: string;
}

export interface ReportRequest {
    company_name: string;
    start_date: string;
    end_date: string;
}

export interface ReportInfo {
    id: number;
    company_name: string;
    start_date: string;
    end_date: string;
    generated_at: string;
    total_water_liters: number;
    total_energy_kwh: number;
    total_co2_kg: number;
    inference_events: number;
}

export interface Requirement {
    article: string;
    requirement: string;
    description: string;
    our_compliance: string;
    status: string;
}

export const complianceAPI = {
    getImpact: (timeframe = 'month') =>
        apiRequest<ImpactResponse>(`/api/compliance/impact?timeframe=${timeframe}`),

    getMetrics: (timeframe = 'month') =>
        apiRequest<MetricsResponse>(`/api/compliance/metrics?timeframe=${timeframe}`),

    getStatus: () =>
        apiRequest<ComplianceStatus>('/api/compliance/status'),

    generateReport: async (data: ReportRequest): Promise<Blob> => {
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        };
        if (accessToken) {
            (headers as Record<string, string>)['Authorization'] = `Bearer ${accessToken}`;
        }

        const response = await fetch(`${API_BASE}/api/compliance/generate-report`, {
            method: 'POST',
            headers,
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error('Failed to generate report');
        }

        return response.blob();
    },

    listReports: () =>
        apiRequest<ReportInfo[]>('/api/compliance/reports'),

    getRequirements: () =>
        apiRequest<{ requirements: Requirement[]; overall_status: string }>('/api/compliance/eu-ai-act-requirements', {}, false),
};
