import { Download, CheckCircle, AlertCircle, Loader2, FileText } from 'lucide-react';

// Types matching backend schema
export interface ClinicalTrialData {
  pipeline_summary: string;
  key_trials: string[];
  recent_updates: string[];
  strategic_insights: string;
}

interface ClinicalTrialViewProps {
  data: ClinicalTrialData | null;
  isLoading: boolean;
  error: string | null;
}

export function ClinicalTrialView({ data, isLoading, error }: ClinicalTrialViewProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 mx-auto mb-4 text-blue-400 animate-spin" />
          <p className="text-gray-400">Analyzing clinical trial pipeline...</p>
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
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-400" />
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
          <p>Submit a query to see clinical trial analysis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Download */}
      <div className="flex items-center justify-between">
        <h3 className="text-2xl">Clinical Trial Analysis Report</h3>
        <button className="flex items-center gap-2 bg-gradient-to-r from-[#4ade80] to-[#22d3ee] px-4 py-2 rounded-lg hover:from-[#22d3ee] hover:to-[#4ade80] transition-all shadow-lg">
          <Download className="w-4 h-4" />
          Export PDF
        </button>
      </div>

      {/* Pipeline Summary */}
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-blue-400" />
          Pipeline Summary
        </h4>
        <p className="text-gray-300 leading-relaxed">{data.pipeline_summary}</p>
      </div>

      {/* Key Trials */}
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-blue-400" />
          Key Clinical Trials
        </h4>
        <div className="space-y-3">
          {data.key_trials && data.key_trials.length > 0 ? (
            data.key_trials.map((trial, idx) => (
              <div key={idx} className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 hover:border-blue-400/50 transition-all">
                <p className="text-sm text-gray-300">{trial}</p>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-400">No key trials found</p>
          )}
        </div>
      </div>

      {/* Recent Updates */}
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-green-400" />
          Recent Updates & Milestones
        </h4>
        <div className="space-y-3">
          {data.recent_updates && data.recent_updates.length > 0 ? (
            data.recent_updates.map((update, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-sm text-gray-300 flex-1">{update}</p>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-400">No recent updates available</p>
          )}
        </div>
      </div>

      {/* Strategic Insights */}
      <div className="bg-gradient-to-br from-[#4ade80]/5 to-[#22d3ee]/5 border border-[#4ade80]/30 rounded-xl p-6 shadow-lg">
        <h4 className="mb-4 flex items-center gap-2">
          <span className="w-5 h-5 bg-gradient-to-br from-[#4ade80] to-[#22d3ee] rounded-full"></span>
          Strategic Insights & Recommendations
        </h4>
        <p className="text-gray-300 leading-relaxed">{data.strategic_insights}</p>
      </div>
    </div>
  );
}
