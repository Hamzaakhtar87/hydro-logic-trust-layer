// API client for Hydro-Logic Trust Layer

const API_BASE = import.meta.env.VITE_API_URL || '';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
        },
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
}

// Shield API
export const shieldApi = {
    getStats: () => fetchAPI<{
        agents_protected: number;
        threats_blocked: number;
        uptime: string;
        last_24h: { interactions: number; threats: number; blocked: number };
    }>('/api/shield/stats'),

    getThreats: (limit = 10, agentId?: string) => {
        const params = new URLSearchParams({ limit: String(limit) });
        if (agentId) params.append('agent_id', agentId);
        return fetchAPI<{ threats: any[]; total: number; blocked: number; warned: number }>(
            `/api/shield/threats?${params}`
        );
    },

    verify: (agentId: string, message: string, geminiResponse: object) =>
        fetchAPI<{
            is_safe: boolean;
            threats_detected: any[];
            confidence: number;
            action: string;
            analysis_id: string;
        }>('/api/shield/verify', {
            method: 'POST',
            body: JSON.stringify({ agent_id: agentId, message, gemini_response: geminiResponse }),
        }),

    simulateAttack: (attackType = 'injection') =>
        fetchAPI<{ message: string; attack_type: string; result: any }>(
            `/api/shield/demo/simulate-attack?attack_type=${attackType}`,
            { method: 'POST' }
        ),
};

// FinOps API
export const finopsApi = {
    route: (query: string, context?: object) =>
        fetchAPI<{
            thinking_level: string;
            token_budget: number;
            cost_per_1k_tokens: number;
            potential_savings_percent: number;
            reasoning: string[];
            query_stats: { word_count: number; question_count: number; character_count: number };
        }>('/api/finops/route', {
            method: 'POST',
            body: JSON.stringify({ query, context }),
        }),

    getSavings: (timeframe = 'today') =>
        fetchAPI<{
            timeframe: string;
            optimized_cost: number;
            naive_cost: number;
            savings: number;
            savings_percent: number;
            queries_processed: number;
        }>(`/api/finops/savings?timeframe=${timeframe}`),

    getBreakdown: () =>
        fetchAPI<{
            by_level: { [key: string]: { count: number; cost: number } };
            total_cost: number;
            total_queries: number;
        }>('/api/finops/breakdown'),

    getHistory: (days = 7) =>
        fetchAPI<{ date: string; optimized: number; naive: number }[]>(`/api/finops/history?days=${days}`),

    getPricing: () => fetchAPI<{ pricing: object; note: string }>('/api/finops/pricing'),

    processDemo: (count = 50) =>
        fetchAPI<{ message: string; stats: object; sample_results: any[] }>(
            `/api/finops/demo/process-queries?count=${count}`,
            { method: 'POST' }
        ),
};

// Compliance API
export const complianceApi = {
    getStatus: () =>
        fetchAPI<{
            status: string;
            eu_ai_act_compliant: boolean;
            last_report_date: string | null;
            environmental_rating: string;
            transparency_score: number;
        }>('/api/compliance/status'),

    getMetrics: (timeframe = 'month') =>
        fetchAPI<{
            timeframe: string;
            water: { value: number; unit: string; trend: string };
            energy: { value: number; unit: string; trend: string };
            co2: { value: number; unit: string; trend: string };
            optimization_impact: string;
            carbon_offset_equivalent: string;
        }>(`/api/compliance/metrics?timeframe=${timeframe}`),

    getRequirements: () =>
        fetchAPI<{
            requirements: {
                article: string;
                requirement: string;
                description: string;
                our_compliance: string;
                status: string;
            }[];
            overall_status: string;
            certification_ready: boolean;
        }>('/api/compliance/eu-ai-act-requirements'),

    calculateImpact: (usageData: { level: string; tokens: number }[]) =>
        fetchAPI<{
            total_water_liters: number;
            total_energy_kwh: number;
            total_co2_kg: number;
            inference_events: number;
        }>('/api/compliance/impact', {
            method: 'POST',
            body: JSON.stringify({ usage_data: usageData }),
        }),

    generateSampleReport: () =>
        fetch(`${API_BASE}/api/compliance/demo/generate-sample-report`, {
            method: 'POST',
        }).then((res) => res.blob()),
};

// Health check
export const healthCheck = () => fetchAPI<{ status: string; services: object }>('/health');
