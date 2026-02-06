// API types for Hydro-Logic Trust Layer

export interface Threat {
    id: string;
    agent_id: string;
    type: string;
    severity: 'low' | 'medium' | 'high';
    details: string;
    detected_at: string;
    action?: string;
}

export interface ShieldStats {
    agents_protected: number;
    threats_blocked: number;
    uptime: string;
    last_24h: {
        interactions: number;
        threats: number;
        blocked: number;
    };
}

export interface VerifyResult {
    is_safe: boolean;
    threats_detected: Threat[];
    confidence: number;
    action: 'allow' | 'warn' | 'block';
    analysis_id: string;
    analyzed_at: string;
}

export interface RouteResult {
    thinking_level: 'minimal' | 'low' | 'medium' | 'high';
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

export interface SavingsSummary {
    timeframe: string;
    optimized_cost: number;
    naive_cost: number;
    savings: number;
    savings_percent: number;
    queries_processed: number;
}

export interface CostBreakdown {
    by_level: {
        [key: string]: {
            count: number;
            cost: number;
        };
    };
    total_cost: number;
    total_queries: number;
}

export interface CostHistoryItem {
    date: string;
    optimized: number;
    naive: number;
}

export interface EnvironmentalImpact {
    total_water_liters: number;
    total_energy_kwh: number;
    total_co2_kg: number;
    inference_events: number;
}

export interface ComplianceStatus {
    status: string;
    eu_ai_act_compliant: boolean;
    last_report_date: string | null;
    environmental_rating: string;
    transparency_score: number;
}

export interface ComplianceRequirement {
    article: string;
    requirement: string;
    description: string;
    our_compliance: string;
    status: 'compliant' | 'partial' | 'non_compliant';
}
