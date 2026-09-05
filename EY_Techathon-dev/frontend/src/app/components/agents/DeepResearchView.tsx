import { Download, FileText, AlertTriangle, CheckCircle, TrendingUp, Loader2, Activity, Beaker, Target, BookOpen, Lightbulb } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Types matching backend schema
export interface EvidenceSummary {
  total_papers: number;
  total_trials: number;
  total_drugs: number;
  evidence_quality?: string;
  confidence_level?: number;
  key_evidence_types?: string[];
}

export interface KeyFinding {
  finding: string;
  source_type: string;
  confidence: string;
  supporting_evidence?: string[];
  clinical_relevance?: string;
}

export interface TherapeuticLandscape {
  current_standard_of_care?: string;
  approved_therapies?: string[];
  emerging_therapies?: string[];
  pipeline_therapies?: string[];
  unmet_needs?: string[];
  market_trends?: string;
}

export interface ResearchGap {
  gap_description: string;
  priority: string;
  potential_impact?: string;
  suggested_approach?: string;
}

export interface Recommendation {
  recommendation: string;
  strength: string;
  rationale?: string;
  implementation_steps?: string[];
  timeline?: string;
}

export interface CritiqueResult {
  overall_quality?: string;
  strengths?: string[];
  limitations?: string[];
  confidence_assessment?: string;
}

export interface PaperResult {
  title: string;
  authors?: string[];
  journal?: string;
  publication_date?: string;
  abstract?: string;
  pmid?: string;
}

export interface ClinicalTrialResult {
  title?: string;
  nct_id?: string;
  status?: string;
  phase?: string;
  conditions?: string[];
}

export interface DrugResult {
  name: string;
  generic_name?: string;
  mechanism?: string;
  fda_status?: string;
}

export interface DeepResearchData {
  research_id: string;
  query: string;
  status: string;
  execution_time?: number;
  papers?: PaperResult[];
  trials?: ClinicalTrialResult[];
  drugs?: DrugResult[];
  evidence_summary?: EvidenceSummary;
  key_findings?: KeyFinding[];
  therapeutic_landscape?: TherapeuticLandscape;
  research_summary?: string;
  synthesis?: string;
  research_gaps?: ResearchGap[];
  recommendations?: Recommendation[];
  critique?: CritiqueResult;
}

interface DeepResearchViewProps {
  data: DeepResearchData | null;
  isLoading: boolean;
  error: string | null;
}

export function DeepResearchView({ data, isLoading, error }: DeepResearchViewProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 mx-auto mb-4 text-purple-400 animate-spin" />
          <p className="text-gray-400">Conducting deep research analysis...</p>
          <p className="text-xs text-gray-500 mt-2">Searching literature, trials, and drug databases</p>
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
          <p className="text-gray-400">Error in research analysis</p>
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
          <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>Submit a query to start deep research</p>
        </div>
      </div>
    );
  }

  // Compute evidence summary from arrays if not provided
  const evidenceSummary = data.evidence_summary || {
    total_papers: data.papers?.length || 0,
    total_trials: data.trials?.length || 0,
    total_drugs: data.drugs?.length || 0,
    confidence_level: data.status === 'complete' ? 85 : 0,
  };

  // Check if we have any content to display
  const hasPapers = data.papers && data.papers.length > 0;
  const hasTrials = data.trials && data.trials.length > 0;
  const hasDrugs = data.drugs && data.drugs.length > 0;
  const hasSynthesis = data.synthesis || data.research_summary;
  const hasAnyContent = hasPapers || hasTrials || hasDrugs || hasSynthesis;

  return (
    <div className="space-y-6 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            Deep Research Report
          </h3>
          <p className="text-sm text-gray-400 mt-1">Research ID: {data.research_id}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
            data.status === 'complete' 
              ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
              : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
          }`}>
            {data.status === 'complete' ? '✓ Complete' : data.status}
          </span>
          {data.execution_time && (
            <span className="text-sm text-gray-400">{data.execution_time.toFixed(1)}s</span>
          )}
          <button className="flex items-center gap-2 bg-gradient-to-r from-[#4ade80] to-[#22d3ee] px-4 py-2 rounded-lg hover:from-[#22d3ee] hover:to-[#4ade80] transition-all shadow-lg text-sm">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* Evidence Summary Stats - Always show if we have any data */}
      {hasAnyContent && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-500/10 to-transparent border border-blue-500/30 rounded-xl p-4 text-center">
            <FileText className="w-8 h-8 text-blue-400 mx-auto mb-2" />
            <p className="text-3xl font-bold text-white">{evidenceSummary.total_papers}</p>
            <p className="text-xs text-gray-400">Papers Found</p>
          </div>
          <div className="bg-gradient-to-br from-green-500/10 to-transparent border border-green-500/30 rounded-xl p-4 text-center">
            <Activity className="w-8 h-8 text-green-400 mx-auto mb-2" />
            <p className="text-3xl font-bold text-white">{evidenceSummary.total_trials}</p>
            <p className="text-xs text-gray-400">Clinical Trials</p>
          </div>
          <div className="bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/30 rounded-xl p-4 text-center">
            <Beaker className="w-8 h-8 text-purple-400 mx-auto mb-2" />
            <p className="text-3xl font-bold text-white">{evidenceSummary.total_drugs}</p>
            <p className="text-xs text-gray-400">Drugs Analyzed</p>
          </div>
          <div className="bg-gradient-to-br from-cyan-500/10 to-transparent border border-cyan-500/30 rounded-xl p-4 text-center">
            <Target className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
            <p className="text-3xl font-bold text-white">{evidenceSummary.confidence_level || 0}%</p>
            <p className="text-xs text-gray-400">Confidence</p>
          </div>
        </div>
      )}

      {/* Research Summary */}
      {(data.research_summary || data.synthesis) && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-400" />
            Research Summary
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
              {(data.research_summary || data.synthesis || '').replace(/^```markdown\n?/, '').replace(/\n?```$/, '')}
            </ReactMarkdown>
          </div>
        </div>
      )}

      {/* Key Findings */}
      {data.key_findings && data.key_findings.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-yellow-400" />
            Key Findings ({data.key_findings.length})
          </h4>
          <div className="space-y-4">
            {data.key_findings.map((finding, idx) => (
              <div key={idx} className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <p className="text-white font-medium flex-1">{finding.finding}</p>
                  <span className={`px-2 py-1 rounded text-xs font-medium flex-shrink-0 ${
                    finding.confidence === 'High' ? 'bg-green-500/20 text-green-400' :
                    finding.confidence === 'Moderate' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-blue-500/20 text-blue-400'
                  }`}>
                    {finding.confidence}
                  </span>
                </div>
                {finding.supporting_evidence && finding.supporting_evidence.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-[#2a3f5f]">
                    <p className="text-xs text-gray-400 mb-2">Supporting Evidence:</p>
                    <ul className="space-y-1">
                      {finding.supporting_evidence.slice(0, 3).map((evidence, i) => (
                        <li key={i} className="text-xs text-gray-300 flex items-start gap-2">
                          <span className="text-gray-500">•</span> {evidence}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {finding.clinical_relevance && (
                  <p className="text-xs text-cyan-400 mt-2">Clinical Relevance: {finding.clinical_relevance}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Therapeutic Landscape */}
      {data.therapeutic_landscape && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-green-400" />
            Therapeutic Landscape
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.therapeutic_landscape.current_standard_of_care && (
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 col-span-full">
                <p className="text-xs text-gray-400 mb-1">Current Standard of Care</p>
                <p className="text-gray-200">{data.therapeutic_landscape.current_standard_of_care}</p>
              </div>
            )}
            {data.therapeutic_landscape.approved_therapies && data.therapeutic_landscape.approved_therapies.length > 0 && (
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-2 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3 text-green-400" /> Approved Therapies
                </p>
                <div className="flex flex-wrap gap-2">
                  {data.therapeutic_landscape.approved_therapies.map((therapy, i) => (
                    <span key={i} className="bg-green-500/20 text-green-400 border border-green-500/30 px-2 py-1 rounded text-xs">
                      {therapy}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.therapeutic_landscape.emerging_therapies && data.therapeutic_landscape.emerging_therapies.length > 0 && (
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-2 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3 text-blue-400" /> Emerging Therapies
                </p>
                <div className="flex flex-wrap gap-2">
                  {data.therapeutic_landscape.emerging_therapies.map((therapy, i) => (
                    <span key={i} className="bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-1 rounded text-xs">
                      {therapy}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.therapeutic_landscape.unmet_needs && data.therapeutic_landscape.unmet_needs.length > 0 && (
              <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 col-span-full">
                <p className="text-xs text-gray-400 mb-2 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3 text-yellow-400" /> Unmet Medical Needs
                </p>
                <div className="space-y-2">
                  {data.therapeutic_landscape.unmet_needs.map((need, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-yellow-400 rounded-full mt-1.5 flex-shrink-0"></div>
                      <p className="text-sm text-gray-300">{need}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Research Gaps */}
      {data.research_gaps && data.research_gaps.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-400" />
            Research Gaps
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#2a3f5f]">
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Gap</th>
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Priority</th>
                  <th className="text-left py-3 px-4 text-xs text-gray-400 font-medium">Potential Impact</th>
                </tr>
              </thead>
              <tbody>
                {data.research_gaps.map((gap, idx) => (
                  <tr key={idx} className="border-b border-[#2a3f5f]/50 hover:bg-[#1a2533]">
                    <td className="py-3 px-4 text-gray-200 text-sm">{gap.gap_description}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        gap.priority === 'High' ? 'bg-red-500/20 text-red-400' :
                        gap.priority === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-green-500/20 text-green-400'
                      }`}>
                        {gap.priority}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-300 text-sm">{gap.potential_impact || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div className="bg-gradient-to-br from-[#4ade80]/5 to-[#22d3ee]/5 border border-[#4ade80]/30 rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-400" />
            Recommendations
          </h4>
          <div className="space-y-4">
            {data.recommendations.map((rec, idx) => (
              <div key={idx} className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-gradient-to-br from-[#4ade80] to-[#22d3ee] rounded-full flex items-center justify-center flex-shrink-0 text-xs text-white font-bold">
                      {idx + 1}
                    </div>
                    <p className="text-white font-medium">{rec.recommendation}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium flex-shrink-0 ${
                    rec.strength === 'Strong' ? 'bg-green-500/20 text-green-400' :
                    rec.strength === 'Moderate' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-blue-500/20 text-blue-400'
                  }`}>
                    {rec.strength}
                  </span>
                </div>
                {rec.rationale && (
                  <p className="text-sm text-gray-400 mb-2 ml-9">{rec.rationale}</p>
                )}
                {rec.implementation_steps && rec.implementation_steps.length > 0 && (
                  <div className="ml-9 mt-3 pt-3 border-t border-[#2a3f5f]">
                    <p className="text-xs text-gray-400 mb-2">Implementation Steps:</p>
                    <ol className="list-decimal list-inside space-y-1">
                      {rec.implementation_steps.map((step, i) => (
                        <li key={i} className="text-xs text-gray-300">{step}</li>
                      ))}
                    </ol>
                  </div>
                )}
                {rec.timeline && (
                  <p className="text-xs text-cyan-400 mt-2 ml-9">Timeline: {rec.timeline}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Literature & Clinical Trials - Collapsible */}
      {data.papers && data.papers.length > 0 && (
        <details className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl overflow-hidden">
          <summary className="cursor-pointer p-4 text-white font-semibold hover:bg-[#1a2533] flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-400" />
            📚 Literature ({data.papers.length} papers) - Click to expand
          </summary>
          <div className="p-4 border-t border-[#2a3f5f] max-h-96 overflow-y-auto space-y-3">
            {data.papers.slice(0, 10).map((paper, i) => (
              <div key={i} className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-3">
                <p className="text-white font-medium text-sm mb-1">{paper.title}</p>
                {paper.authors && paper.authors.length > 0 && (
                  <p className="text-xs text-gray-500">{paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? ' et al.' : ''}</p>
                )}
                <div className="flex gap-2 mt-2">
                  {paper.journal && (
                    <span className="bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded text-xs">
                      {paper.journal}
                    </span>
                  )}
                  {paper.publication_date && (
                    <span className="bg-gray-500/20 text-gray-400 border border-gray-500/30 px-2 py-0.5 rounded text-xs">
                      {paper.publication_date}
                    </span>
                  )}
                  {paper.pmid && (
                    <a href={`https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}/`} target="_blank" rel="noopener noreferrer" 
                       className="text-cyan-400 text-xs hover:underline">
                      PMID: {paper.pmid}
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </details>
      )}

      {/* Clinical Trials */}
      {data.trials && data.trials.length > 0 && (
        <details className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl overflow-hidden">
          <summary className="cursor-pointer p-4 text-white font-semibold hover:bg-[#1a2533] flex items-center gap-2">
            <Activity className="w-5 h-5 text-green-400" />
            🏥 Clinical Trials ({data.trials.length} trials) - Click to expand
          </summary>
          <div className="p-4 border-t border-[#2a3f5f] overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#2a3f5f]">
                  <th className="text-left py-2 px-3 text-xs text-gray-400 font-medium">Title</th>
                  <th className="text-left py-2 px-3 text-xs text-gray-400 font-medium">NCT ID</th>
                  <th className="text-left py-2 px-3 text-xs text-gray-400 font-medium">Status</th>
                  <th className="text-left py-2 px-3 text-xs text-gray-400 font-medium">Phase</th>
                </tr>
              </thead>
              <tbody>
                {data.trials.slice(0, 10).map((trial, idx) => (
                  <tr key={idx} className="border-b border-[#2a3f5f]/50 hover:bg-[#1a2533]">
                    <td className="py-2 px-3 text-gray-200 text-sm">{trial.title?.substring(0, 60)}{trial.title && trial.title.length > 60 ? '...' : ''}</td>
                    <td className="py-2 px-3 text-cyan-400 font-mono text-sm">{trial.nct_id || 'N/A'}</td>
                    <td className="py-2 px-3">
                      <span className={`px-2 py-0.5 rounded text-xs ${
                        trial.status === 'Completed' ? 'bg-green-500/20 text-green-400' :
                        trial.status === 'Recruiting' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {trial.status || 'N/A'}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-gray-300 text-sm">{trial.phase || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      )}

      {/* Quality Assessment */}
      {data.critique && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-purple-400" />
            Quality Assessment
          </h4>
          {data.critique.overall_quality && (
            <div className="mb-4">
              <span className={`px-3 py-1 rounded-lg text-sm font-medium ${
                data.critique.overall_quality === 'High' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                data.critique.overall_quality === 'Moderate' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
                'bg-blue-500/20 text-blue-400 border border-blue-500/30'
              }`}>
                Overall Quality: {data.critique.overall_quality}
              </span>
            </div>
          )}
          <div className="grid grid-cols-2 gap-4">
            {data.critique.strengths && data.critique.strengths.length > 0 && (
              <div>
                <p className="text-xs text-green-400 mb-2 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" /> Strengths
                </p>
                <div className="space-y-1">
                  {data.critique.strengths.map((s, i) => (
                    <p key={i} className="text-xs text-gray-300 flex items-start gap-2">
                      <span className="text-green-400">✓</span> {s}
                    </p>
                  ))}
                </div>
              </div>
            )}
            {data.critique.limitations && data.critique.limitations.length > 0 && (
              <div>
                <p className="text-xs text-yellow-400 mb-2 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" /> Limitations
                </p>
                <div className="space-y-1">
                  {data.critique.limitations.map((l, i) => (
                    <p key={i} className="text-xs text-gray-300 flex items-start gap-2">
                      <span className="text-yellow-400">!</span> {l}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
