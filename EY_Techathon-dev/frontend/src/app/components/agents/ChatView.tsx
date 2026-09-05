import { Send, Sparkles, Loader2, CheckCircle, AlertTriangle, XCircle, TrendingUp, Target, Beaker, Shield, FileText, Activity } from 'lucide-react';
import { Agent } from '../../App';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const API_BASE_URL = 'http://localhost:8000';

// Styled Components for Structured Output
const Card = ({ title, icon: Icon, children, className = '' }: { title: string; icon?: any; children: React.ReactNode; className?: string }) => (
  <div className={`bg-[#1a2533] border border-[#2a3f5f] rounded-xl p-4 mb-4 ${className}`}>
    <h3 className="flex items-center gap-2 text-lg font-semibold text-white mb-3 border-b border-[#2a3f5f] pb-2">
      {Icon && <Icon className="w-5 h-5 text-[#4ade80]" />}
      {title}
    </h3>
    {children}
  </div>
);

const ScoreBar = ({ label, score, max = 10 }: { label: string; score: number; max?: number }) => {
  const percentage = (score / max) * 100;
  const getColor = () => {
    if (percentage >= 70) return 'bg-green-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  return (
    <div className="mb-2">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-white font-semibold">{score}/{max}</span>
      </div>
      <div className="h-2 bg-[#0f1722] rounded-full overflow-hidden">
        <div className={`h-full ${getColor()} rounded-full transition-all`} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
};

const Badge = ({ children, variant = 'default' }: { children: React.ReactNode; variant?: 'success' | 'warning' | 'danger' | 'info' | 'default' }) => {
  const colors = {
    success: 'bg-green-500/20 text-green-400 border-green-500/30',
    warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    danger: 'bg-red-500/20 text-red-400 border-red-500/30',
    info: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    default: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  };
  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${colors[variant]}`}>
      {children}
    </span>
  );
};

const DataTable = ({ headers, rows }: { headers: string[]; rows: (string | React.ReactNode)[][] }) => (
  <div className="overflow-x-auto">
    <table className="w-full border-collapse">
      <thead>
        <tr>
          {headers.map((h, i) => (
            <th key={i} className="bg-[#0f1722] border border-[#2a3f5f] px-3 py-2 text-left text-sm font-semibold text-white">{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i} className="hover:bg-[#0f1722]/50">
            {row.map((cell, j) => (
              <td key={j} className="border border-[#2a3f5f] px-3 py-2 text-sm text-gray-300">{cell}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const StatCard = ({ label, value, icon: Icon, color = 'text-[#4ade80]' }: { label: string; value: string | number; icon?: any; color?: string }) => (
  <div className="bg-[#0f1722] border border-[#2a3f5f] rounded-lg p-3 text-center">
    {Icon && <Icon className={`w-6 h-6 ${color} mx-auto mb-1`} />}
    <div className={`text-2xl font-bold ${color}`}>{value}</div>
    <div className="text-xs text-gray-400">{label}</div>
  </div>
);

interface ChatViewProps {
  agent: Agent;
  config: any;
  input: string;
  setInput: (value: string) => void;
  handleSend: () => void;
  hasQuery: boolean;
}

// Drug Discovery API Response types
interface AgentOutput {
  status: 'success' | 'error' | 'pending';
  content: string | null;
  error: string | null;
  timestamp: string;
}

// Structured Output Types for Drug Discovery
interface TargetInfo {
  target_name: string;
  target_type?: string;
  gene_symbol?: string;
  uniprot_id?: string;
  validation_score?: number;
  disease_association?: string;
  druggability_assessment?: string;
  known_modulators?: string[];
}

interface LeadCompound {
  compound_id: string;
  smiles?: string;
  molecular_weight?: number;
  logp?: number;
  binding_affinity?: string;
  selectivity?: string;
  lead_score?: number;
  lipinski_violations?: number;
  source?: string;
}

interface OptimizationResult {
  optimized_compound_id: string;
  parent_compound_id?: string;
  modifications?: string[];
  improved_properties?: Record<string, string>;
  admet_profile?: Record<string, any>;
  optimization_score?: number;
  synthetic_accessibility?: number;
}

interface PreclinicalData {
  candidate_id: string;
  toxicity_assessment?: Record<string, any>;
  efficacy_data?: Record<string, any>;
  pharmacokinetics?: Record<string, any>;
  safety_score?: number;
  efficacy_score?: number;
  recommendation?: string;
  risk_factors?: string[];
}

interface RiskAssessment {
  risk_category: string;
  source_agent: string;
  severity: 'High' | 'Medium' | 'Low';
  impact: string;
  mitigation?: string;
}

interface StrategicDecision {
  recommendation: 'GO' | 'CONDITIONAL_GO' | 'NO_GO';
  scientific_merit_score: number;
  technical_feasibility_score: number;
  safety_profile_score: number;
  commercial_viability_score: number;
  overall_score: number;
  critical_success_factors?: string[];
  red_flags?: string[];
}

interface ActionItem {
  action: string;
  timeframe: 'immediate' | 'near_term' | 'long_term';
  priority: 'High' | 'Medium' | 'Low';
  responsible_party?: string;
  resources_required?: string;
}

interface DrugDiscoveryStructuredOutput {
  workflow_id: string;
  query: string;
  execution_start: string;
  execution_end?: string;
  workflow_status: string;
  target_discovery?: TargetInfo;
  target_discovery_raw?: string;
  lead_compounds?: LeadCompound[];
  lead_identification_raw?: string;
  optimization_results?: OptimizationResult[];
  optimization_raw?: string;
  preclinical_data?: PreclinicalData;
  preclinical_raw?: string;
  risk_matrix?: RiskAssessment[];
  strategic_decision?: StrategicDecision;
  action_roadmap?: ActionItem[];
  executive_summary?: string;
  cross_agent_insights?: string[];
  coordinator_response?: string;
}

interface DrugDiscoveryResponse {
  workflow_id: string;
  query: string;
  execution_start: string;
  execution_end: string | null;
  workflow_status: 'running' | 'complete' | 'failed';
  agent_outputs: Record<string, AgentOutput>;
  coordinator_response: string | null;
  structured_output?: DrugDiscoveryStructuredOutput;
}

// Structured Output Types for Deep Research
interface PaperResult {
  title: string;
  pmid?: string;
  doi?: string;
  authors?: string[];
  journal?: string;
  publication_date?: string;
  abstract?: string;
  url?: string;
  citation_count?: number;
  keywords?: string[];
  study_type?: string;
  evidence_level?: string;
}

interface ClinicalTrialResult {
  nct_id: string;
  title: string;
  status: string;
  phase?: string;
  conditions?: string[];
  interventions?: string[];
  sponsor?: string;
  start_date?: string;
  completion_date?: string;
  enrollment?: number;
  primary_outcomes?: string[];
  url?: string;
  locations?: string[];
}

interface DrugResult {
  name: string;
  generic_name?: string;
  brand_names?: string[];
  drug_class?: string;
  mechanism?: string;
  fda_status?: string;
  approval_date?: string;
  indications?: string[];
  contraindications?: string[];
  side_effects?: string[];
  interactions?: string[];
  dosage_forms?: string[];
}

interface EvidenceSummary {
  total_papers: number;
  total_trials: number;
  total_drugs: number;
  meta_analyses_count: number;
  rct_count: number;
  overall_evidence_quality: string;
  confidence_level?: number;
}

interface ResearchGap {
  gap_description: string;
  gap_type: string;
  priority: string;
  suggested_research?: string;
}

interface Recommendation {
  recommendation: string;
  target_audience: string;
  strength: string;
  evidence_basis?: string;
}

interface CritiqueResult {
  quality_score: number;
  completeness_score?: number;
  accuracy_score?: number;
  structure_score?: number;
  clinical_relevance_score?: number;
  overall_assessment: string;
  strengths?: string[];
  weaknesses?: string[];
  suggestions?: string[];
}

interface KeyFinding {
  finding: string;
  source_type: string;
  confidence: string;
  supporting_evidence?: string[];
}

interface TherapeuticLandscape {
  current_standard_of_care?: string;
  emerging_therapies?: string[];
  pipeline_drugs?: string[];
  unmet_needs?: string[];
  market_trends?: string;
}

interface DeepResearchStructuredOutput {
  research_id: string;
  query: string;
  mode: string;
  status: string;
  execution_time?: number;
  timestamp: string;
  papers?: PaperResult[];
  papers_summary?: string;
  trials?: ClinicalTrialResult[];
  trials_summary?: string;
  active_trials_count?: number;
  drugs?: DrugResult[];
  drugs_summary?: string;
  evidence_summary?: EvidenceSummary;
  key_findings?: KeyFinding[];
  therapeutic_landscape?: TherapeuticLandscape;
  executive_summary?: string;
  synthesis?: string;
  research_gaps?: ResearchGap[];
  recommendations?: Recommendation[];
  critique?: CritiqueResult;
  clinical_implications?: string[];
  future_directions?: string[];
}

interface DeepResearchResponse {
  research_id: string;
  query: string;
  status: string;
  execution_time?: number;
  papers: any[];
  trials: any[];
  drugs: any[];
  synthesis?: string;
  gaps?: string[];
  recommendations?: string[];
  critique?: any;
  structured_output?: DeepResearchStructuredOutput;
  timestamp: string;
}

// Structured Output Renderer Components
const DrugDiscoveryStructuredView = ({ data, coordinator }: { data: DrugDiscoveryStructuredOutput; coordinator?: string }) => (
  <div className="space-y-4">
    {/* Header */}
    <div className="flex items-center gap-3 mb-4">
      <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-cyan-500 rounded-xl flex items-center justify-center">
        <Beaker className="w-6 h-6 text-white" />
      </div>
      <div>
        <h2 className="text-2xl font-bold text-white">Drug Discovery Analysis</h2>
        <p className="text-sm text-gray-400">Workflow ID: {data.workflow_id}</p>
      </div>
      <Badge variant={data.workflow_status === 'complete' ? 'success' : 'warning'}>{data.workflow_status}</Badge>
    </div>

    {/* Executive Summary */}
    {data.executive_summary && (
      <Card title="Executive Summary" icon={FileText}>
        <p className="text-gray-300 leading-relaxed">{data.executive_summary}</p>
      </Card>
    )}

    {/* Strategic Decision */}
    {data.strategic_decision && (
      <Card title="Strategic Decision" icon={Target}>
        <div className="mb-4">
          <div className="flex items-center gap-3 mb-4">
            {data.strategic_decision.recommendation === 'GO' ? (
              <Badge variant="success">🟢 GO</Badge>
            ) : data.strategic_decision.recommendation === 'CONDITIONAL_GO' ? (
              <Badge variant="warning">🟡 CONDITIONAL GO</Badge>
            ) : (
              <Badge variant="danger">🔴 NO-GO</Badge>
            )}
            <span className="text-2xl font-bold text-white">{data.strategic_decision.overall_score}/10</span>
            <span className="text-gray-400">Overall Score</span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <ScoreBar label="Scientific Merit" score={data.strategic_decision.scientific_merit_score} />
          <ScoreBar label="Technical Feasibility" score={data.strategic_decision.technical_feasibility_score} />
          <ScoreBar label="Safety Profile" score={data.strategic_decision.safety_profile_score} />
          <ScoreBar label="Commercial Viability" score={data.strategic_decision.commercial_viability_score} />
        </div>
        {data.strategic_decision.critical_success_factors && data.strategic_decision.critical_success_factors.length > 0 && (
          <div className="mt-3">
            <p className="text-sm font-semibold text-green-400 mb-2">Critical Success Factors:</p>
            <ul className="space-y-1">
              {data.strategic_decision.critical_success_factors.map((f, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-gray-300">
                  <CheckCircle className="w-4 h-4 text-green-500" /> {f}
                </li>
              ))}
            </ul>
          </div>
        )}
        {data.strategic_decision.red_flags && data.strategic_decision.red_flags.length > 0 && (
          <div className="mt-3">
            <p className="text-sm font-semibold text-red-400 mb-2">Red Flags:</p>
            <ul className="space-y-1">
              {data.strategic_decision.red_flags.map((f, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-gray-300">
                  <AlertTriangle className="w-4 h-4 text-red-500" /> {f}
                </li>
              ))}
            </ul>
          </div>
        )}
      </Card>
    )}

    {/* Target Discovery */}
    {data.target_discovery && (
      <Card title="Target Discovery" icon={Target}>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div className="bg-[#0f1722] rounded-lg p-3">
            <p className="text-xs text-gray-400">Target Name</p>
            <p className="text-white font-semibold">{data.target_discovery.target_name}</p>
          </div>
          {data.target_discovery.target_type && (
            <div className="bg-[#0f1722] rounded-lg p-3">
              <p className="text-xs text-gray-400">Type</p>
              <p className="text-white">{data.target_discovery.target_type}</p>
            </div>
          )}
          {data.target_discovery.gene_symbol && (
            <div className="bg-[#0f1722] rounded-lg p-3">
              <p className="text-xs text-gray-400">Gene Symbol</p>
              <p className="text-cyan-400 font-mono">{data.target_discovery.gene_symbol}</p>
            </div>
          )}
          {data.target_discovery.uniprot_id && (
            <div className="bg-[#0f1722] rounded-lg p-3">
              <p className="text-xs text-gray-400">UniProt ID</p>
              <p className="text-cyan-400 font-mono">{data.target_discovery.uniprot_id}</p>
            </div>
          )}
          {data.target_discovery.validation_score && (
            <div className="bg-[#0f1722] rounded-lg p-3">
              <p className="text-xs text-gray-400">Validation Score</p>
              <p className="text-green-400 font-bold">{data.target_discovery.validation_score}/10</p>
            </div>
          )}
          {data.target_discovery.druggability_assessment && (
            <div className="bg-[#0f1722] rounded-lg p-3">
              <p className="text-xs text-gray-400">Druggability</p>
              <p className="text-white">{data.target_discovery.druggability_assessment}</p>
            </div>
          )}
        </div>
      </Card>
    )}

    {/* Lead Compounds */}
    {data.lead_compounds && data.lead_compounds.length > 0 && (
      <Card title="Lead Compounds" icon={Beaker}>
        <DataTable
          headers={['Compound ID', 'MW', 'LogP', 'Binding Affinity', 'Lead Score']}
          rows={data.lead_compounds.map(lead => [
            <span className="font-mono text-cyan-400">{lead.compound_id}</span>,
            lead.molecular_weight?.toFixed(1) || 'N/A',
            lead.logp?.toFixed(2) || 'N/A',
            lead.binding_affinity || 'N/A',
            lead.lead_score ? <Badge variant={lead.lead_score >= 7 ? 'success' : lead.lead_score >= 5 ? 'warning' : 'danger'}>{lead.lead_score}/10</Badge> : 'N/A'
          ])}
        />
      </Card>
    )}

    {/* Risk Matrix */}
    {data.risk_matrix && data.risk_matrix.length > 0 && (
      <Card title="Risk Assessment" icon={AlertTriangle}>
        <DataTable
          headers={['Category', 'Source', 'Severity', 'Impact', 'Mitigation']}
          rows={data.risk_matrix.map(risk => [
            risk.risk_category,
            risk.source_agent,
            <Badge variant={risk.severity === 'High' ? 'danger' : risk.severity === 'Medium' ? 'warning' : 'success'}>{risk.severity}</Badge>,
            risk.impact,
            risk.mitigation || 'N/A'
          ])}
        />
      </Card>
    )}

    {/* Action Roadmap */}
    {data.action_roadmap && data.action_roadmap.length > 0 && (
      <Card title="Action Roadmap" icon={TrendingUp}>
        <div className="space-y-4">
          {['immediate', 'near_term', 'long_term'].map(timeframe => {
            const actions = data.action_roadmap?.filter(a => a.timeframe === timeframe) || [];
            if (actions.length === 0) return null;
            const labels = { immediate: '🚀 Immediate (0-3 months)', near_term: '📈 Near-term (3-12 months)', long_term: '🎯 Long-term (1-3 years)' };
            return (
              <div key={timeframe}>
                <h4 className="text-sm font-semibold text-gray-400 mb-2">{labels[timeframe as keyof typeof labels]}</h4>
                <ul className="space-y-2">
                  {actions.map((a, i) => (
                    <li key={i} className="flex items-start gap-3 bg-[#0f1722] rounded-lg p-3">
                      <Badge variant={a.priority === 'High' ? 'danger' : a.priority === 'Medium' ? 'warning' : 'info'}>{a.priority}</Badge>
                      <div>
                        <p className="text-gray-200">{a.action}</p>
                        {a.responsible_party && <p className="text-xs text-gray-500 mt-1">→ {a.responsible_party}</p>}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </Card>
    )}

    {/* Cross-Agent Insights */}
    {data.cross_agent_insights && data.cross_agent_insights.length > 0 && (
      <Card title="Key Insights" icon={Sparkles}>
        <ul className="space-y-2">
          {data.cross_agent_insights.map((insight, i) => (
            <li key={i} className="flex items-start gap-2 text-gray-300">
              <span className="text-cyan-400">💡</span> {insight}
            </li>
          ))}
        </ul>
      </Card>
    )}

    {/* Coordinator Response - Collapsible */}
    {coordinator && (
      <details className="bg-[#1a2533] border border-[#2a3f5f] rounded-xl overflow-hidden">
        <summary className="cursor-pointer p-4 text-white font-semibold hover:bg-[#0f1722]">
          📄 Full Analysis Report (Click to expand)
        </summary>
        <div className="p-4 border-t border-[#2a3f5f] prose prose-invert prose-sm max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{coordinator}</ReactMarkdown>
        </div>
      </details>
    )}
  </div>
);

const DeepResearchStructuredView = ({ data, papers, trials, drugs }: { data: DeepResearchStructuredOutput; papers?: any[]; trials?: any[]; drugs?: any[] }) => (
  <div className="space-y-4">
    {/* Header */}
    <div className="flex items-center gap-3 mb-4">
      <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
        <FileText className="w-6 h-6 text-white" />
      </div>
      <div>
        <h2 className="text-2xl font-bold text-white">Deep Research Report</h2>
        <p className="text-sm text-gray-400">Research ID: {data.research_id}</p>
      </div>
      <Badge variant={data.status === 'complete' ? 'success' : 'warning'}>{data.status}</Badge>
      {data.execution_time && (
        <span className="text-sm text-gray-400 ml-auto">{data.execution_time.toFixed(1)}s</span>
      )}
    </div>

    {/* Evidence Summary Stats */}
    {data.evidence_summary && (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <StatCard label="Papers Found" value={data.evidence_summary.total_papers} icon={FileText} color="text-blue-400" />
        <StatCard label="Clinical Trials" value={data.evidence_summary.total_trials} icon={Activity} color="text-green-400" />
        <StatCard label="Drugs Analyzed" value={data.evidence_summary.total_drugs} icon={Beaker} color="text-purple-400" />
        <StatCard 
          label="Confidence" 
          value={`${(data.evidence_summary.confidence_level || 0) * 100}%`} 
          icon={Shield} 
          color={(data.evidence_summary.confidence_level || 0) >= 0.7 ? 'text-green-400' : 'text-yellow-400'} 
        />
      </div>
    )}

    {/* Research Summary */}
    {(data.executive_summary || data.synthesis) && (
      <Card title="Research Summary" icon={FileText}>
        <p className="text-gray-300 leading-relaxed">{data.executive_summary || data.synthesis}</p>
      </Card>
    )}

    {/* Key Findings */}
    {data.key_findings && data.key_findings.length > 0 && (
      <Card title="Key Findings" icon={Sparkles}>
        <div className="space-y-3">
          {data.key_findings.map((finding, i) => (
            <div key={i} className="bg-[#0f1722] rounded-lg p-4">
              <div className="flex items-start justify-between gap-2 mb-2">
                <p className="text-white font-medium">{finding.finding}</p>
                <Badge variant={finding.confidence === 'High' ? 'success' : finding.confidence === 'Moderate' ? 'warning' : 'info'}>
                  {finding.confidence}
                </Badge>
              </div>
              {finding.supporting_evidence && finding.supporting_evidence.length > 0 && (
                <ul className="mt-2 space-y-1">
                  {finding.supporting_evidence.slice(0, 3).map((e, j) => (
                    <li key={j} className="text-sm text-gray-400 flex items-start gap-2">
                      <span className="text-gray-500">•</span> {e}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      </Card>
    )}

    {/* Therapeutic Landscape */}
    {data.therapeutic_landscape && (
      <Card title="Therapeutic Landscape" icon={Activity}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.therapeutic_landscape.current_standard_of_care && (
            <div className="bg-[#0f1722] rounded-lg p-3">
              <p className="text-xs text-gray-400 mb-1">Current Standard of Care</p>
              <p className="text-gray-200">{data.therapeutic_landscape.current_standard_of_care}</p>
            </div>
          )}
          {data.therapeutic_landscape.emerging_therapies && data.therapeutic_landscape.emerging_therapies.length > 0 && (
            <div className="bg-[#0f1722] rounded-lg p-3">
              <p className="text-xs text-gray-400 mb-1">Emerging Therapies</p>
              {data.therapeutic_landscape.emerging_therapies.map((t, i) => (
                <Badge key={i} variant="success">{t}</Badge>
              ))}
            </div>
          )}
          {data.therapeutic_landscape.unmet_needs && data.therapeutic_landscape.unmet_needs.length > 0 && (
            <div className="bg-[#0f1722] rounded-lg p-3 col-span-full">
              <p className="text-xs text-gray-400 mb-2">Unmet Medical Needs</p>
              <ul className="space-y-1">
                {data.therapeutic_landscape.unmet_needs.map((n, i) => (
                  <li key={i} className="text-gray-300 text-sm flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" /> {n}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </Card>
    )}

    {/* Research Gaps */}
    {data.research_gaps && data.research_gaps.length > 0 && (
      <Card title="Research Gaps" icon={AlertTriangle}>
        <DataTable
          headers={['Gap', 'Priority', 'Impact']}
          rows={data.research_gaps.map(gap => [
            gap.gap_description,
            <Badge variant={gap.priority === 'High' ? 'danger' : gap.priority === 'Medium' ? 'warning' : 'info'}>{gap.priority}</Badge>,
            gap.potential_impact || 'N/A'
          ])}
        />
      </Card>
    )}

    {/* Recommendations */}
    {data.recommendations && data.recommendations.length > 0 && (
      <Card title="Recommendations" icon={CheckCircle}>
        <div className="space-y-3">
          {data.recommendations.map((rec, i) => (
            <div key={i} className="bg-[#0f1722] rounded-lg p-4">
              <div className="flex items-start justify-between gap-2 mb-2">
                <p className="text-white font-medium">{rec.recommendation}</p>
                <Badge variant={rec.strength === 'Strong' ? 'success' : rec.strength === 'Moderate' ? 'warning' : 'info'}>
                  {rec.strength}
                </Badge>
              </div>
              {rec.rationale && <p className="text-sm text-gray-400 mb-2">{rec.rationale}</p>}
              {rec.implementation_steps && rec.implementation_steps.length > 0 && (
                <ol className="mt-2 space-y-1 list-decimal list-inside">
                  {rec.implementation_steps.map((step, j) => (
                    <li key={j} className="text-sm text-gray-300">{step}</li>
                  ))}
                </ol>
              )}
            </div>
          ))}
        </div>
      </Card>
    )}

    {/* Papers - Collapsible */}
    {papers && papers.length > 0 && (
      <details className="bg-[#1a2533] border border-[#2a3f5f] rounded-xl overflow-hidden">
        <summary className="cursor-pointer p-4 text-white font-semibold hover:bg-[#0f1722] flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-400" />
          📚 Literature ({papers.length} papers)
        </summary>
        <div className="p-4 border-t border-[#2a3f5f] max-h-96 overflow-y-auto space-y-3">
          {papers.slice(0, 10).map((paper: any, i: number) => (
            <div key={i} className="bg-[#0f1722] rounded-lg p-3">
              <p className="text-white font-medium text-sm">{paper.title}</p>
              {paper.authors && <p className="text-xs text-gray-500 mt-1">{paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? ' et al.' : ''}</p>}
              <div className="flex gap-2 mt-2">
                {paper.journal && <Badge variant="info">{paper.journal}</Badge>}
                {paper.publication_date && <Badge variant="default">{paper.publication_date}</Badge>}
              </div>
            </div>
          ))}
        </div>
      </details>
    )}

    {/* Clinical Trials - Collapsible */}
    {trials && trials.length > 0 && (
      <details className="bg-[#1a2533] border border-[#2a3f5f] rounded-xl overflow-hidden">
        <summary className="cursor-pointer p-4 text-white font-semibold hover:bg-[#0f1722] flex items-center gap-2">
          <Activity className="w-5 h-5 text-green-400" />
          🏥 Clinical Trials ({trials.length} trials)
        </summary>
        <div className="p-4 border-t border-[#2a3f5f] overflow-x-auto">
          <DataTable
            headers={['Title', 'NCT ID', 'Status', 'Phase']}
            rows={trials.slice(0, 10).map((trial: any) => [
              trial.title?.substring(0, 60) + (trial.title?.length > 60 ? '...' : ''),
              <span className="font-mono text-cyan-400">{trial.nct_id}</span>,
              <Badge variant={trial.status === 'Completed' ? 'success' : trial.status === 'Recruiting' ? 'warning' : 'info'}>{trial.status}</Badge>,
              trial.phase || 'N/A'
            ])}
          />
        </div>
      </details>
    )}
  </div>
);

export function ChatView({ agent, config, input, setInput, handleSend: parentHandleSend, hasQuery }: ChatViewProps) {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string; structuredData?: any; dataType?: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userQuery = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userQuery }]);
    setInput('');
    setIsLoading(true);
    setError(null);
    
    // Call parent handleSend to update hasQuery state
    parentHandleSend();

    try {
      let response: Response;
      let result: any;

      if (agent === 'drug-discovery') {
        response = await fetch(`${API_BASE_URL}/api/v1/drug-discovery/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: userQuery }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        result = await response.json() as DrugDiscoveryResponse;
        
        // Use structured view if available
        if (result.structured_output) {
          setMessages(prev => [...prev, { 
            role: 'assistant', 
            content: '', 
            structuredData: result.structured_output,
            dataType: 'drug-discovery'
          }]);
        } else {
          // Fallback to markdown
          let markdownContent = `# 🧬 Drug Discovery Analysis\n\n`;
          markdownContent += `**Workflow ID:** \`${result.workflow_id}\`\n`;
          markdownContent += `**Status:** ${result.workflow_status === 'complete' ? '✅ Complete' : result.workflow_status}\n\n`;
          if (result.coordinator_response) {
            markdownContent += `## Summary\n\n${result.coordinator_response}\n\n`;
          }
          setMessages(prev => [...prev, { role: 'assistant', content: markdownContent }]);
        }

      } else if (agent === 'drug-repurposing') {
        // Drug repurposing expects drug_name field
        response = await fetch(`${API_BASE_URL}/api/v1/drug-repurposing/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ drug_name: userQuery, full_analysis: true }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        result = await response.json();

        // Format drug repurposing response (API returns DrugRepurposingResult directly)
        let markdownContent = `# Drug Repurposing Analysis\n\n`;
        
        if (result.summary) {
          markdownContent += `## Summary\n\n${result.summary}\n\n`;
        }
        
        // Drug Profile
        if (result.drug_profile) {
          markdownContent += `## Drug Profile\n\n`;
          markdownContent += `- **Drug Name:** ${result.drug_profile.drug_name}\n`;
          if (result.drug_profile.original_indication) markdownContent += `- **Original Indication:** ${result.drug_profile.original_indication}\n`;
          if (result.drug_profile.drug_class) markdownContent += `- **Drug Class:** ${result.drug_profile.drug_class}\n`;
          if (result.drug_profile.mechanism_of_action) markdownContent += `- **Mechanism of Action:** ${result.drug_profile.mechanism_of_action}\n`;
          if (result.drug_profile.smiles) markdownContent += `- **SMILES:** \`${result.drug_profile.smiles}\`\n`;
          markdownContent += `\n`;
        }

        // Repurposing Candidates
        if (result.repurposing_candidates && result.repurposing_candidates.length > 0) {
          markdownContent += `## Repurposing Candidates\n\n`;
          result.repurposing_candidates.forEach((candidate: any, idx: number) => {
            markdownContent += `### ${idx + 1}. ${candidate.predicted_indication}\n\n`;
            markdownContent += `- **Confidence Score:** ${(candidate.confidence_score * 100).toFixed(1)}%\n`;
            markdownContent += `- **Evidence Strength:** ${candidate.evidence_strength}\n`;
            if (candidate.supporting_evidence && candidate.supporting_evidence.length > 0) {
              markdownContent += `- **Supporting Evidence:**\n`;
              candidate.supporting_evidence.forEach((evidence: string) => {
                markdownContent += `  - ${evidence}\n`;
              });
            }
            if (candidate.similar_approved_drugs && candidate.similar_approved_drugs.length > 0) {
              markdownContent += `- **Similar Approved Drugs:** ${candidate.similar_approved_drugs.join(', ')}\n`;
            }
            markdownContent += `\n`;
          });
        }

        // Similar Drugs
        if (result.similar_drugs && result.similar_drugs.length > 0) {
          markdownContent += `## Similar Drugs\n\n`;
          markdownContent += `| Drug Name | Current Indication | Similarity Score |\n`;
          markdownContent += `|-----------|-------------------|------------------|\n`;
          result.similar_drugs.forEach((drug: any) => {
            markdownContent += `| ${drug.drug_name} | ${drug.current_indication} | ${(drug.similarity_score * 100).toFixed(1)}% |\n`;
          });
          markdownContent += `\n`;
        }

        // Clinical Considerations
        if (result.clinical_considerations && result.clinical_considerations.length > 0) {
          markdownContent += `## Clinical Considerations\n\n`;
          result.clinical_considerations.forEach((consideration: string) => {
            markdownContent += `- ${consideration}\n`;
          });
          markdownContent += `\n`;
        }

        // Research Gaps
        if (result.research_gaps && result.research_gaps.length > 0) {
          markdownContent += `## Research Gaps\n\n`;
          result.research_gaps.forEach((gap: string) => {
            markdownContent += `- ${gap}\n`;
          });
          markdownContent += `\n`;
        }

        setMessages(prev => [...prev, { role: 'assistant', content: markdownContent }]);

      } else if (agent === 'deep-research') {
        response = await fetch(`${API_BASE_URL}/api/v1/deep-research/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            query: userQuery,
            mode: 'comprehensive',
            include_clinical_trials: true,
            include_drug_info: true,
            output_format: 'detailed'
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        result = await response.json() as DeepResearchResponse;
        
        // Format deep research response with structured output
        let markdownContent = `# 🔬 Deep Research Report\n\n`;
        markdownContent += `**Research ID:** \`${result.research_id}\`\n`;
        markdownContent += `**Status:** ${result.status === 'complete' ? '✅ Complete' : result.status}\n`;
        markdownContent += `**Execution Time:** ${result.execution_time?.toFixed(2)}s\n\n`;

        // Use structured output if available
        const structured = result.structured_output;
        
        if (structured) {
          // Research Summary
          if (structured.research_summary) {
            markdownContent += `## 📋 Research Summary\n\n${structured.research_summary}\n\n`;
          }
          
          // Evidence Summary
          if (structured.evidence_summary) {
            const evidence = structured.evidence_summary;
            markdownContent += `## 📊 Evidence Summary\n\n`;
            markdownContent += `| Metric | Count |\n|--------|-------|\n`;
            markdownContent += `| Total Papers | ${evidence.total_papers} |\n`;
            markdownContent += `| Clinical Trials | ${evidence.total_trials} |\n`;
            markdownContent += `| Drugs Analyzed | ${evidence.total_drugs} |\n`;
            markdownContent += `\n`;
            
            if (evidence.evidence_quality) {
              const qualityEmoji = evidence.evidence_quality === 'High' ? '🟢' : evidence.evidence_quality === 'Moderate' ? '🟡' : '🟠';
              markdownContent += `**Evidence Quality:** ${qualityEmoji} ${evidence.evidence_quality}\n\n`;
            }
            
            if (evidence.confidence_level) {
              markdownContent += `**Confidence Level:** ${evidence.confidence_level}%\n\n`;
            }
            
            if (evidence.key_evidence_types && evidence.key_evidence_types.length > 0) {
              markdownContent += `**Key Evidence Types:**\n`;
              evidence.key_evidence_types.forEach(t => markdownContent += `- 📄 ${t}\n`);
              markdownContent += `\n`;
            }
          }
          
          // Key Findings
          if (structured.key_findings && structured.key_findings.length > 0) {
            markdownContent += `## 🔑 Key Findings\n\n`;
            structured.key_findings.forEach((finding, idx) => {
              const confEmoji = finding.confidence === 'High' ? '🟢' : finding.confidence === 'Moderate' ? '🟡' : '🟠';
              markdownContent += `### ${idx + 1}. ${finding.finding}\n\n`;
              markdownContent += `**Confidence:** ${confEmoji} ${finding.confidence}\n\n`;
              if (finding.supporting_evidence && finding.supporting_evidence.length > 0) {
                markdownContent += `**Supporting Evidence:**\n`;
                finding.supporting_evidence.slice(0, 3).forEach(e => markdownContent += `- ${e}\n`);
                markdownContent += `\n`;
              }
              if (finding.clinical_relevance) {
                markdownContent += `**Clinical Relevance:** ${finding.clinical_relevance}\n\n`;
              }
            });
          }
          
          // Therapeutic Landscape
          if (structured.therapeutic_landscape) {
            const landscape = structured.therapeutic_landscape;
            markdownContent += `## 💊 Therapeutic Landscape\n\n`;
            
            if (landscape.approved_therapies && landscape.approved_therapies.length > 0) {
              markdownContent += `### ✅ Approved Therapies\n`;
              landscape.approved_therapies.forEach(t => markdownContent += `- ${t}\n`);
              markdownContent += `\n`;
            }
            
            if (landscape.pipeline_therapies && landscape.pipeline_therapies.length > 0) {
              markdownContent += `### 🔬 Pipeline Therapies\n`;
              landscape.pipeline_therapies.forEach(t => markdownContent += `- ${t}\n`);
              markdownContent += `\n`;
            }
            
            if (landscape.emerging_approaches && landscape.emerging_approaches.length > 0) {
              markdownContent += `### 🌟 Emerging Approaches\n`;
              landscape.emerging_approaches.forEach(t => markdownContent += `- ${t}\n`);
              markdownContent += `\n`;
            }
            
            if (landscape.unmet_needs && landscape.unmet_needs.length > 0) {
              markdownContent += `### ⚠️ Unmet Medical Needs\n`;
              landscape.unmet_needs.forEach(t => markdownContent += `- ${t}\n`);
              markdownContent += `\n`;
            }
          }
          
          // Research Gaps
          if (structured.research_gaps && structured.research_gaps.length > 0) {
            markdownContent += `## 🔍 Research Gaps\n\n`;
            markdownContent += `| Gap | Priority | Impact |\n`;
            markdownContent += `|-----|----------|--------|\n`;
            structured.research_gaps.forEach(gap => {
              const priorityEmoji = gap.priority === 'High' ? '🔴' : gap.priority === 'Medium' ? '🟡' : '🟢';
              markdownContent += `| ${gap.gap_description} | ${priorityEmoji} ${gap.priority} | ${gap.potential_impact || 'N/A'} |\n`;
            });
            markdownContent += `\n`;
          }
          
          // Recommendations
          if (structured.recommendations && structured.recommendations.length > 0) {
            markdownContent += `## 💡 Recommendations\n\n`;
            structured.recommendations.forEach((rec, idx) => {
              const strengthEmoji = rec.strength === 'Strong' ? '💪' : rec.strength === 'Moderate' ? '👍' : '🤔';
              markdownContent += `### ${idx + 1}. ${rec.recommendation}\n\n`;
              markdownContent += `**Strength:** ${strengthEmoji} ${rec.strength}\n\n`;
              if (rec.rationale) {
                markdownContent += `**Rationale:** ${rec.rationale}\n\n`;
              }
              if (rec.implementation_steps && rec.implementation_steps.length > 0) {
                markdownContent += `**Implementation Steps:**\n`;
                rec.implementation_steps.forEach((step, i) => markdownContent += `${i + 1}. ${step}\n`);
                markdownContent += `\n`;
              }
              if (rec.timeline) {
                markdownContent += `**Timeline:** ${rec.timeline}\n\n`;
              }
            });
          }
          
          // Critique
          if (structured.critique) {
            const critique = structured.critique;
            markdownContent += `## 📝 Quality Assessment\n\n`;
            
            if (critique.overall_quality) {
              const qualityEmoji = critique.overall_quality === 'High' ? '🟢' : critique.overall_quality === 'Moderate' ? '🟡' : '🟠';
              markdownContent += `**Overall Quality:** ${qualityEmoji} ${critique.overall_quality}\n\n`;
            }
            
            if (critique.strengths && critique.strengths.length > 0) {
              markdownContent += `**Strengths:**\n`;
              critique.strengths.forEach(s => markdownContent += `- ✅ ${s}\n`);
              markdownContent += `\n`;
            }
            
            if (critique.limitations && critique.limitations.length > 0) {
              markdownContent += `**Limitations:**\n`;
              critique.limitations.forEach(l => markdownContent += `- ⚠️ ${l}\n`);
              markdownContent += `\n`;
            }
            
            if (critique.confidence_assessment) {
              markdownContent += `**Confidence Assessment:** ${critique.confidence_assessment}\n\n`;
            }
          }
        }

        // Synthesis (original format fallback)
        if (result.synthesis && !structured?.research_summary) {
          markdownContent += `## 📖 Research Synthesis\n\n${result.synthesis}\n\n`;
        }

        // Papers/Literature
        if (result.papers && result.papers.length > 0) {
          markdownContent += `---\n\n## 📚 Literature Findings (${result.papers.length} papers)\n\n`;
          result.papers.slice(0, 10).forEach((paper: PaperResult, idx: number) => {
            markdownContent += `### ${idx + 1}. ${paper.title}\n\n`;
            if (paper.authors && paper.authors.length > 0) {
              markdownContent += `**Authors:** ${paper.authors.slice(0, 3).join(', ')}${paper.authors.length > 3 ? ' et al.' : ''}\n\n`;
            }
            if (paper.journal) markdownContent += `**Journal:** ${paper.journal}\n\n`;
            if (paper.publication_date) markdownContent += `**Published:** ${paper.publication_date}\n\n`;
            if (paper.abstract) markdownContent += `${paper.abstract.substring(0, 500)}${paper.abstract.length > 500 ? '...' : ''}\n\n`;
            if (paper.pmid) markdownContent += `[📄 PubMed Link](https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}/)\n\n`;
            markdownContent += `---\n\n`;
          });
        }

        // Clinical Trials
        if (result.trials && result.trials.length > 0) {
          markdownContent += `## 🏥 Clinical Trials (${result.trials.length} trials)\n\n`;
          markdownContent += `| Title | NCT ID | Status | Phase |\n`;
          markdownContent += `|-------|--------|--------|-------|\n`;
          result.trials.slice(0, 10).forEach((trial: ClinicalTrialResult) => {
            const statusEmoji = trial.status === 'Completed' ? '✅' : trial.status === 'Recruiting' ? '🔄' : '📋';
            markdownContent += `| ${trial.title?.substring(0, 50)}${trial.title && trial.title.length > 50 ? '...' : ''} | ${trial.nct_id || 'N/A'} | ${statusEmoji} ${trial.status || 'N/A'} | ${trial.phase || 'N/A'} |\n`;
          });
          markdownContent += `\n`;
        }

        // Drugs
        if (result.drugs && result.drugs.length > 0) {
          markdownContent += `## 💊 Drug Information (${result.drugs.length} drugs)\n\n`;
          result.drugs.slice(0, 5).forEach((drug: DrugResult) => {
            const statusEmoji = drug.fda_status === 'Approved' ? '✅' : drug.fda_status === 'In Development' ? '🔬' : '📋';
            markdownContent += `### ${statusEmoji} ${drug.name}\n\n`;
            if (drug.generic_name) markdownContent += `**Generic Name:** ${drug.generic_name}\n\n`;
            if (drug.mechanism) markdownContent += `**Mechanism:** ${drug.mechanism}\n\n`;
            if (drug.fda_status) markdownContent += `**FDA Status:** ${drug.fda_status}\n\n`;
            markdownContent += `---\n\n`;
          });
        }

        // Recommendations (original format fallback)
        if (result.recommendations && result.recommendations.length > 0 && !structured?.recommendations) {
          markdownContent += `## 💡 Recommendations\n\n`;
          result.recommendations.forEach((rec: string) => {
            markdownContent += `- ${rec}\n`;
          });
          markdownContent += `\n`;
        }

        // Research Gaps (original format fallback)
        if (result.gaps && result.gaps.length > 0 && !structured?.research_gaps) {
          markdownContent += `## 🔍 Identified Research Gaps\n\n`;
          result.gaps.forEach((gap: string) => {
            markdownContent += `- ${gap}\n`;
          });
          markdownContent += `\n`;
        }

        setMessages(prev => [...prev, { role: 'assistant', content: markdownContent }]);
      }

    } catch (err) {
      console.error(`${agent} error:`, err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `⚠️ **Error:** ${err instanceof Error ? err.message : 'An error occurred while processing your request.'}\n\nPlease try again or check if the backend service is running.`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const mockResponses = {
    'drug-discovery': `# Novel KRAS G12C Inhibitor Discovery Analysis

## Executive Summary
Our AI-powered analysis has identified **23 promising novel compounds** with potential KRAS G12C inhibitory activity based on structural similarity, binding affinity predictions, and ADMET properties.

## Top Candidate Compounds

### Compound DRG-2847
- **Predicted IC50**: 8.2 nM (vs sotorasib 6.1 nM)
- **Binding Mode**: Covalent modification of Cys12
- **Key Features**:
  - Enhanced selectivity vs KRAS wild-type (>500-fold)
  - Improved blood-brain barrier penetration (LogP: 3.2)
  - Favorable metabolic stability (T½: 4.2 hours)
  
**Molecular Structure**: Quinazoline-based scaffold with novel C7 substitution

**Predicted Efficacy**: 
- Cell viability inhibition in H358 cells: IC50 ~12 nM
- Selectivity index: >400 (KRAS G12C vs G12D)

---

### Compound DRG-3192
- **Predicted IC50**: 11.5 nM
- **Mechanism**: Allosteric pocket binding + covalent warhead
- **Differentiation**: 
  - Dual inhibition of KRAS-SOS interaction
  - Reduced off-target kinase activity (<10% at 1µM)
  - Superior aqueous solubility (78 µg/mL)

---

## Structure-Activity Relationship (SAR) Insights

Key structural features associated with improved activity:

1. **Warhead Chemistry**: Acrylamide derivatives show superior reactivity-selectivity balance
2. **Scaffold Optimization**: Bicyclic aromatic cores improve binding pocket occupancy
3. **Linker Design**: 3-4 carbon linkers optimize covalent bond formation geometry

## ADMET Profile Comparison

| Compound | Solubility | Permeability | CYP Inhibition | hERG Risk | Brain Penetration |
|----------|------------|--------------|----------------|-----------|-------------------|
| DRG-2847 | High | Moderate | Low | Low | High |
| DRG-3192 | Very High | High | Very Low | Very Low | Moderate |
| Sotorasib | Moderate | Moderate | Moderate | Low | Low |

## Recommended Next Steps

### Immediate Actions
1. **Synthesis & Validation**: Synthesize top 5 candidates for in vitro validation
2. **Cell Line Testing**: H358, H2122, MIA PaCa-2 (KRAS G12C+ lines)
3. **Selectivity Profiling**: Test against KRAS G12D, G12V, and WT

### Development Pathway
- **Timeline**: 18-24 months to IND
- **Investment**: $12-15M for preclinical development
- **Success Probability**: 42% based on target validation and scaffold novelty

### Strategic Considerations
- Patent landscape analysis shows freedom to operate in quinazoline space
- Potential first-in-class opportunity for CNS penetrant KRAS inhibitor
- Partnership opportunities with academic centers for validation

---

## Data Sources & Confidence
- **Molecular Docking**: AutoDock Vina, Schrödinger Glide (Confidence: 87%)
- **ADMET Prediction**: SwissADME, pkCSM (Confidence: 82%)
- **SAR Analysis**: 847 known KRAS inhibitors from ChEMBL (Confidence: 91%)
- **Literature Mining**: 2,341 relevant publications (2019-2024)

*This analysis was generated by DrugIQ's AI-powered drug discovery engine. All predictions should be validated experimentally.*`,
    
    'drug-repurposing': `# Metformin Repurposing Opportunity: Alzheimer's Disease

## Analysis Overview
Our comprehensive AI analysis has evaluated **metformin** for potential repurposing in **Alzheimer's disease** based on mechanistic rationale, epidemiological data, and clinical evidence.

## Mechanistic Rationale

### Primary Mechanisms of Action
1. **AMPK Activation**: Enhances cellular energy metabolism and autophagy
2. **mTOR Inhibition**: Reduces protein aggregation and tau hyperphosphorylation  
3. **Anti-inflammatory Effects**: Decreases neuroinflammation via NF-κB suppression
4. **Metabolic Benefits**: Improves insulin sensitivity and glucose metabolism

### Alzheimer's-Relevant Pathways
- **Amyloid-β Clearance**: AMPK activation promotes Aβ degradation
- **Tau Pathology**: mTOR inhibition reduces tau phosphorylation
- **Mitochondrial Function**: Improves mitochondrial biogenesis and function
- **Blood-Brain Barrier**: Moderate BBB penetration (Brain/Plasma ratio: 0.3-0.4)

---

## Epidemiological Evidence

### Population Studies Analyzed: 18 cohorts (N=247,892)

**Key Findings**:
- Metformin use associated with **24% reduction** in AD incidence (HR: 0.76, 95% CI: 0.68-0.84)
- Dose-response relationship observed (>2 years use shows greater benefit)
- Effect size comparable to or better than current AD drugs

**Meta-Analysis Results**:
- Pooled hazard ratio: 0.78 (95% CI: 0.71-0.86, p<0.001)
- Heterogeneity: I² = 34% (moderate)
- Publication bias: Not detected (Egger's test p=0.42)

---

## Clinical Data Review

### Completed Studies
1. **Singapore Epidemiological Study** (N=7,156)
   - 3.8-year follow-up
   - 26% reduced AD risk in metformin users
   
2. **Taiwan National Database** (N=12,378)
   - 4.2-year follow-up
   - Improved cognitive scores in metformin users

### Ongoing Trials
- **NCT04098666**: Metformin 2000mg/day vs placebo (Phase II, N=80)
- **NCT04098692**: Metformin + lifestyle intervention (Phase II, N=120)
- **Expected completion**: Q3 2025

---

## Safety & Feasibility Assessment

### Safety Profile
✅ **Excellent established safety record** (>60 years clinical use)  
✅ **Well-tolerated** in elderly populations  
⚠️ **Contraindications**: eGFR <30 mL/min, severe hepatic impairment  
⚠️ **Common side effects**: GI symptoms (10-15%), B12 deficiency (long-term)

### Regulatory Pathway
- **Advantage**: Extensive safety database reduces regulatory burden
- **Timeline**: 18-24 months to pivotal trial initiation
- **Estimated cost**: $15-20M for Phase II proof-of-concept

---

## Market Opportunity

### Target Population
- **Mild Cognitive Impairment**: 46M globally
- **Early-stage AD**: 22M globally
- **Prevention (high-risk)**: 180M globally

### Competitive Landscape
- Limited effective therapies for early/prodromal AD
- Metformin's safety profile advantages vs. anti-amyloid antibodies
- Potential combination therapy opportunities

### Market Potential
- **Peak sales projection**: $2.1-3.8B (prevention + early treatment)
- **Generic competition**: Limited differentiation opportunity
- **Formulation improvements**: Extended-release, CNS-optimized versions

---

## Strategic Recommendations

### Priority Actions
1. ✅ **Initiate Phase II proof-of-concept** trial in MCI population
2. ✅ **Develop CNS-optimized formulation** (improved BBB penetration)
3. ✅ **Establish biomarker strategy** (tau-PET, plasma p-tau217)

### Development Strategy
- **Target indication**: MCI due to AD (biomarker-positive)
- **Primary endpoint**: Change in CDR-SB at 18 months
- **Biomarker endpoints**: Plasma p-tau217, Aβ42/40 ratio
- **Trial design**: Enriched population (APOE4 carriers, T2D comorbidity)

### Partnership Opportunities
- Academic centers with AD cohorts
- Diagnostics companies (biomarker integration)
- Digital health platforms (remote monitoring)

---

## Confidence Assessment
- **Mechanistic plausibility**: 89% (strong preclinical evidence)
- **Epidemiological support**: 91% (consistent across studies)
- **Clinical feasibility**: 94% (established safety, accessible)
- **Market opportunity**: 76% (competitive landscape uncertainty)

**Overall Repurposing Recommendation**: ⭐⭐⭐⭐⭐ **Highly Recommended**

*Analysis based on 2,341 publications, 18 epidemiological studies, and 4 ongoing clinical trials.*`,

    'deep-research': `# Comprehensive Research Analysis: PD-1/PD-L1 Checkpoint Inhibitors

## Literature Analysis Summary
**Total Publications Analyzed**: 12,847 peer-reviewed articles (2014-2024)  
**Clinical Trials Reviewed**: 1,284 studies (all phases)  
**Patents Analyzed**: 3,462 patent families  

---

## Key Research Findings

### 1. Mechanism of Action Advances

Recent structural biology studies have elucidated the molecular basis of PD-1/PD-L1 interaction with unprecedented detail:

**Critical Discoveries (2022-2024)**:
- Crystal structure of PD-1/pembrolizumab complex reveals unique binding epitope (Science, 2023)
- Glycosylation patterns on PD-L1 affect antibody binding affinity by up to 40-fold (Nature, 2023)
- Novel non-canonical PD-L1 signaling pathway identified in immune cells (Cell, 2024)

**Implications**: Next-generation inhibitors may target glycosylation sites or non-canonical pathways for enhanced efficacy.

---

### 2. Biomarker Evolution

The field has progressed beyond simple PD-L1 expression:

**Emerging Predictive Biomarkers**:
1. **Tumor Mutational Burden (TMB)**: ≥10 mutations/Mb predicts response (HR: 0.64)
2. **Interferon-γ Gene Signature**: 18-gene panel shows 78% PPV
3. **Gut Microbiome Composition**: Akkermansia muciniphila associated with response
4. **Circulating Tumor DNA**: ctDNA clearance predicts long-term outcomes
5. **Tertiary Lymphoid Structures**: TLS presence correlates with OS benefit

**Meta-Analysis Results** (47 studies, N=18,429):
- PD-L1 ≥50%: ORR 42% vs 18% (PD-L1 <1%)
- TMB-high: ORR 38% vs 12% (TMB-low)
- Combined biomarkers improve prediction accuracy to 72%

---

### 3. Resistance Mechanisms

Comprehensive analysis of resistance has identified multiple pathways:

**Primary Resistance** (de novo):
- Loss of MHC class I expression (23% of resistant cases)
- JAK1/2 mutations disrupting IFN-γ signaling (18%)
- PTEN loss and PI3K pathway activation (31%)
- T-cell exclusion due to stroma/CAF barriers (42%)

**Acquired Resistance** (developed on treatment):
- Clonal evolution with loss of neoantigens (34%)
- Upregulation of alternative checkpoints (LAG-3, TIM-3) (41%)
- Epithelial-mesenchymal transition (28%)

**Novel Insights**: Single-cell RNA-seq reveals dynamic resistance states that may be reversible with combination therapies.

---

### 4. Combination Strategy Evidence

**Most Promising Combinations** (based on Phase II/III data):

| Combination | N Studies | ORR | mPFS | mOS | Key Findings |
|------------|-----------|-----|------|-----|--------------|
| PD-1 + CTLA-4 | 47 | 58% | 11.5m | 22.3m | High toxicity (60% G3/4) |
| PD-1 + Chemo | 89 | 64% | 9.2m | 18.7m | Synergistic in multiple tumors |
| PD-1 + LAG-3 | 12 | 43% | 10.1m | NR | Lower toxicity profile |
| PD-1 + VEGF | 34 | 52% | 8.9m | 19.2m | Overcomes immunosuppression |

**Mechanistic Synergies**:
- Chemotherapy increases neoantigen release and T-cell priming
- Anti-VEGF normalizes vasculature and improves T-cell infiltration
- Dual checkpoint blockade prevents compensatory upregulation

---

### 5. Toxicity Management Advances

**Immune-Related Adverse Events (irAEs)**: Sophisticated understanding emerging

**Predictive Markers for irAEs**:
- Baseline autoantibodies predict endocrine toxicity (AUC: 0.81)
- Gut microbiome dysbiosis predicts colitis risk
- Genetic variants in CTLA4 and IL6 genes

**Management Innovations**:
- Early corticosteroid intervention reduces severe irAE incidence by 40%
- Selective immunosuppression (TNF-α, IL-6 inhibitors) doesn't compromise efficacy
- Rechallenge protocols show 70% success rate after irAE resolution

---

### 6. Novel Delivery Strategies

**Emerging Approaches**:
1. **Bispecific Antibodies**: PD-1 x TGF-β trap shows promise in cold tumors
2. **Antibody-Drug Conjugates**: PD-L1-directed ADCs deliver cytotoxic payload
3. **mRNA-Encoded Antibodies**: Local production reduces systemic toxicity
4. **Bacterial Delivery Systems**: Engineered microbes produce anti-PD-L1 intratumorally

---

## Patent Landscape Analysis

**Key Patent Families**:
- Pembrolizumab core patents expire 2028-2031 (formulation patents extend to 2033)
- 1,247 combination therapy patents filed (2020-2024)
- Novel mechanisms (LAG-3, TIGIT) have strong IP protection through 2037

**Freedom to Operate**:
- Biosimilar space increasingly crowded (12 Phase III candidates)
- Combination patents create complex licensing landscape
- Novel mechanisms offer clearest IP pathway

---

## Future Directions

**High-Priority Research Areas**:
1. Mechanisms of hyperprogression (accelerated disease on immunotherapy)
2. Optimal sequencing of immunotherapy and targeted therapy
3. Immunotherapy in immunologically "cold" tumors
4. Predictive algorithms integrating multi-omics data
5. Strategies to overcome T-cell exhaustion

**Funding Trends**:
- NIH funding for cancer immunotherapy: $2.1B (2024)
- Industry R&D investment: $18.4B globally
- Academic-industry partnerships increasing 34% year-over-year

---

## Confidence & Data Quality

**Source Quality Assessment**:
- ⭐⭐⭐⭐⭐ Tier 1 journals (Nature, Science, Cell, NEJM): 2,847 papers
- ⭐⭐⭐⭐ High-impact oncology journals: 6,234 papers
- ⭐⭐⭐ Specialty journals: 3,766 papers

**Data Reliability**: 94% (based on study quality, replication, and consistency)

*This deep research analysis synthesized 12,847 publications, 1,284 clinical trials, and 3,462 patents using DrugIQ's AI-powered research engine.*`
  };

  return (
    <>
      <div className="flex-1 overflow-auto p-6">
        {!hasQuery && messages.length === 0 ? (
          <div className="max-w-3xl mx-auto text-center py-20">
            <div className={`w-20 h-20 ${config.bgColor} rounded-full flex items-center justify-center mx-auto mb-6`}>
              <Sparkles className={`w-10 h-10 ${config.color}`} />
            </div>
            <h3 className="text-2xl mb-4">{config.name}</h3>
            <p className="text-gray-400 mb-8">{config.description}</p>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <div key={index}>
                {message.role === 'user' ? (
                  <div className="flex justify-end">
                    <div className="max-w-2xl bg-gradient-to-br from-[#4ade80] to-[#22d3ee] text-white px-6 py-4 rounded-2xl shadow-lg">
                      <p>{message.content}</p>
                    </div>
                  </div>
                ) : (
                  <div className="flex gap-4">
                    <div className={`w-10 h-10 ${config.bgColor} rounded-full flex items-center justify-center flex-shrink-0`}>
                      <Sparkles className={`w-5 h-5 ${config.color}`} />
                    </div>
                    <div className="flex-1 bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-2xl p-6 shadow-lg overflow-hidden">
                      <div className="prose prose-invert prose-sm max-w-none 
                        prose-headings:text-white prose-headings:font-semibold
                        prose-h1:text-2xl prose-h1:mb-4 prose-h1:mt-0 prose-h1:border-b prose-h1:border-[#2a3f5f] prose-h1:pb-2
                        prose-h2:text-xl prose-h2:mb-3 prose-h2:mt-6 prose-h2:text-[#4ade80]
                        prose-h3:text-lg prose-h3:mb-2 prose-h3:mt-4 prose-h3:text-[#22d3ee]
                        prose-p:text-gray-300 prose-p:leading-relaxed prose-p:mb-3
                        prose-ul:text-gray-300 prose-ul:my-2
                        prose-ol:text-gray-300 prose-ol:my-2
                        prose-li:text-gray-300 prose-li:my-1
                        prose-strong:text-white prose-strong:font-semibold
                        prose-code:text-[#4ade80] prose-code:bg-[#1a2533] prose-code:px-1 prose-code:py-0.5 prose-code:rounded
                        prose-pre:bg-[#0a1628] prose-pre:border prose-pre:border-[#2a3f5f] prose-pre:rounded-lg
                        prose-table:border-collapse prose-table:w-full
                        prose-th:bg-[#1a2533] prose-th:border prose-th:border-[#2a3f5f] prose-th:px-3 prose-th:py-2 prose-th:text-left prose-th:text-white
                        prose-td:border prose-td:border-[#2a3f5f] prose-td:px-3 prose-td:py-2 prose-td:text-gray-300
                        prose-hr:border-[#2a3f5f] prose-hr:my-6
                        prose-blockquote:border-l-4 prose-blockquote:border-[#4ade80] prose-blockquote:pl-4 prose-blockquote:italic prose-blockquote:text-gray-400
                        prose-a:text-[#22d3ee] prose-a:no-underline hover:prose-a:underline">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {message.content}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex gap-4">
                <div className={`w-10 h-10 ${config.bgColor} rounded-full flex items-center justify-center flex-shrink-0`}>
                  <Sparkles className={`w-5 h-5 ${config.color}`} />
                </div>
                <div className="flex-1 bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-2xl p-6 shadow-lg">
                  <div className="flex items-center gap-3">
                    <Loader2 className={`w-5 h-5 ${config.color} animate-spin`} />
                    <span className="text-gray-400">
                      {agent === 'drug-discovery' && 'Running drug discovery workflow...'}
                      {agent === 'drug-repurposing' && 'Analyzing drug repurposing opportunities...'}
                      {agent === 'deep-research' && 'Conducting deep research analysis...'}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">This may take a few moments</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-[#2a3f5f] bg-gradient-to-r from-[#0f1722] to-[#1a2533] p-6 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-xl p-2 flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
              placeholder={`Ask ${config.name} a question...`}
              className="flex-1 bg-transparent px-4 py-2 outline-none"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading}
              className="bg-gradient-to-r from-[#4ade80] to-[#22d3ee] hover:from-[#22d3ee] hover:to-[#4ade80] transition-all rounded-lg px-4 py-2 flex items-center gap-2 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
