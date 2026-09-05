import { Download, Target, Beaker, AlertTriangle, CheckCircle, TrendingUp, Loader2, Shield, Award, FileText, Activity } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Types matching backend schema
export interface TargetInfo {
  target_name: string;
  target_type?: string;
  gene_symbol?: string;
  uniprot_id?: string;
  validation_score?: number;
  disease_association?: string;
  druggability_assessment?: string;
  known_modulators?: string[];
}

export interface LeadCompound {
  compound_id: string;
  smiles?: string;
  molecular_weight?: number;
  logp?: number;
  binding_affinity?: string;
  lead_score?: number;
  source?: string;
}

export interface OptimizationResult {
  optimized_compound_id: string;
  modifications?: string[];
  improved_properties?: Record<string, string>;
  admet_profile?: Record<string, string>;
  optimization_score?: number;
  synthetic_accessibility?: number;
}

export interface PreclinicalData {
  candidate_id: string;
  toxicity_assessment?: Record<string, string>;
  efficacy_data?: Record<string, string>;
  pharmacokinetics?: Record<string, string>;
  safety_score?: number;
  efficacy_score?: number;
  recommendation?: string;
  risk_factors?: string[];
}

export interface RiskAssessment {
  risk_category: string;
  source_agent: string;
  severity: string;
  impact: string;
  mitigation?: string;
}

export interface StrategicDecision {
  recommendation: string;
  scientific_merit_score: number;
  technical_feasibility_score: number;
  safety_profile_score: number;
  commercial_viability_score: number;
  overall_score: number;
  critical_success_factors?: string[];
  red_flags?: string[];
}

export interface ActionItem {
  action: string;
  timeframe: string;
  priority: string;
  responsible_party?: string;
}

export interface DrugDiscoveryData {
  workflow_id: string;
  query: string;
  workflow_status: string;
  execution_start?: string;
  execution_end?: string;
  target_discovery?: TargetInfo;
  lead_compounds?: LeadCompound[];
  optimization_results?: OptimizationResult[];
  preclinical_data?: PreclinicalData;
  risk_matrix?: RiskAssessment[];
  strategic_decision?: StrategicDecision;
  action_roadmap?: ActionItem[];
  executive_summary?: string;
  cross_agent_insights?: string[];
  coordinator_response?: string;
}

interface DrugDiscoveryViewProps {
  data: DrugDiscoveryData | null;
  isLoading: boolean;
  error: string | null;
}

// Score bar component
const ScoreBar = ({ label, score, max = 10 }: { label: string; score: number; max?: number }) => {
  const percentage = (score / max) * 100;
  const getColor = () => {
    if (percentage >= 70) return 'bg-green-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-white font-semibold">{score}/{max}</span>
      </div>
      <div className="h-2 bg-[#0a1628] rounded-full overflow-hidden">
        <div className={`h-full ${getColor()} rounded-full transition-all duration-500`} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
};

export function DrugDiscoveryView({ data, isLoading, error }: DrugDiscoveryViewProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 mx-auto mb-4 text-green-400 animate-spin" />
          <p className="text-gray-400">Running drug discovery workflow...</p>
          <p className="text-xs text-gray-500 mt-2">Analyzing targets, leads, and preclinical data</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-red-400" />
          <p className="text-gray-400">Error in drug discovery workflow</p>
          <p className="text-xs text-red-400 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  // No data state
  if (!data) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-gray-400">
          <Beaker className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>Submit a query to start drug discovery analysis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-cyan-500 rounded-xl flex items-center justify-center">
              <Beaker className="w-5 h-5 text-white" />
            </div>
            Drug Discovery Report
          </h3>
          <p className="text-sm text-gray-400 mt-1">Workflow ID: {data.workflow_id}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
            data.workflow_status === 'complete' 
              ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
              : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
          }`}>
            {data.workflow_status === 'complete' ? '✓ Complete' : data.workflow_status}
          </span>
          <button className="flex items-center gap-2 bg-gradient-to-r from-[#4ade80] to-[#22d3ee] px-4 py-2 rounded-lg hover:from-[#22d3ee] hover:to-[#4ade80] transition-all shadow-lg text-sm">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* Executive Summary */}
      {data.executive_summary && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-400" />
            Executive Summary
          </h4>
          <div className="text-gray-300 leading-relaxed prose prose-invert prose-sm max-w-none 
            prose-headings:text-white prose-headings:font-semibold prose-headings:mt-4 prose-headings:mb-2
            prose-p:text-gray-300 prose-p:my-2
            prose-strong:text-white prose-strong:font-semibold
            prose-ul:my-2 prose-li:text-gray-300 prose-li:my-1
            prose-ol:my-2
            prose-a:text-cyan-400 prose-a:no-underline hover:prose-a:underline
            prose-code:text-cyan-300 prose-code:bg-[#1a2533] prose-code:px-1 prose-code:py-0.5 prose-code:rounded
            prose-pre:bg-[#0f1722] prose-pre:border prose-pre:border-[#2a3f5f] prose-pre:rounded-lg">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {(data.executive_summary || '').replace(/^```markdown\n?/, '').replace(/\n?```$/, '')}
            </ReactMarkdown>
          </div>
        </div>
      )}

      {/* Strategic Decision */}
      {data.strategic_decision && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-purple-400" />
            Strategic Decision
          </h4>
          
          {/* Recommendation Badge */}
          <div className="flex items-center gap-4 mb-6">
            <div className={`px-4 py-2 rounded-lg text-lg font-bold ${
              data.strategic_decision.recommendation === 'GO' 
                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                : data.strategic_decision.recommendation === 'CONDITIONAL_GO'
                ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                : 'bg-red-500/20 text-red-400 border border-red-500/30'
            }`}>
              {data.strategic_decision.recommendation === 'GO' && '🟢 GO'}
              {data.strategic_decision.recommendation === 'CONDITIONAL_GO' && '🟡 CONDITIONAL GO'}
              {data.strategic_decision.recommendation === 'NO_GO' && '🔴 NO-GO'}
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-white">{data.strategic_decision.overall_score}</p>
              <p className="text-xs text-gray-400">Overall Score /10</p>
            </div>
          </div>

          {/* Score Bars */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            <ScoreBar label="Scientific Merit" score={data.strategic_decision.scientific_merit_score} />
            <ScoreBar label="Technical Feasibility" score={data.strategic_decision.technical_feasibility_score} />
            <ScoreBar label="Safety Profile" score={data.strategic_decision.safety_profile_score} />
            <ScoreBar label="Commercial Viability" score={data.strategic_decision.commercial_viability_score} />
          </div>

          {/* Success Factors & Red Flags */}
          <div className="grid grid-cols-2 gap-6">
            {data.strategic_decision.critical_success_factors && data.strategic_decision.critical_success_factors.length > 0 && (
              <div>
                <h5 className="mb-3 flex items-center gap-2 text-sm text-green-400">
                  <CheckCircle className="w-4 h-4" />
                  Critical Success Factors
                </h5>
                <div className="space-y-2">
                  {data.strategic_decision.critical_success_factors.map((factor, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-green-400 rounded-full mt-1.5 flex-shrink-0"></div>
                      <p className="text-xs text-gray-300">{factor}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {data.strategic_decision.red_flags && data.strategic_decision.red_flags.length > 0 && (
              <div>
                <h5 className="mb-3 flex items-center gap-2 text-sm text-red-400">
                  <AlertTriangle className="w-4 h-4" />
                  Red Flags
                </h5>
                <div className="space-y-2">
                  {data.strategic_decision.red_flags.map((flag, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-red-400 rounded-full mt-1.5 flex-shrink-0"></div>
                      <p className="text-xs text-gray-300">{flag}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Target Discovery */}
      {data.target_discovery && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-cyan-400" />
            Target Discovery
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
              <p className="text-xs text-gray-400 mb-1">Target Name</p>
              <p className="text-white font-semibold">{data.target_discovery.target_name}</p>
            </div>
            {data.target_discovery.target_type && (
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">Type</p>
                <p className="text-white">{data.target_discovery.target_type}</p>
              </div>
            )}
            {data.target_discovery.gene_symbol && (
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">Gene Symbol</p>
                <p className="text-cyan-400 font-mono">{data.target_discovery.gene_symbol}</p>
              </div>
            )}
            {data.target_discovery.uniprot_id && (
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">UniProt ID</p>
                <p className="text-cyan-400 font-mono">{data.target_discovery.uniprot_id}</p>
              </div>
            )}
            {data.target_discovery.validation_score && (
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">Validation Score</p>
                <p className="text-green-400 font-bold text-xl">{data.target_discovery.validation_score}/10</p>
              </div>
            )}
            {data.target_discovery.druggability_assessment && (
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">Druggability</p>
                <p className="text-white">{data.target_discovery.druggability_assessment}</p>
              </div>
            )}
          </div>
          {data.target_discovery.disease_association && (
            <div className="mt-4 bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
              <p className="text-xs text-gray-400 mb-1">Disease Association</p>
              <p className="text-gray-300">{data.target_discovery.disease_association}</p>
            </div>
          )}
        </div>
      )}

      {/* Lead Compounds */}
      {data.lead_compounds && data.lead_compounds.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <Beaker className="w-5 h-5 text-purple-400" />
            Lead Compounds ({data.lead_compounds.length})
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#2a3f5f]">
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Compound ID</th>
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">MW</th>
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">LogP</th>
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Binding Affinity</th>
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Lead Score</th>
                </tr>
              </thead>
              <tbody>
                {data.lead_compounds.map((compound, idx) => (
                  <tr key={idx} className="border-b border-[#2a3f5f]/50 hover:bg-[#1a2533]">
                    <td className="py-3 px-4 text-cyan-400 font-mono text-sm">{compound.compound_id}</td>
                    <td className="py-3 px-4 text-gray-300 text-sm">{compound.molecular_weight?.toFixed(1) || 'N/A'}</td>
                    <td className="py-3 px-4 text-gray-300 text-sm">{compound.logp?.toFixed(2) || 'N/A'}</td>
                    <td className="py-3 px-4 text-gray-300 text-sm">{compound.binding_affinity || 'N/A'}</td>
                    <td className="py-3 px-4">
                      {compound.lead_score ? (
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          compound.lead_score >= 7 ? 'bg-green-500/20 text-green-400' :
                          compound.lead_score >= 5 ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          {compound.lead_score}/10
                        </span>
                      ) : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Risk Matrix */}
      {data.risk_matrix && data.risk_matrix.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-400" />
            Risk Assessment
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#2a3f5f]">
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Category</th>
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Source</th>
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Severity</th>
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Impact</th>
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Mitigation</th>
                </tr>
              </thead>
              <tbody>
                {data.risk_matrix.map((risk, idx) => (
                  <tr key={idx} className="border-b border-[#2a3f5f]/50 hover:bg-[#1a2533]">
                    <td className="py-3 px-4 text-white text-sm">{risk.risk_category}</td>
                    <td className="py-3 px-4 text-gray-300 text-sm">{risk.source_agent}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        risk.severity === 'High' ? 'bg-red-500/20 text-red-400' :
                        risk.severity === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-green-500/20 text-green-400'
                      }`}>
                        {risk.severity}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-300 text-sm">{risk.impact}</td>
                    <td className="py-3 px-4 text-gray-300 text-sm">{risk.mitigation || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Action Roadmap */}
      {data.action_roadmap && data.action_roadmap.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            Action Roadmap
          </h4>
          <div className="space-y-6">
            {/* Immediate */}
            {data.action_roadmap.filter(a => a.timeframe === 'immediate').length > 0 && (
              <div>
                <h5 className="text-sm text-gray-400 mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 bg-red-400 rounded-full"></span>
                  Immediate (0-3 months)
                </h5>
                <div className="space-y-2">
                  {data.action_roadmap.filter(a => a.timeframe === 'immediate').map((action, idx) => (
                    <div key={idx} className="flex items-start gap-3 bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        action.priority === 'High' ? 'bg-red-500/20 text-red-400' :
                        action.priority === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {action.priority}
                      </span>
                      <div className="flex-1">
                        <p className="text-sm text-gray-200">{action.action}</p>
                        {action.responsible_party && (
                          <p className="text-xs text-gray-500 mt-1">→ {action.responsible_party}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Near-term */}
            {data.action_roadmap.filter(a => a.timeframe === 'near_term').length > 0 && (
              <div>
                <h5 className="text-sm text-gray-400 mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 bg-yellow-400 rounded-full"></span>
                  Near-term (3-12 months)
                </h5>
                <div className="space-y-2">
                  {data.action_roadmap.filter(a => a.timeframe === 'near_term').map((action, idx) => (
                    <div key={idx} className="flex items-start gap-3 bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        action.priority === 'High' ? 'bg-red-500/20 text-red-400' :
                        action.priority === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {action.priority}
                      </span>
                      <div className="flex-1">
                        <p className="text-sm text-gray-200">{action.action}</p>
                        {action.responsible_party && (
                          <p className="text-xs text-gray-500 mt-1">→ {action.responsible_party}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Long-term */}
            {data.action_roadmap.filter(a => a.timeframe === 'long_term').length > 0 && (
              <div>
                <h5 className="text-sm text-gray-400 mb-3 flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                  Long-term (1-3 years)
                </h5>
                <div className="space-y-2">
                  {data.action_roadmap.filter(a => a.timeframe === 'long_term').map((action, idx) => (
                    <div key={idx} className="flex items-start gap-3 bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        action.priority === 'High' ? 'bg-red-500/20 text-red-400' :
                        action.priority === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {action.priority}
                      </span>
                      <div className="flex-1">
                        <p className="text-sm text-gray-200">{action.action}</p>
                        {action.responsible_party && (
                          <p className="text-xs text-gray-500 mt-1">→ {action.responsible_party}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Cross-Agent Insights */}
      {data.cross_agent_insights && data.cross_agent_insights.length > 0 && (
        <div className="bg-gradient-to-br from-[#4ade80]/5 to-[#22d3ee]/5 border border-[#4ade80]/30 rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-green-400" />
            Key Insights
          </h4>
          <div className="space-y-3">
            {data.cross_agent_insights.map((insight, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <div className="w-6 h-6 bg-gradient-to-br from-[#4ade80] to-[#22d3ee] rounded-full flex items-center justify-center flex-shrink-0 text-xs text-white">
                  {idx + 1}
                </div>
                <p className="text-sm text-gray-300 flex-1">{insight}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
