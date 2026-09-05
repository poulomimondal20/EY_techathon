import { Download, TrendingUp, AlertTriangle, Target, Award, Loader2 } from 'lucide-react';

// Types matching backend schema
export interface CompetitorProfile {
  name: string;
  market_share: string | null;
  revenue: string | null;
  active_trials: number | null;
  pipeline_drugs: number | null;
  key_products: string[];
  strengths: string[];
  weaknesses: string[];
}

export interface CompetitorAnalysisData {
  overview: string;
  market_size: string | null;
  market_growth_rate: string | null;
  total_competitors: number | null;
  competitors: CompetitorProfile[];
  pipeline_insights: string[];
  market_trends: string[];
  threats: string[];
  opportunities: string[];
  recommendations: string[];
}

interface CompetitorAnalysisViewProps {
  data: CompetitorAnalysisData | null;
  isLoading: boolean;
  error: string | null;
}

export function CompetitorAnalysisView({ data, isLoading, error }: CompetitorAnalysisViewProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 mx-auto mb-4 text-red-400 animate-spin" />
          <p className="text-gray-400">Analyzing competitive landscape...</p>
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
          <p className="text-gray-400">Error fetching analysis</p>
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
          <Target className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>Submit a query to see competitive analysis</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-2xl">Competitive Intelligence Report</h3>
        <button className="flex items-center gap-2 bg-gradient-to-r from-[#4ade80] to-[#22d3ee] px-4 py-2 rounded-lg hover:from-[#22d3ee] hover:to-[#4ade80] transition-all shadow-lg">
          <Download className="w-4 h-4" />
          Export PDF
        </button>
      </div>

      {/* Executive Summary */}
      <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
        <h4 className="mb-4">Market Overview</h4>
        <p className="text-gray-300 leading-relaxed mb-4">{data.overview}</p>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 text-center">
            <p className="text-2xl text-green-400 mb-1">{data.market_size || 'N/A'}</p>
            <p className="text-xs text-gray-400">Market Size</p>
          </div>
          <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 text-center">
            <p className="text-2xl text-green-400 mb-1">{data.market_growth_rate || 'N/A'}</p>
            <p className="text-xs text-gray-400">Growth Rate</p>
          </div>
          <div className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-4 text-center">
            <p className="text-2xl text-green-400 mb-1">{data.total_competitors || 'N/A'}</p>
            <p className="text-xs text-gray-400">Major Competitors</p>
          </div>
        </div>
      </div>

      {/* Competitor Details */}
      {data.competitors.map((competitor, idx) => (
        <div key={idx} className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h4 className="text-xl mb-2">{competitor.name}</h4>
              <div className="flex items-center gap-4 text-sm text-gray-400">
                <span>Market Share: <span className="text-green-400">{competitor.market_share}</span></span>
                <span>•</span>
                <span>Revenue: <span className="text-green-400">{competitor.revenue}</span></span>
              </div>
            </div>
            <div className="flex gap-6">
              <div className="text-center">
                <p className="text-2xl text-blue-400">{competitor.active_trials}</p>
                <p className="text-xs text-gray-400">Active Trials</p>
              </div>
              <div className="text-center">
                <p className="text-2xl text-purple-400">{competitor.pipeline_drugs}</p>
                <p className="text-xs text-gray-400">Pipeline Drugs</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            {/* Strengths */}
            <div>
              <h5 className="mb-3 flex items-center gap-2 text-sm">
                <Award className="w-4 h-4 text-green-400" />
                Key Strengths
              </h5>
              <div className="space-y-2">
                {competitor.strengths.map((strength, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-green-400 rounded-full mt-1.5 flex-shrink-0"></div>
                    <p className="text-xs text-gray-300">{strength}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Weaknesses */}
            <div>
              <h5 className="mb-3 flex items-center gap-2 text-sm">
                <AlertTriangle className="w-4 h-4 text-orange-400" />
                Key Weaknesses
              </h5>
              <div className="space-y-2">
                {competitor.weaknesses.map((weakness, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-orange-400 rounded-full mt-1.5 flex-shrink-0"></div>
                    <p className="text-xs text-gray-300">{weakness}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Key Products */}
          <div className="mt-4 pt-4 border-t border-[#2a3f5f]">
            <p className="text-xs text-gray-400 mb-2">Key Products:</p>
            <div className="flex flex-wrap gap-2">
              {competitor.key_products.map((product, i) => (
                <span key={i} className="bg-[#1a2533] border border-[#2a3f5f] px-3 py-1 rounded-full text-xs">
                  {product}
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}

      {/* Pipeline Insights */}
      {data.pipeline_insights.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-400" />
            Pipeline Insights
          </h4>
          <div className="space-y-2">
            {data.pipeline_insights.map((insight, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <div className="w-2 h-2 bg-purple-400 rounded-full mt-1.5 flex-shrink-0"></div>
                <p className="text-sm text-gray-300">{insight}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Market Trends */}
      {data.market_trends.length > 0 && (
        <div className="bg-gradient-to-br from-[#0f1722] to-[#1a2533] border border-[#2a3f5f] rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            Market Trends
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {data.market_trends.map((trend, idx) => (
              <div key={idx} className="bg-[#1a2533] border border-[#2a3f5f] rounded-lg p-3">
                <p className="text-xs text-gray-300">{trend}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Threats & Opportunities */}
      <div className="grid grid-cols-2 gap-6">
        {data.threats.length > 0 && (
          <div className="bg-gradient-to-br from-red-400/5 to-transparent border border-red-400/30 rounded-xl p-6 shadow-lg">
            <h4 className="mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              Key Threats
            </h4>
            <div className="space-y-2">
              {data.threats.map((threat, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-red-400 rounded-full mt-1.5 flex-shrink-0"></div>
                  <p className="text-xs text-gray-300">{threat}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {data.opportunities.length > 0 && (
          <div className="bg-gradient-to-br from-green-400/5 to-transparent border border-green-400/30 rounded-xl p-6 shadow-lg">
            <h4 className="mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-green-400" />
              Opportunities
            </h4>
            <div className="space-y-2">
              {data.opportunities.map((opportunity, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-green-400 rounded-full mt-1.5 flex-shrink-0"></div>
                  <p className="text-xs text-gray-300">{opportunity}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Strategic Recommendations */}
      {data.recommendations.length > 0 && (
        <div className="bg-gradient-to-br from-[#4ade80]/5 to-[#22d3ee]/5 border border-[#4ade80]/30 rounded-xl p-6 shadow-lg">
          <h4 className="mb-4 flex items-center gap-2">
            <span className="w-5 h-5 bg-gradient-to-br from-[#4ade80] to-[#22d3ee] rounded-full"></span>
            Strategic Recommendations
          </h4>
          <div className="space-y-3">
            {data.recommendations.map((rec, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <div className="w-6 h-6 bg-gradient-to-br from-[#4ade80] to-[#22d3ee] rounded-full flex items-center justify-center flex-shrink-0 text-xs">
                  {idx + 1}
                </div>
                <p className="text-sm text-gray-300 flex-1">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
