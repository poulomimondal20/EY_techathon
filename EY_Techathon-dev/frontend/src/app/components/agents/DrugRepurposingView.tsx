import { Download, Pill, Target, FlaskConical, AlertTriangle, Lightbulb, BookOpen, Loader2, FileText, CheckCircle, TrendingUp } from 'lucide-react';

// Types matching backend schema
export interface DrugProfile {
  drug_name: string;
  smiles: string | null;
  original_indication: string | null;
  drug_class: string | null;
  mechanism_of_action: string | null;
}

export interface RepurposingCandidate {
  predicted_indication: string;
  confidence_score: number;
  evidence_strength: string;
  supporting_evidence: string[];
  similar_approved_drugs: string[];
}

export interface SimilarDrug {
  drug_name: string;
  current_indication: string;
  similarity_score: number;
  mechanism_of_action: string | null;
}

export interface DrugRepurposingData {
  summary: string;
  drug_profile: DrugProfile;
  repurposing_candidates: RepurposingCandidate[];
  similar_drugs: SimilarDrug[];
  clinical_considerations: string[];
  research_gaps: string[];
  recommendations: string[];
  data_sources: string[];
}

interface DrugRepurposingViewProps {
  data: DrugRepurposingData | null;
  isLoading: boolean;
  error: string | null;
}

// Helper function to get confidence color
function getConfidenceColor(score: number): string {
  if (score >= 0.7) return 'text-green-400';
  if (score >= 0.4) return 'text-yellow-400';
  return 'text-red-400';
}

// Helper function to get evidence badge color
function getEvidenceBadgeColor(strength: string): string {
  switch (strength.toLowerCase()) {
    case 'high':
      return 'bg-green-400/20 text-green-400 border-green-400/30';
    case 'medium':
      return 'bg-yellow-400/20 text-yellow-400 border-yellow-400/30';
    case 'low':
      return 'bg-red-400/20 text-red-400 border-red-400/30';
    default:
      return 'bg-gray-400/20 text-gray-400 border-gray-400/30';
  }
}

export function DrugRepurposingView({ data, isLoading, error }: DrugRepurposingViewProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 mx-auto mb-4 text-purple-400 animate-spin" />
          <p className="text-gray-400">Analyzing drug repurposing opportunities...</p>
          <p className="text-xs text-gray-500 mt-2">This may take a moment</p>
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
          <p className="text-gray-400">Analysis Failed</p>
          <p className="text-sm text-red-400 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  // No data state
  if (!data) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-gray-400">
          <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>Enter a drug name to analyze repurposing opportunities</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Download */}
      <div className="flex items-center justify-between">
        <h3 className="text-2xl">Drug Repurposing Analysis</h3>
        <button className="flex items-center gap-2 bg-gradient-to-r from-[#a855f7] to-[#6366f1] px-4 py-2 rounded-lg hover:from-[#6366f1] hover:to-[#a855f7] transition-all shadow-lg">
          <Download className="w-4 h-4" />
          Export PDF
        </button>
      </div>

      {/* Summary */}
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-purple-400" />
          Executive Summary
        </h4>
        <p className="text-gray-300 leading-relaxed">{data.summary}</p>
      </div>

      {/* Drug Profile */}
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <Pill className="w-5 h-5 text-purple-400" />
          Drug Profile
        </h4>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Drug Name</p>
            <p className="text-white font-medium">{data.drug_profile.drug_name}</p>
          </div>
          {data.drug_profile.drug_class && (
            <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Drug Class</p>
              <p className="text-white font-medium">{data.drug_profile.drug_class}</p>
            </div>
          )}
          {data.drug_profile.original_indication && (
            <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 col-span-2">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Original Indication</p>
              <p className="text-gray-300">{data.drug_profile.original_indication}</p>
            </div>
          )}
          {data.drug_profile.mechanism_of_action && (
            <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 col-span-2">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Mechanism of Action</p>
              <p className="text-gray-300">{data.drug_profile.mechanism_of_action}</p>
            </div>
          )}
          {data.drug_profile.smiles && (
            <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 col-span-2">
              <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">SMILES Structure</p>
              <p className="text-xs text-purple-400 font-mono break-all">{data.drug_profile.smiles}</p>
            </div>
          )}
        </div>
      </div>

      {/* Repurposing Candidates */}
      {data.repurposing_candidates && data.repurposing_candidates.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-green-400" />
            Repurposing Candidates
            <span className="ml-2 text-xs bg-purple-400/20 text-purple-400 px-2 py-0.5 rounded-full">
              {data.repurposing_candidates.length} found
            </span>
          </h4>
          <div className="space-y-4">
            {data.repurposing_candidates.map((candidate, idx) => (
              <div key={idx} className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-5 hover:border-purple-400/50 transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h5 className="text-white font-medium text-lg">{candidate.predicted_indication}</h5>
                    <div className="flex items-center gap-3 mt-2">
                      <span className={`text-sm ${getConfidenceColor(candidate.confidence_score)}`}>
                        <TrendingUp className="w-4 h-4 inline mr-1" />
                        {(candidate.confidence_score * 100).toFixed(0)}% Confidence
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full border ${getEvidenceBadgeColor(candidate.evidence_strength)}`}>
                        {candidate.evidence_strength} Evidence
                      </span>
                    </div>
                  </div>
                </div>
                
                {candidate.supporting_evidence && candidate.supporting_evidence.length > 0 && (
                  <div className="mt-4">
                    <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Supporting Evidence</p>
                    <ul className="space-y-2">
                      {candidate.supporting_evidence.map((evidence, eIdx) => (
                        <li key={eIdx} className="flex items-start gap-2">
                          <div className="w-1.5 h-1.5 bg-purple-400 rounded-full mt-2 flex-shrink-0"></div>
                          <span className="text-sm text-gray-300">{evidence}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {candidate.similar_approved_drugs && candidate.similar_approved_drugs.length > 0 && (
                  <div className="mt-4">
                    <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Similar Approved Drugs</p>
                    <div className="flex flex-wrap gap-2">
                      {candidate.similar_approved_drugs.map((drug, dIdx) => (
                        <span key={dIdx} className="text-xs bg-[#0f1722] text-gray-300 px-3 py-1 rounded-full border border-[#2a3f5f]">
                          {drug}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Similar Drugs */}
      {data.similar_drugs && data.similar_drugs.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-cyan-400" />
            Structurally Similar Drugs
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#2a3f5f]">
                  <th className="text-left text-xs text-gray-500 uppercase tracking-wider py-3 px-4">Drug Name</th>
                  <th className="text-left text-xs text-gray-500 uppercase tracking-wider py-3 px-4">Current Indication</th>
                  <th className="text-left text-xs text-gray-500 uppercase tracking-wider py-3 px-4">Similarity</th>
                </tr>
              </thead>
              <tbody>
                {data.similar_drugs.map((drug, idx) => (
                  <tr key={idx} className="border-b border-[#2a3f5f]/50 hover:bg-[#1a2533] transition-colors">
                    <td className="py-3 px-4 text-white font-medium">{drug.drug_name}</td>
                    <td className="py-3 px-4 text-gray-300 text-sm">{drug.current_indication}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 bg-[#2a3f5f] rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-purple-400 to-cyan-400 rounded-full"
                            style={{ width: `${drug.similarity_score * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-400">{(drug.similarity_score * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Clinical Considerations */}
      {data.clinical_considerations && data.clinical_considerations.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-400" />
            Clinical Considerations
          </h4>
          <div className="space-y-3">
            {data.clinical_considerations.map((consideration, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-sm text-gray-300">{consideration}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Research Gaps */}
      {data.research_gaps && data.research_gaps.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-orange-400" />
            Research Gaps
          </h4>
          <div className="space-y-3">
            {data.research_gaps.map((gap, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <div className="w-2 h-2 bg-orange-400 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-sm text-gray-300">{gap}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div className="bg-gradient-to-br from-[#a855f7]/5 to-[#6366f1]/5 border border-[#a855f7]/30 rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-purple-400" />
            Strategic Recommendations
          </h4>
          <div className="space-y-3">
            {data.recommendations.map((rec, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <span className="w-6 h-6 bg-purple-400/20 text-purple-400 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0">
                  {idx + 1}
                </span>
                <p className="text-gray-300">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Sources */}
      {data.data_sources && data.data_sources.length > 0 && (
        <div className="bg-[#0f1722] border border-[#2a3f5f]/50 rounded-xl p-4">
          <p className="text-xs text-gray-500 mb-2">Data Sources</p>
          <div className="flex flex-wrap gap-2">
            {data.data_sources.map((source, idx) => (
              <span key={idx} className="text-xs text-gray-400 bg-[#1a2533] px-2 py-1 rounded">
                {source}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
